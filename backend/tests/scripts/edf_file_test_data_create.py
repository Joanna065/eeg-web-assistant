import json
from typing import List

import numpy as np
import pandas as pd
from scipy.integrate import simps
from scipy.stats import kurtosis, skew
from yasa import bandpower

from eeg_web_assistant import settings


def generate_array(channels: int, n_times: int, min_val: float, max_val: float) -> np.ndarray:
    return np.random.uniform(low=min_val, high=max_val, size=(channels, n_times))


def normalize(array: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    return (array - ((max_val + min_val) / 2)) / ((max_val - min_val) / 2)


def gen_split_segments_test_data(channels: int, segment_len: int = 16, segment_amount: int = 3,
                                 sfreq: int = 10):
    n_times = segment_amount * segment_len * sfreq
    array = np.random.randint(0, 10, size=(channels, n_times))
    step = segment_len * sfreq

    segments = [array[:, t:(t + step)] for t in range(0, array.shape[1] - step + 1, step)]
    segment_cuts = [t for t in range(0, array.shape[1] - step + 1, step)]

    output = np.array(segments)
    return array, output, segment_cuts, sfreq


def gen_split_frames_test_data(channels: int, segments: int = 3, segment_len: int = 16,
                               frame_amount: int = 8, sfreq: int = 10):
    n_times = segments * segment_len * sfreq
    array = np.random.randint(0, 10, size=(channels, n_times))
    step = segment_len * sfreq

    segments = [array[:, t:(t + step)] for t in range(0, array.shape[-1] - step + 1, step)]

    frame_step = int((segment_len / frame_amount) * sfreq)
    frames_list = []
    for segment in segments:
        frames = [segment[:, t:t + frame_step] for t in
                  range(0, segment.shape[-1] - frame_step + 1, frame_step)]
        frames_list.append(frames)

    output = np.array(frames_list)
    return np.array(segments), output, frame_amount, sfreq, segment_len


def gen_spearman_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)

    df = pd.DataFrame(data=array.T)
    spearman_corr = df.corr(method='spearman').to_numpy()

    return array, spearman_corr


def gen_mean_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)
    output = np.mean(array, axis=1)

    return array, output


def gen_variance_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)
    output = np.var(array, axis=1, ddof=1)

    return array, output


def gen_skewness_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)
    output = skew(array, axis=1, bias=False, nan_policy='omit')

    return array, output


def gen_kurtosis_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)
    output = kurtosis(array, axis=1, bias=False)

    return array, output


def gen_zero_crossing_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)
    output = np.count_nonzero(np.diff(np.sign(array)), axis=1)

    return array, output


def gen_area_under_signal_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)
    output = simps(np.abs(array), dx=1e-6, axis=1)

    return array, output


def gen_peak2peak_test_data(channels: int, n_times: int, min_val: float, max_val: float):
    array = generate_array(channels, n_times, min_val, max_val)
    output = np.max(array, axis=1) - np.min(array, axis=1)

    return array, output


def gen_bandpower_test_data(channels: int, min_val: float, max_val: float, sfreq: int,
                            frame_len: int, bands: List[str]):
    n_times = frame_len * sfreq
    edf_array = generate_array(channels, n_times, min_val, max_val)

    df = bandpower(edf_array, sf=sfreq, win_sec=frame_len)
    df = df.loc[:, bands]
    output = df.to_numpy()

    return edf_array, output, sfreq, bands


if __name__ == '__main__':
    array_tuples = []
    for i in range(0, 5):
        MIN_VAL = -1.5
        MAX_VAL = 1.7
        array = generate_array(channels=4, n_times=20, min_val=MIN_VAL, max_val=MAX_VAL)
        result_array = normalize(array, min_val=MIN_VAL, max_val=MAX_VAL)
        array_tuples.append(
            {'min_val': MIN_VAL, 'max_val': MAX_VAL, 'input': array.tolist(),
             'expected_output': result_array.tolist()})

    test_dict = {'normalize': array_tuples}

    DATA_DIR = settings.TestConfig.FIXTURE_DIR.joinpath('edf_processing')

    with DATA_DIR.joinpath('test_normalize_array.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        SEGMENT_LEN = 16
        array, output, segment_cuts, sfreq = gen_split_segments_test_data(channels=4,
                                                                          segment_amount=3,
                                                                          segment_len=SEGMENT_LEN,
                                                                          sfreq=10)
        test_arrays.append(
            {'input': array.tolist(),
             'expected_output': output.tolist(),
             'segment_cuts': segment_cuts,
             'segment_len': SEGMENT_LEN,
             'sfreq': sfreq})

    test_dict = {'split_segments': test_arrays}

    with DATA_DIR.joinpath('test_split_segments.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, frame_amount, sfreq, segment_len = gen_split_frames_test_data(
            channels=4, segments=3, segment_len=16, sfreq=10, frame_amount=8)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist(),
             'frame_amount': frame_amount,
             'segment_len': segment_len,
             'sfreq': sfreq})

    test_dict = {'split_frames': test_arrays}

    with DATA_DIR.joinpath('test_split_frames.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, = gen_spearman_test_data(channels=3, n_times=5, min_val=-1.5,
                                                            max_val=2.3)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist()})

    test_dict = {'spearman_corr': test_arrays}

    with DATA_DIR.joinpath('test_spearman_corr.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, = gen_mean_test_data(channels=3, n_times=5, min_val=-1.5,
                                                        max_val=2.3)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist()})

    test_dict = {'mean': test_arrays}

    with DATA_DIR.joinpath('test_mean.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, = gen_variance_test_data(channels=3, n_times=5, min_val=-1.5,
                                                            max_val=2.3)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist()})

    test_dict = {'variance': test_arrays}

    with DATA_DIR.joinpath('test_variance.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, = gen_skewness_test_data(channels=3, n_times=5, min_val=-1.5,
                                                            max_val=2.3)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist()})

    test_dict = {'skewness': test_arrays}

    with DATA_DIR.joinpath('test_skewness.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, = gen_kurtosis_test_data(channels=3, n_times=5, min_val=-1.5,
                                                            max_val=2.3)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist()})

    test_dict = {'kurtosis': test_arrays}

    with DATA_DIR.joinpath('test_kurtosis.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, = gen_zero_crossing_test_data(channels=3, n_times=5,
                                                                 min_val=-1.5, max_val=2.3)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist()})

    test_dict = {'zero_crossing': test_arrays}

    with DATA_DIR.joinpath('test_zero_crossing.json').open(mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, = gen_area_under_signal_test_data(channels=3, n_times=5,
                                                                     min_val=-1.5, max_val=2.3)
        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist()})

    test_dict = {'absolute_area_under_signal': test_arrays}

    with DATA_DIR.joinpath('test_absolute_area_under_signal.json').open(
            mode='w') as f:
        json.dump(test_dict, f)

    test_arrays = []
    for i in range(0, 5):
        input_array, output_array, sfreq, bands = gen_bandpower_test_data(channels=3, sfreq=64,
                                                                          frame_len=2,
                                                                          min_val=-1.5, max_val=3.1,
                                                                          bands=['Delta', 'Theta',
                                                                                 'Alpha', 'Beta'])

        test_arrays.append(
            {'input': input_array.tolist(),
             'expected_output': output_array.tolist(),
             'sfreq': sfreq,
             'bands': bands})

    test_dict = {'bandpower': test_arrays}

    with DATA_DIR.joinpath('test_bandpower.json').open(mode='w') as f:
        json.dump(test_dict, f)
