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

from representation.parsers.music_parser import MusicParser
from representation.parsers.score_conversor import ScoreConversor

import os

def main():
    """
    Main function for extracting the viewpoints for examples
    """

    music = {}
    folder = r'D:\FEUP_1920\DISS\Dissertation\generation_system\data\database\music21\bach'
    if os.path.isdir(folder):
        for _, _, files in os.walk(folder):
            for filename in files:
                print(filename)
                music_parser = MusicParser(filename, ['data', 'database', 'music21', 'bach'])
                music_parser.parse(vertical=False)
                music[filename] = music_parser


    # name = 'bwv1.6.2.mxl'  # 'MicrotonsExample.mxl' #'VoiceExample.mxl' #'bwv1.6.2.mxl'
    # parser = MusicParser(name)
    # parser.parse(vertical=False)
    # parser.to_pickle('MicrotonsExample')

    # weights = {
    #     'pitch': 5,
    #     'dnote': 1,
    #     'accidental': 1,
    #     # 'pitch_class': 0.5,
    #     'rest': 1,
    #     'contour': 1,
    #     'intfib': 3,
    #     'thrbar': 0.1,
    #     # 'posinbar': 0.5,
    #     # 'beat_strength': 0.5,
    #     'dur_length': 5,
    #     # 'dur_type': 0.5
    # }

    # events = parser.get_part_events()[1] + parser.get_part_events()[2] + parser.get_part_events()[3]
    # sequenced_events_0 = oracle_and_generator(
    #     events, 20)

    # score = ScoreConversor()
    # score.parse_events(sequenced_events_0, True)
    # score.stream.show()


def oracle_and_generator(events, seq_len, weights=None, dim=-1):
    o_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=events, weights=weights)

    norm_features = gen_utils.normalize(o_features, -1, 1)

    dict_normalized = {}
    for i, event in enumerate(norm_features):
        dict_normalized[str(event)] = o_features[i]

    thresh = gen_utils.find_threshold(
        norm_features[:dim], weights=weighted_fit, dim=len(features_names), entropy=True)

    oracle = gen_utils.build_oracle(
        norm_features[:dim], flag='a', features=features_names,
        weights=weighted_fit, dim=len(features_names),
        dfunc='cosine', threshold=thresh[0][1])
    #gen_plot.start_draw(oracle).show()

    # oracle2 = VMO.oracle.build_oracle(
    #     norm_features[:dim], flag='a', feature=features_names,
    #     weights=weighted_fit, dim=len(features_names), 
    #     dfunc='cosine', threshold=thresh[0][1])
    # plot.start_draw(oracle2).show()

    sequence, end, k_trace = gen.generate(
        oracle, seq_len=seq_len, p=0.125, k=1, LRS=5)

    return [LinearEvent(from_list=o_features[state], features=features_names) for state in sequence]


if __name__ == "__main__":
    main()
