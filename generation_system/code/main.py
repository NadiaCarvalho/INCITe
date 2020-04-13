#!/usr/bin/env python3.7
"""
This script is the main script of the generation system
"""

import numpy as np
from vmo import VMO, plot

import generation.generation as gen
import generation.plot_fo as gen_plot
import generation.utils as gen_utils
import representation.utils as rep_utils

from representation.events.linear_event import LinearEvent

from representation.parsers.parser import Parser
from representation.parsers.score_conversor import ScoreConversor


def main():
    """
    Main function for extracting the viewpoints for examples
    """
    name = 'MicrotonsExample.mxl'  # 'MicrotonsExample.mxl' #'VoiceExample.mxl' #'bwv1.6.2.mxl'
    parser = Parser(name)
    parser.parse(vertical=False)
    #parser.show_events(events='one part', parts=0, viewpoints=['accidental'])
    #parser.show_events(events='all parts', viewpoints='all')

    weights = {
        'pitch': 0.5,
        'dnote': 0.5,
        'accidental': 0.5,
        # 'pitch_class': 0.5,
        'rest': 0.5,
        'contour': 0.5,
        # 'intfib': 0.5,
        # 'thrbar': 0.5,
        # 'posinbar': 0.5,
        # 'beat_strength': 0.5,
        'dur_length': 0.5,
        # 'dur_type': 0.5
    }

    sequenced_events_0 = oracle_and_generator(
        parser.get_part_events()[0], weights, 50)

    score = ScoreConversor()
    score.parse_events(sequenced_events_0, True)
    score.stream.show()

    """
    oracle2 = VMO.oracle.build_oracle(
        event_features[:15], flag='a', dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])
    plot.start_draw(oracle2).show()
    """


def oracle_and_generator(events, weights, seq_len, dim=-1):
    event_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=events, weights=weights)

    thresh = gen_utils.find_threshold(
        event_features[:dim], weights=weighted_fit, dim=len(features_names), entropy=True)

    oracle = gen_utils.build_oracle(
        event_features[:dim], flag='a', features=features_names,
        weights=weighted_fit, dim=len(features_names),
        dfunc='cosine', threshold=thresh[0][1])
    # gen_plot.start_draw(oracle).show()

    sequence, end, k_trace = gen.generate(oracle, seq_len=seq_len)
    return [LinearEvent(from_list=oracle.f_array[state], features=features_names) for state in sequence]


if __name__ == "__main__":
    main()
