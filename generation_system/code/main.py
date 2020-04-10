#!/usr/bin/env python3.7
"""
This script is the main script of the generation system
"""

import numpy as np
from vmo import VMO, plot

import generation.plot_fo as gen_plot
import generation.utils as gen_utils

from representation.parser import Parser


def main():
    """
    Main function for extracting the viewpoints for examples
    """
    name = 'VoiceExample.mxl'  # 'MicrotonsExample.mxl' #'VoiceExample.mxl' #'bwv1.6.2.mxl'
    parser = Parser(name)
    parser.parse()
    parser.show_events(events='some parts', parts=[0], viewpoints=['midi_pitch', 'posinbar'])

    weights = {
        'midi_pitch': 0.5,
        'pitch_class': 0.5,
        'contour': 0.5,
        'intfib': 0.5,
        'thrbar': 0.5,
        'posinbar': 0.5,
        'beatstrength': 0.5,
        'duration_length': 0.5,
        'duration_type': 0.5
    }

    """     
    event_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=part_events[0], weights=weights)

    thresh = gen_utils.find_threshold(
        event_features[:15], weights=weighted_fit, dim=len(features_names), entropy=True)

    oracle = gen_utils.build_oracle(
        event_features[:15], flag='a', features=features_names, weights=weighted_fit, dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])
    gen_plot.start_draw(oracle).show()

    oracle2 = VMO.oracle.build_oracle(
        event_features[:15], flag='a', dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])
    plot.start_draw(oracle2).show()
    """


if __name__ == "__main__":
    main()
