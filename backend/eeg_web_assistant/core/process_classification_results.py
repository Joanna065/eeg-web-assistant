from math import ceil, floor
from typing import Dict, List, Tuple

import numpy as np
import plotly.graph_objects as go

from eeg_web_assistant import settings


class ClassificationResults:
    def __init__(self,
                 raw_array: np.ndarray,
                 proba_mean: List[float],
                 proba_std: List[float],
                 segment_cuts: List[Tuple[int, int]],
                 ch_names: List[str], sfreq: float,
                 config=settings.PlotConfig()):
        assert len(proba_mean) == len(proba_std) == len(segment_cuts)
        assert raw_array.shape[0] == len(ch_names)

        self.raw_array = raw_array
        self.proba_mean = proba_mean
        self.proba_std = proba_std
        self.segment_cuts = segment_cuts
        self.ch_names = ch_names
        self.sfreq = sfreq
        self.config = config

    def process(self) -> List[Dict]:
        segment_amount = len(self.segment_cuts)

        classified_segments = []
        for nr in range(segment_amount):
            start, stop = self.segment_cuts[nr]
            segment = self._prepare_segment(nr=nr,
                                            prob=self.proba_mean[nr],
                                            std=self.proba_std[nr],
                                            start_x=start,
                                            stop_x=stop)

            # return segment
            classified_segments.append(segment)
        return classified_segments

    def _prepare_segment(self, nr: int, prob: float, std: float, start_x: int, stop_x: int) -> Dict:
        start_time = floor(start_x / self.sfreq)
        stop_time = ceil(stop_x / self.sfreq)

        segment = {
            'nr': nr,
            'prob': prob,
            'std': std,
            'start_time': start_time,
            'stop_time': stop_time
        }
        return segment

    def _get_plot_img(self, plot_array: np.ndarray, start_time: int):
        channel_amount, n_times = plot_array.shape
        step = 1. / channel_amount

        layout = go.Layout()

        x_axis = [(x / self.sfreq) + start_time for x in range(0, n_times + 1)]

        plot_traces = []
        for chan_nr in range(channel_amount):
            domain_start = chan_nr * step
            domain_stop = (chan_nr + 1) * step

            kwargs = dict(domain=[domain_start, domain_stop], showticklabels=False, zeroline=False,
                          showgrid=False)

            trace = go.Scattergl(x=x_axis, y=plot_array[chan_nr, :], yaxis=f'y{chan_nr + 1}')
            plot_traces.append(trace)

            layout.update({f'yaxis{chan_nr + 1}': kwargs, 'showlegend': False})

        # add channel names
        annotations = go.Annotations(
            [go.layout.Annotation(
                x=-0.105, y=0, xref='paper', yref=f'y{ii + 1}',
                text=ch_name, font=go.layout.annotation.Font(size=self.config.FONT_SIZE),
                showarrow=False
            ) for ii, ch_name in enumerate(self.ch_names)])

        layout.update(annotations=annotations)
        layout.update(autosize=False, width=self.config.WIDTH, height=self.config.HEIGHT)

        left_m, right_m, top_m, bottom_m = self.config.PADDINGS_LRTB
        fig = go.Figure(data=plot_traces, layout=layout)
        fig.update_layout(margin=dict(l=left_m, r=right_m, t=top_m, b=bottom_m))

        img_bytes = fig.to_image(format=self.config.IMG_FORMAT, engine="kaleido",
                                 width=self.config.WIDTH, height=self.config.HEIGHT)

        return img_bytes
