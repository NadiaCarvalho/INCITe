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

from representation.parsers.segmentation import segmentation, apply_segmentation_info, get_phrases_from_events
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
    # name = 'bwv67.4.mxl'
    # parser = MusicParser(name)
    # parser.parse(parts=True, vertical=True)
    # parser.to_pickle(name[:-4])

    parser = MusicParser()
    parser.from_pickle('bwv67.4')

    weights = {
        # 'basic.rest': 1,
        # 'basic.grace': 1,
        # 'basic.chord': 1,
        # 'duration.length': 1,
        # 'duration.type': 1,
        # 'pitch.cpitch': 1,
        # 'pitch.dnote': 1,
        # 'pitch.chordPitches': 1,
        # 'time.timesig': 1,
        # 'metro.value': 1,
        'fermata': 1,

        # 'derived.seq_int': 1,
        # 'derived.contour': 1,
        # 'derived.contour_hd': 1,
        # 'derived.closure': 1,
        # 'derived.registral_direction': 1,
        # 'derived.intervallic_difference': 1,
        # 'derived.upwards': 1,
        # 'derived.downwards': 1,
        # 'derived.no_movement': 1,
        # 'derived.fib': 1,
        # 'derived.posinbar': 1,
        # 'derived.beat_strength': 1,
        # 'derived.tactus': 1,
        # 'derived.intfib': 1,
        # 'derived.thrbar': 1,
    }

    vertical_start_indexes = {}
    original_features = {}
    oracles = {}

    vertical_offsets = [ev.get_offset() for ev in parser.get_vertical_events()]

    last_offset = 0
    for key, events in parser.get_part_events().items():
        if len(events) > 1:
            oracle, vs_ind, o_features, last_off = create_line_oracle(parser, events, weights, vertical_offsets=None, phrase=0)
            oracles[key] = oracle
            original_features[key] = o_features
            vertical_start_indexes[key] = vs_ind
            if last_off > last_offset:
                last_offset = last_off

    vert_oracle = create_vertical_oracle(parser, dim2=vertical_offsets.index(last_offset))
    oracles['vertical'] = vert_oracle

    for key, oracle in oracles.items():
        image = gen_plot.start_draw(oracle)
        name = r'data\myexamples\oracle of part '+ str(key) + '.PNG'
        image.save(name)
        

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
        oracle, seq_len=seq_len, p=0.3, k=-1, LRS=5)

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


def create_music(parser):
    first = True
    for part_number in ['1.0', '1.1']:
        events = parser.get_part_events()[part_number]
        segmentation(events)
        apply_segmentation_info(events)

        events_to_learn = []
        for phrase in get_phrases_from_events(events):
            events_to_learn.extend(phrase)

        sequenced_events = oracle_and_generator(
            events_to_learn, 100)
        if len(sequenced_events) > 0:
            score.parse_events(sequenced_events, first)
            first = False

    score.stream.show('text')


def view_specific_part(parser):
    part_number = input('Choose a part from {}:  '.format(
        list(parser.get_part_events())))

    if part_number.find('.') == -1 and part_number != '':
        part_number = int(part_number)

    if part_number in parser.get_part_events().keys():

        events = parser.get_part_events()[part_number]
        segmentation(events)
        apply_segmentation_info(events)

        # rep_utils.statistic_features(events)

        events_to_learn = []
        for phrase in get_phrases_from_events(events):
            events_to_learn.extend(phrase)

        sequenced_events_0 = oracle_and_generator(
            events_to_learn, 100)

        score = ScoreConversor()
        score.parse_events(sequenced_events_0, True)
        score.stream.show()
    else:
        print('Not a part of this piece!')


def create_vertical_oracle(parser, dim1=0, dim2=None):
    """
    Create the vertical oracle
    """
    norm_features, o_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=parser.get_vertical_events())
    thresh = gen_utils.find_threshold(
        norm_features[dim1:dim2], weights=weighted_fit, dim=len(features_names), entropy=True)

    if dim2 is None:
        dim2 = len(norm_features)

    oracle = gen_utils.build_oracle(
        norm_features[dim1:dim2], flag='a', features=features_names,
        weights=weighted_fit, dim=len(features_names),
        dfunc='cosine', threshold=thresh[0][1])
    return oracle


def create_line_oracle(parser, events, weights=None, dim1=0, dim2=None, vertical_offsets=None, phrase=None):
    """
    Create oracle for line part
    """

    vertical_start_indexes = []
    if vertical_offsets is not None:
        ev_offsets = [ev.get_offset() for ev in events]
        vertical_start_indexes = [vertical_offsets.index(off) for off in ev_offsets]
        segmentation(events, weights_line=weights, vertical_events=parser.get_vertical_events(), indexes=vertical_start_indexes)
    else:
        segmentation(events, weights_line=weights)

    apply_segmentation_info(events)
    
    new_events = events
    if phrase is not None and phrase < len(get_phrases_from_events(events)):
        new_events = get_phrases_from_events(events)[phrase]
    
    last_offset = new_events[-1].get_offset()

    if dim2 is None:
        dim2 = len(new_events)

    norm_features, o_features, features_names, weighted_fit = rep_utils.create_feature_array_events(events=new_events)
    thresh = gen_utils.find_threshold(
        norm_features[dim1:dim2], weights=weighted_fit, dim=len(features_names), entropy=True)
    oracle = gen_utils.build_oracle(
        norm_features[dim1:dim2], flag='a', features=features_names,
        weights=weighted_fit, dim=len(features_names),
        dfunc='cosine', threshold=thresh[0][1])
    
    return oracle, vertical_start_indexes, o_features, last_offset



if __name__ == "__main__":
    main()
    # parsing_music_folder(r'D:\FEUP_1920\DISS\Dissertation\generation_system\data\database\music21\bach')
    # recover_parsed_folder(r'D:\FEUP_1920\DISS\Dissertation\generation_system\data\database\parsed\bach')
