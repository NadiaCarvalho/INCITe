#!/usr/bin/env python3.7
"""
This script is the main script of the generation system
"""

import os
from representation.conversor.score_conversor import ScoreConversor
from representation.parsers.music_parser import MusicParser
from representation.parsers.segmentation import segmentation, apply_segmentation_info, get_phrases_from_events
from representation.events.linear_event import LinearEvent
import representation.utils as rep_utils
import generation.utils as gen_utils
import generation.plot_fo as gen_plot
import generation.generation as gen
import generation.multi_oracle_gen as multi_gen
import numpy as np

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
    # name = 'lg-199757.mxl'
    # parser = MusicParser(name, folders=['data','database','ScoresOfScores-master', '3-Corpus'])
    # parser.parse(parts=True, vertical=True)
    # parser.to_pickle(name[:-4])

    parser = MusicParser()
    parser.from_pickle('lg-199757')

    weights = {
        'line': {
            'basic.rest': 1,
            'basic.grace': 1,
            'basic.chord': 1,
            'duration.length': 1,
            'duration.type': 1,
            'pitch.cpitch': 1,
            'pitch.dnote': 1,
            'pitch.accidental': 1,
            'pitch.octave': 1,
            'pitch.chordPitches': 1,
            'time.timesig': 1,
            'metro.value': 1,
            'fermata': 1,

            'derived.seq_int': 1,
            'derived.contour': 1,
            'derived.contour_hd': 1,
            'derived.closure': 1,
            'derived.registral_direction': 1,
            'derived.intervallic_difference': 1,
            'derived.upwards': 1,
            'derived.downwards': 1,
            'derived.no_movement': 1,
            'derived.fib': 1,
            'derived.posinbar': 1,
            'derived.beat_strength': 1,
            'derived.tactus': 1,
            'derived.intfib': 1,
            'derived.thrbar': 1,
        },
        'vertical': {
            'basic.root': 1,
            'pitches': 1,
            'cardinality': 1,
            'quality': 1,
            'prime_form': 1,
            'inversion': 1,
            'pitch_class': 1,
            'forte_class': 1,
            'pc_ordered': 1,
            'keysig': 1,
            'signatures.function': 1,
            'measure.function': 1,
        }
    }
    # parts=[0,1,2],
    oracles, o_feats, feat_names, vs_ind, offsets = create_oracles(parser,
                                                          seg_weights={'line': {
                                                              'fermata': 1, 'basic.rest': 1}},
                                                          model_weights=None,
                                                          phrases=[0],
                                                          use_vertical=False)
    
    multi_gen.sync_generate(oracles, offsets)
    # key = 0
    # score = ScoreConversor()
    # sequence, end, k_trace = gen.generate(
    #     oracles[key], seq_len=30, p=0.3, k=0, LRS=5)
    # sequenced_events = [LinearEvent(
    #     from_list=o_feats[key][state-1], features=feat_names[key]) for state in sequence]
    # score.parse_events(sequenced_events, new_part=True, new_voice=True)
    # score.stream.show()

    # score = ScoreConversor()
    # sequence, end, k_trace = gen.generate(
    #     oracles[0], seq_len=30, p=0.3, k=0, LRS=5)
    # sequenced_events = [LinearEvent(
    #     from_list=o_feats[0][state-1], features=feat_names[0]) for state in sequence]
    # score.parse_events(sequenced_events, new_part=True, new_voice=True)
    # score.stream.show()

    # score = ScoreConversor()
    # for key, oracle in oracles.items():
    #     if key != 'vertical':
    #         sequence, end, k_trace = gen.generate(
    #             oracle, seq_len=30, p=0.3, k=0, LRS=5)
    #         sequenced_events = [LinearEvent(
    #             from_list=o_feats[key][state-1], features=feat_names[key]) for state in sequence]
    #         score.parse_events(sequenced_events, new_part=True, new_voice=True)
    # score.stream.show()


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


def create_vertical_oracle(parser, model_weights=None, dim1=0, dim2=None):
    """
    Create the vertical oracle
    """
    norm_features, o_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=parser.get_vertical_events(), weights=model_weights)
    thresh = gen_utils.find_threshold(
        norm_features[dim1:dim2], weights=weighted_fit, dim=len(features_names), entropy=True)

    if dim2 is None:
        dim2 = len(norm_features)

    oracle = gen_utils.build_oracle(
        norm_features[dim1:dim2], flag='a', features=features_names,
        weights=weighted_fit, dim=len(features_names),
        dfunc='cosine', threshold=thresh[0][1])
    return oracle


def create_line_oracle(parser, events, seg_weights=None, model_weights=None, dim1=0, dim2=None, vertical_offsets=None, phrases=None):
    """
    Create oracle for line part
    """
    line_seg_weights = None
    if seg_weights is not None and 'line' in seg_weights:
        line_seg_weights = seg_weights['line']

    vert_seg_weights = None
    if seg_weights is not None and 'vertical' in seg_weights:
        vert_seg_weights = seg_weights['vertical']

    vertical_start_indexes = []
    if vertical_offsets is not None:
        ev_offsets = [ev.get_offset() for ev in events]
        vertical_start_indexes = [
            vertical_offsets.index(off) for off in ev_offsets]
        segmentation(events, weights_line=line_seg_weights,
                     weights_vert=vert_seg_weights,
                     vertical_events=parser.get_vertical_events(),
                     indexes=vertical_start_indexes)
    else:
        segmentation(events, weights_line=line_seg_weights)

    apply_segmentation_info(events)

    new_events = []
    piece_phrases = get_phrases_from_events(events)
    if phrases is None:
        phrases = range(len(piece_phrases))

    for phrase in phrases:
        if phrase < len(piece_phrases):
            new_events.extend(piece_phrases[phrase])

    last_offset = new_events[-1].get_offset()

    if dim2 is None:
        dim2 = len(new_events)

    norm_features, o_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=new_events, weights=model_weights)
    thresh = gen_utils.find_threshold(
        norm_features[dim1:dim2], weights=weighted_fit, dim=len(features_names), entropy=True)
    oracle = gen_utils.build_oracle(
        norm_features[dim1:dim2], flag='a', features=features_names,
        weights=weighted_fit, dim=len(features_names),
        dfunc='cosine', threshold=thresh[0][1])

    return oracle, vertical_start_indexes, o_features, features_names, last_offset


def create_oracles(parser, seg_weights=None, model_weights=None, parts=None, phrases=None, use_vertical=False, print=True):
    """
    Creator of oracles
    """
    vertical_start_indexes = {}
    offsets = {}
    original_features = {}
    oracles = {}
    total_features_names = {}

    if parser.get_vertical_events() is not None:
        offsets['vertical'] = [ev.get_offset()
                               for ev in parser.get_vertical_events()]

    if parts is None:
        parts = list(parser.get_part_events())

    line_mod_weights = None
    if model_weights is not None and 'line' in model_weights:
        line_mod_weights = model_weights['line']

    vert_mod_weights = None
    if model_weights is not None and 'vertical' in model_weights:
        vert_mod_weights = model_weights['vertical']

    last_offset = 0.0
    for key, events in parser.get_part_events().items():
        if len(events) > 1 and key in parts:
            oracle, vs_ind, o_features, features_names, last_off = create_line_oracle(
                parser, events, seg_weights, line_mod_weights,
                vertical_offsets=(None, offsets['vertical'])[use_vertical], phrases=phrases)
            oracles[key] = oracle
            original_features[key] = o_features
            offsets[key] = [ev.get_offset() for ev in events]
            vertical_start_indexes[key] = vs_ind
            total_features_names[key] = features_names

            if (last_offset < last_off and last_off in offsets['vertical']):
                last_offset = last_off

    if parser.get_vertical_events() is not None:
        index = offsets['vertical'].index(last_offset)
        vert_oracle = create_vertical_oracle(
            parser, model_weights=vert_mod_weights, dim2=index)
        oracles['vertical'] = vert_oracle

    if print:
        for key, oracle in oracles.items():
            image = gen_plot.start_draw(oracle)
            name = r'data\myexamples\oracle of part ' + str(key) + '.PNG'
            image.save(name)

    return oracles, original_features, total_features_names, vertical_start_indexes, offsets


if __name__ == "__main__":
    main()

    # parsing_music_folder(r'D:\FEUP_1920\DISS\Dissertation\generation_system\data\database\music21\bach')
    # recover_parsed_folder(r'D:\FEUP_1920\DISS\Dissertation\generation_system\data\database\parsed\bach')
