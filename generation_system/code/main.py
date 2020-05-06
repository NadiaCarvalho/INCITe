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
from representation.conversor.score_conversor import ScoreConversor

import os

# 'MicrotonsExample.mxl'
# 'VoiceExample.mxl'
# 'bwv1.6.2.mxl'
# 'to.mxl'
# 'bwv67.4.mxl'
# 'complexcompass.mxl'


def main():
    """
    Main function for extracting the viewpoints for examples
    """
    name = 'to.mxl'
    parser = MusicParser(name)
    parser.parse(parts=True, vertical=True)
    parser.to_pickle(name[:-4])

    new_parser = MusicParser()
    new_parser.from_pickle('to')

    weights = {
        'cpitch': 5,
        # 'dnote': 4,
        # 'accidental': 1,
        # 'pitch_class': 0.5,
        'rest': 1,
        'contour': 1,
        # 'intfib': 3,
        # 'thrbar': 0.1,
        # 'posinbar': 0.5,
        # 'beat_strength': 0.5,
        'duration.length': 5,
        'duration.type': 0.5,
        'timesig': 1,
        'fib': 0.1,
        # 'fermata': 0.5,
        'phrase.boundary': 0.5,
    }
    part_number = input('Choose a part from {}:  '.format(
        new_parser.get_part_events().keys()))

    if part_number.find('.') == -1 and part_number != '':
        part_number = int(part_number)

    if part_number in new_parser.get_part_events().keys():

        events = new_parser.get_part_events()[part_number][:100]

        score = ScoreConversor()
        score.parse_events(events, True)
        score.stream.show()

        norm_features,  o_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
            events=events, offset=False)
        
        columns_values = list(zip(*norm_features))
        statistic_dict = {}
        for i, feat in enumerate(features_names):
            if '=' in feat:
                info = feat.split('=')
                if not info[0] in statistic_dict:
                    statistic_dict[info[0]] = []

                values = list(zip(*np.unique(list(columns_values[i]), return_counts=True)))
                if len(values) == 1:
                    statistic_dict[info[0]].append((info[1], values[0][1]))
                else: 
                    ret = [item for item in values if item[0] == 1.0]
                    if len(ret) > 0:
                        statistic_dict[info[0]].append((info[1], ret[0][1]))
            else:
                statistic_dict[feat] = list(zip(*np.unique(list(columns_values[i]), return_counts=True)))
        for feat, value in statistic_dict.items():
           print(feat + ': ' + str(value))

        sequenced_events_0 = oracle_and_generator(
            events, 30)

        score = ScoreConversor()
        score.parse_events(sequenced_events_0, True)
        score.stream.show()
    else:
        print('Not a part of this piece!')


def oracle_and_generator(events, seq_len, weights=None, dim=-1):
    norm_features, o_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=events, weights=weights)

    thresh = gen_utils.find_threshold(
        norm_features[:dim], weights=weighted_fit, dim=len(features_names), entropy=True)

    oracle = gen_utils.build_oracle(
        norm_features[:dim], flag='a', features=features_names,
        weights=weighted_fit, dim=len(features_names),
        dfunc='cosine', threshold=thresh[0][1])
    gen_plot.start_draw(oracle).show()

    sequence, end, k_trace = gen.generate(
        oracle, seq_len=seq_len, p=0.3, k=1, LRS=5)

    return [LinearEvent(from_list=o_features[state], features=features_names) for state in sequence]


def parsing_music_folder(folder, json=False, pickle=True):
    """
    Parsing a music folder to json/pickle format and return parsed music
    """
    music = {}
    if os.path.isdir(folder):
        for root, _, files in os.walk(folder):
            dirs_to_save = root.split(os.sep)[-4:]
            dirs_to_save[2] = 'parsed'

            for filename in files:
                if '.mxl' in filename:
                    music_parser = MusicParser(
                        filename, root.split(os.sep)[-4:])
                    music_parser.parse()

                    name = '.'.join(filename.split('.')[:-1])
                    music[name] = music_parser

                    if json:
                        music_parser.to_json(name, dirs_to_save)
                    if pickle:
                        music_parser.to_pickle(name, dirs_to_save)

    return music


def recover_parsed_folder(folder, pickle=True):
    """
    Recover parsed music in folder
    If pickle == True: recover '.pbz2' files (default)
    If pickle == False: recover '.json' files (default)
    """
    music = {}
    if os.path.isdir(folder):
        for root, _, files in os.walk(folder):
            for filename in files:
                name = '.'.join(filename.split('.')[:-1])
                if pickle and '.pbz2' in filename:
                    music_parser = MusicParser()
                    music_parser.from_pickle(name, root.split(os.sep)[-4:])
                    music[name] = music_parser
                elif '.json' in filename:
                    music_parser = MusicParser()
                    music_parser.from_json(name, root.split(os.sep)[-4:])
                    music[name] = music_parser
    return music


if __name__ == "__main__":
    main()
    # parsing_music_folder(r'D:\FEUP_1920\DISS\Dissertation\generation_system\data\database\music21\bach')
    # recover_parsed_folder(r'D:\FEUP_1920\DISS\Dissertation\generation_system\data\database\parsed\bach')
