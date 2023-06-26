import json
from copy import deepcopy
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import mne
import numpy as np

from eeg_web_assistant import settings
from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.services.logging import Logging

logger = Logging.get(__name__)


class EdfFile:
    def __init__(self, path: Path, config=settings.EdfFileConfig):
        self.path = path
        self.config = config
        self.raw = None
        self.exclude_channels = None
        self._load()

    @property
    def duration(self) -> int:
        return ceil(self.raw.n_times // self.raw.info['sfreq'])

    @property
    def channel_names(self) -> List[str]:
        return self.raw.ch_names

    @property
    def lowpass(self) -> Optional[float]:
        return self.raw.info.get('lowpass')

    @property
    def highpass(self) -> Optional[float]:
        return self.raw.info.get('highpass')

    @property
    def sampling_frequency(self) -> float:
        return self.raw.info['sfreq']

    @property
    def measure_date(self) -> Optional[datetime]:
        return self.raw.info.get('meas_date')

    @property
    def subject_info(self) -> Optional[Dict]:
        subject_info = self.raw.info.get('subject_info')
        if subject_info:
            birthday: Tuple[int, int, int] = subject_info.get('birthday')
            if birthday:
                subject_info['birthday'] = datetime(*birthday)

        return subject_info

    @property
    def n_times(self) -> int:
        return self.raw.n_times

    @property
    def min_max_value(self) -> Tuple[float, float]:
        array = self.to_numpy()
        return np.amin(array), np.amax(array)

    def drop_channels(self, drop_names: Iterable[str]):
        logger.debug("Dropping channels: %s", ",".join(drop_names))

        self.raw.drop_channels(ch_names=drop_names)

    def change_duration(self, new_duration: int):
        if new_duration <= 0:
            raise ValueError("New duration value must be greater than 0 seconds")

        logger.debug("Changing edf duration from %d to %d", self.duration, new_duration)
        self.raw.crop(tmin=0, tmax=new_duration, include_tmax=False)

        assert self.raw.n_times / self.raw.info['sfreq'] == new_duration

    def resample(self, new_sfreq: float):
        logger.debug("Resampling data from sfreq %.1f to %.1f", self.sampling_frequency, new_sfreq)

        self.raw = self.raw.resample(sfreq=new_sfreq)

    def to_numpy(self) -> np.ndarray:
        return self.raw.get_data()

    def _load(self):
        self._load_config()

        self.raw = mne.io.read_raw_edf(str(self.path))
        self.raw.close()
        logger.info("Edf file read")

        if self.exclude_channels is not None:
            logger.debug("Excluding non EEG channel types...")
            ch_names = self.raw.ch_names
            drop_chan = set(self.exclude_channels).intersection(ch_names)

            self.drop_channels(drop_names=drop_chan)

    def _load_config(self):
        logger.debug("Loading config for EDF file read...")

        with self.config.EDF_FILE_EXCLUDE.open(mode='r') as f:
            self.exclude_channels = json.load(f).get('exclude')


class EdfProcessor:
    def __init__(self, edf_record: EdfFile, classification_type: ClassificationType,
                 config=settings.EdfProcessingConfig):
        self.edf_record = deepcopy(edf_record)
        self.classification_type = classification_type
        self.config = config
        self.segment_cuts = None
        self.common_channels = None
        self.processed_data = None

    def process(self) -> np.ndarray:
        logger.info("Begin processing EDF record for classification...")

        self._load_config()
        self._modify_for_classification()
        array = self._split_to_segments()
        array = self._normalize(array)
        array = self._split_to_frames(segmented_array=array)

        return array

    def _load_config(self):
        with self.config.EDF_CHANNELS_SETUP.open(mode='r') as f:
            edf_setup = json.load(f)

        self.common_channels = edf_setup[self.classification_type.value]
        self.frames_amount = self.config.TIMEFRAMES_AMOUNT
        self.segment_len = self.config.SEGMENT_LEN_SECONDS

        if self.segment_len % self.frames_amount == 0:
            self.frame_len = int(self.segment_len / self.frames_amount)
        else:
            raise ValueError("Wrong segment and frames config.")

    def _modify_for_classification(self):
        drop_chan = set(self.edf_record.channel_names).difference(self.common_channels)
        self.edf_record.drop_channels(drop_names=drop_chan)

        self._check_edf_duration()

    def _check_edf_duration(self):
        duration = self.edf_record.duration

        if duration < self.segment_len:
            raise ValueError(f"Cannot process EDF shorter than {self.segment_len} s duration.")

        if not duration % self.segment_len == 0:
            new_duration = int(duration / self.segment_len) * self.segment_len
            self.edf_record.change_duration(new_duration=new_duration)

    def _split_to_segments(self) -> np.ndarray:
        assert self.edf_record.duration % self.segment_len == 0

        array = self.edf_record.to_numpy()
        n_times = array.shape[-1]
        step = int(self.segment_len * self.edf_record.sampling_frequency)

        logger.debug("Splitting EDF record to segments...")

        self.segment_cuts = [(t, t + step) for t in range(0, n_times - step + 1, step)]
        segments = np.array([array[:, t:t + step] for t in range(0, n_times - step + 1, step)])

        logger.debug("Segmented data shape: %s", segments.shape)

        assert segments.shape[-1] == step

        return segments

    def _split_to_frames(self, segmented_array: np.ndarray) -> np.ndarray:
        logger.debug("Input segmented data shape: %s", segmented_array.shape)

        assert len(segmented_array.shape) == 3
        assert segmented_array.shape[-1] == self.segment_len * self.edf_record.sampling_frequency

        logger.debug("Splitting segmented EDF record to frames...")
        step = int(self.frame_len * self.edf_record.sampling_frequency)

        frames_list = []
        for segment in segmented_array:
            n_times = segment.shape[-1]
            frames = [segment[:, t:t + step] for t in range(0, n_times - step + 1, step)]
            frames_list.append(frames)

        frames = np.array(frames_list)

        logger.debug("Split into frames data shape: %s", frames.shape)

        return frames

    def _normalize(self, array: np.ndarray) -> np.ndarray:
        signal_min, signal_max = self.edf_record.min_max_value
        return (array - ((signal_max + signal_min) / 2)) / ((signal_max - signal_min) / 2)
