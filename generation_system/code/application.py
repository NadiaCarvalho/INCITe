#!/usr/bin/env python3.7
"""
This script presents the application class
To comunicate with interface
"""

import math
import os
import time

import numpy as np
from PyQt5 import QtCore

import generation.gen_algorithms.generation as gen
import generation.gen_algorithms.multi_oracle_gen as multi_gen
import generation.plot_fo as gen_plot
import generation.utils as gen_utils
import representation.utils.features as rep_utils
import representation.utils.statistics as statistics
from generation.cdist_fixed import distance_between_windowed_features
from representation.conversor.score_conversor import ScoreConversor
from representation.events.linear_event import LinearEvent
from representation.parsers.music_parser import MusicParser
from representation.parsers.segmentation import (apply_segmentation_info,
                                                 get_phrases_from_events,
                                                 segmentation)


class Application(QtCore.QObject):
    """
    Class Application,
    Communicates with interface to deal with the
    main part of the logistics of the app
    """
    signal_parsed = QtCore.pyqtSignal(int)
    signal_viewpoints = QtCore.pyqtSignal(dict)

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.database_path = os.sep.join([os.getcwd(), 'data', 'database'])

        # Music To Use
        self.music = {}

        # Viewpoints To Use
        self.model_viewpoints = {
            'line': {},
            'vertical': {}
        }
        self.segmentation_viewpoints = {
            'line': {},
            'vertical': {}
        }

        # Music Generated
        self.generation_sequences = {}

    def parse_files(self, filenames, interface):
        """
        Parses Music
        """
        self.signal_parsed.connect(interface.increase_progress_bar)

        reversed_filenames = reversed(filenames)

        n_processed = 0
        for filename in reversed_filenames:
            if '.mxl' in filename:
                self.music[filename] = (MusicParser(filename), filename, False)
                self.music[filename][0].parse()

                folder_name = ['Other']
                if self.music[filename][0].music.metadata.composer is not None:
                    folder_name = [
                        self.music[filename][0].music.metadata.composer.split(' ')[-1]]
                    folder_name[-1].capitalize()
                name = os.path.normpath(filename).split(os.path.sep)[-1]
                name = '.'.join(name.split('.')[:-1])
                folders = self.database_path.split(os.path.sep) + folder_name
                self.music[filename][0].to_pickle(name, folders)

                n_processed += 1

                perc = int((n_processed/len(filenames))*100)
                self.signal_parsed.emit(perc)

    def retrieve_database(self, folders):
        """
        Retrieves Music from Database
        """
        folders_in_database_path = [f.path for f in os.scandir(
            self.database_path) if f.is_dir() and any(folder in f.path for folder in folders)]
        for folder in folders_in_database_path:
            self.recover_parsed_folder(folder)

        if folders_in_database_path:
            for key in list(self.music.keys()):
                if self.music[key][1] not in folders_in_database_path and self.music[key][2]:
                    self.music.pop(key, None)

    def recover_parsed_folder(self, folder):
        """
        Recover parsed music in folder
        """
        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for filename in files:
                    name = '.'.join(filename.split('.')[:-1])
                    if not name in self.music and '.pbz2' in filename:
                        music_parser = MusicParser()
                        music_parser.from_pickle(name, root.split(os.sep))
                        self.music[name] = (music_parser, folder, True)

    def calculate_statistics(self, interface, calc_weights=False):
        """
        Calculate Statistics For Viewpoints
        """
        self.indexes_first = {}

        entire_part_music_to_learn_statistics = []
        vertical_music_to_learn = []

        for music, _tuple in self.music.items():
            parser = _tuple[0]
            self.indexes_first[music] = {}

            for key, part in parser.get_part_events().items():
                if 'parts' not in self.indexes_first[music]:
                    self.indexes_first[music]['parts'] = []
                if len(part) > 0:
                    self.indexes_first[music]['parts'].append(len(
                        entire_part_music_to_learn_statistics))
                    entire_part_music_to_learn_statistics.extend(part)

            vertical_part = parser.get_vertical_events()
            if vertical_part is not None or vertical_part is not []:
                self.indexes_first[music]['vertical'] = len(
                    vertical_music_to_learn)
                vertical_music_to_learn.extend(vertical_part)

        statistic_part_dict_percentages, self.part_features, self.part_features_names = statistics.statistic_features(
            entire_part_music_to_learn_statistics)
        statistic_vert_dict_percentages, self.vertical_features, self.vert_features_names = statistics.statistic_features(
            vertical_music_to_learn)

        statistic_dict = {
            'parts': statistic_part_dict_percentages,
            'vertical': statistic_vert_dict_percentages
        }

        # TODO: Calculate measurement for better viewpoints
        if calc_weights:
            variances_parts = dict([(key, stats['variance'])
                                    for key, stats in statistic_dict['parts'].items()])
            variances_parts = rep_utils.normalize_dictionary(
                variances_parts, x_min=0, x_max=100)
            variances_vert = dict([(key, stats['variance'])
                                   for key, stats in statistic_dict['vertical'].items()])
            variances_vert = rep_utils.normalize_dictionary(
                variances_vert, x_min=0, x_max=100)

            for key, stats in statistic_dict['parts'].items():
                stats['weight'] = variances_parts[key]
                stats['fixed'] = False

            for key, stats in statistic_dict['vertical'].items():
                stats['weight'] = variances_vert[key]
                stats['fixed'] = False

        if interface is not None:
            self.signal_viewpoints.connect(
                interface.create_statistics_overview)
            self.signal_viewpoints.emit(statistic_dict)
        else:
            return statistic_dict

    def apply_viewpoint_weights(self, weight_dict, fixed_dict):
        """
        Apply choosen weights
        """
        if weight_dict['parts'] == {} and weight_dict['vertical'] == {}:
            statistics_dict = self.calculate_statistics(None, True)
            for key, stats in statistics_dict['parts'].items():
                weight_dict['parts'][key] = stats['weight']
            for key, stats in statistics_dict['vertical'].items():
                weight_dict['vertical'][key] = stats['weight']

        self.model_viewpoints = weight_dict

        self.segmentation_viewpoints = {
            'parts': {'fermata': 1, 'basic.rest': 1},
            'vertical': None}
        # TODO: Decide from the ones incoming

        max_weight = max(list(weight_dict['parts'].values()))
        res_weights = {
            'derived.intphrase': max_weight,
            'phrase.boundary': max_weight,
            'phrase.length': max_weight
        }
        self.process_and_segment_parts(res_weights)

        part_columns, non_norm_part_weights, self.fixed_part_weights, self.feat_part_names = self.get_columns_from_weights(
            self.model_viewpoints['parts'], fixed_dict['parts'], self.part_features_names)
        vertical_cols, non_norm_vert_weights, self.fixed_vert_weights, self.feat_vert_names = self.get_columns_from_weights(
            self.model_viewpoints['vertical'], fixed_dict['vertical'], self.vert_features_names)

        self.sel_part_o_feats = self.part_features[:, part_columns]
        self.sel_vert_o_feats = self.vertical_features[:,
                                                       vertical_cols]

        self.normed_part_feats = rep_utils.normalize(
            self.sel_part_o_feats, -1, 1)
        self.normed_vertical_feats = rep_utils.normalize(
            self.sel_vert_o_feats, -1, 1)
        self.normalized_part_weights = rep_utils.normalize_weights(
            non_norm_part_weights)
        self.normalized_vert_weights = rep_utils.normalize_weights(
            non_norm_vert_weights)

    def process_and_segment_parts(self, res_weights):
        """
        Segment Parts and join segmentation
        information to part features,
        not yet normalized
        """
        index_of_res_weights = [self.part_features_names.index(
            key) for key in res_weights.keys() if key in self.part_features_names]
        for music, _tuple in self.music.items():
            parser = _tuple[0]
            vertical_offsets = None
            if parser.get_vertical_events() is not None:
                vertical_offsets = [ev.get_offset()
                                    for ev in parser.get_vertical_events()]
            number_part = 0
            for key, events in parser.get_part_events().items():
                if len(events) > 0:
                    self.part_segmentation(
                        events, vertical_offsets, parser.get_vertical_events())
                    features, _ = rep_utils.create_feat_array(
                        events, res_weights, False)
                    first_ind = self.indexes_first[music]['parts'][number_part]
                    last_ind = first_ind + len(events)
                    self.part_features[first_ind:last_ind,
                                       index_of_res_weights] = features
                    number_part += 1

    def part_segmentation(self, events, vertical_offsets, vertical_events):
        """
        Segmentation for a part
        """
        if vertical_offsets is not None and self.segmentation_viewpoints['vertical'] is not None:
            ev_offsets = [ev.get_offset() for ev in events]
            vertical_start_indexes = [
                vertical_offsets.index(off) for off in ev_offsets]
            segmentation(events, weights_line=self.segmentation_viewpoints['parts'],
                         weights_vert=self.segmentation_viewpoints['vertical'],
                         vertical_events=vertical_events,
                         indexes=vertical_start_indexes)
        else:
            segmentation(
                events, weights_line=self.segmentation_viewpoints['parts'])
        apply_segmentation_info(events)

    def generate_oracle(self, interface, line_oracle, line=0):
        """
        Construct oracle and generate
        """
        if line_oracle:
            self.construct_single_oracle(line)
        else:
            self.construct_oracles()

        if interface is not None:
            self.signal_parsed.connect(
                interface.handler_create_sequence)
            self.signal_parsed.emit(1)

    def generate_sequences(self, line_oracle, num_seq):
        """
        Construct oracle and generate
        """
        if line_oracle:
            self.generate_from_single(num_seq)
        else:
            self.generate_from_multiple(num_seq)

    def construct_single_oracle(self, line):
        """
        Construct Oracle from Information
        """
        self.ev_offsets = []
        self.normed_info_for_oracles = []
        self.orig_info = []

        for music, _tuple in self.music.items():
            parser = _tuple[0]
            last_offset = 0
            if self.ev_offsets != []:
                last_offset = self.ev_offsets[-1]

            i = 0
            for key, events in parser.get_part_events().items():
                if len(events) > 0 and i == line:
                    start_index = self.indexes_first[music]['parts'][i]
                    finish_index = start_index + len(events)
                    self.normed_info_for_oracles.extend(
                        self.normed_part_feats[start_index:finish_index])
                    self.orig_info.extend(
                        self.sel_part_o_feats[start_index:finish_index])
                    self.ev_offsets.extend(
                        [ev.get_offset() + last_offset for ev in events])
                    i += 1

        features_names = self.feat_part_names
        weights = self.normalized_part_weights
        thresh = gen_utils.find_threshold(
            self.normed_info_for_oracles, weights=weights,
            fixed_weights=self.fixed_part_weights,
            dim=len(features_names), entropy=True)
        self.oracle = gen_utils.build_oracle(
            self.normed_info_for_oracles, flag='a', features=features_names,
            weights=weights, fixed_weights=self.fixed_part_weights,
            dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])

        image = gen_plot.start_draw(self.oracle)
        name = r'data\myexamples\oracle' + '.PNG'
        image.save(name)

    def generate_from_single(self, num_seq):
        """
        Generate music from a single oracle
        """
        localtime = time.asctime(time.localtime(time.time()))
        localtime = '_'.join(localtime.split(' '))
        localtime = '-'.join(localtime.split(':'))

        ordered_sequences = []

        i = 0
        while i < num_seq:
            sequence, kend, ktrace = gen.generate(
                oracle=self.oracle, seq_len=100, p=0.5, k=0, LRS=3)
            if len(sequence) > 0:
                dist = distance_between_windowed_features(
                    [self.normed_info_for_oracles[state-1] for state in sequence], self.normed_info_for_oracles)
                ordered_sequences.append((sequence, dist))
                i += 1

        ordered_sequences.sort(key=lambda tup: tup[1])

        for i, (sequence, dist) in enumerate(ordered_sequences):
            sequenced_events = [LinearEvent(
                from_list=self.orig_info[state-1], features=self.feat_part_names) for state in sequence]
            if len(sequenced_events) > 0:
                score = ScoreConversor()
                score.parse_events(
                    sequenced_events, new_part=True, new_voice=True)
                # score.stream.show()
                name = 'gen_' + localtime + '_' + \
                    str(i) + '_distance_' + str(dist) + '.xml'
                path = os.sep.join([os.getcwd(), 'data', 'generations', name])
                fp = score.stream.write(fp=path)

    def construct_oracles(self):
        """
        Construct Multiple Oracles from Information
        """
        self.orig_info = {}
        self.normed_info_for_oracles = {}
        self.ev_offsets = {}

        for music, _tuple in self.music.items():
            parser = _tuple[0]
            last_offset = 0
            if self.ev_offsets != {}:
                last_offset = max([part_off[-1]
                                   for part_off in self.ev_offsets.values()])

            i = 0
            for key, events in parser.get_part_events().items():
                if len(events) > 0:
                    start_index = self.indexes_first[music]['parts'][i]
                    finish_index = start_index + len(events)

                    if i not in self.normed_info_for_oracles:
                        self.normed_info_for_oracles[i] = []
                        self.ev_offsets[i] = []
                        self.orig_info[i] = []

                    self.normed_info_for_oracles[i].extend(
                        self.normed_part_feats[start_index:finish_index])
                    self.orig_info[i].extend(
                        self.sel_part_o_feats[start_index:finish_index])
                    self.ev_offsets[i].extend(
                        [ev.get_offset() + last_offset for ev in events])
                    i += 1

            vertical_events = parser.get_vertical_events()
            if len(vertical_events) > 0:
                start_index = self.indexes_first[music]['vertical']
                finish_index = start_index + len(vertical_events)

                if 'vertical' not in self.normed_info_for_oracles:
                    self.normed_info_for_oracles['vertical'] = []
                    self.ev_offsets['vertical'] = []

                self.normed_info_for_oracles['vertical'].extend(
                    self.normed_vertical_feats[start_index:finish_index])
                self.ev_offsets['vertical'].extend(
                    [ev.get_offset() + last_offset for ev in vertical_events])

        self.oracles = {}

        for key, part in self.normed_info_for_oracles.items():
            features_names = self.feat_part_names
            weights = self.normalized_part_weights
            fixed_weights = self.fixed_part_weights
            if key == 'vertical':
                features_names = self.feat_vert_names
                weights = self.normalized_vert_weights
                fixed_weights = self.fixed_vert_weights

            thresh = gen_utils.find_threshold(
                part, weights=weights, fixed_weights=fixed_weights,
                dim=len(features_names), entropy=True)
            self.oracles[key] = gen_utils.build_oracle(
                part, flag='a', features=features_names,
                weights=weights, fixed_weights=fixed_weights,
                dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])

        image = gen_plot.start_draw(self.oracles, self.ev_offsets)
        name = r'data\myexamples\oracle' + '.PNG'
        image.save(name)

    def generate_from_multiple(self, num_seq):
        """
        Generate from a multiple oracle
        """
        original_sequences = {}
        for key, part in self.orig_info.items():
            original_sequences[key] = range(len(part))
        self.multi_sequence_score_generator(
            original_sequences, self.orig_info, self.feat_part_names, name='original', start=0)

        localtime = time.asctime(time.localtime(time.time()))
        localtime = '_'.join(localtime.split(' '))
        localtime = '-'.join(localtime.split(':'))
        for i in range(num_seq):
            sequences, ktraces = multi_gen.sync_generate(
                self.oracles, self.ev_offsets, seq_len=50, p=0.5, k=0)
            self.multi_sequence_score_generator(
                sequences, self.orig_info, self.feat_part_names, name='gen_' + localtime + '_' + str(i))

    def multi_sequence_score_generator(self, sequences, o_information, feature_names, name='', start=-1):
        """
        Generate Score
        """
        score = ScoreConversor()
        for key, sequence in sequences.items():
            if key != 'vertical':
                sequenced_events = [LinearEvent(
                    from_list=o_information[key][state + start], features=feature_names)
                    if (state + start) < len(o_information[key])
                    else print('key: state ' + str(state + start))
                    for state in sequence]
                if len(sequenced_events) > 0:
                    score.parse_events(
                        sequenced_events, new_part=True, new_voice=True)
        # score.stream.show()

        path = os.sep.join([os.getcwd(), 'data', 'generations', name + '.xml'])
        fp = score.stream.write(fp=path)

    def get_columns_from_weights(self, weights, fixed_weights, features_names):
        """
        Get Columns and Weights (non-normalized)
        per weighted_viewpoints and features_names
        """
        columns_to_retain = []
        weights_per_column = []
        fixed_per_column = []
        feature_names_per_column = []
        for i, key in enumerate(features_names):
            new_key = key
            if '=' in key:
                new_key = key.split('=')[0]
            elif any(s in key for s in ['articulation', 'expressions.expression', 'ornamentation',
                                        'dynamic', 'chordPitches', 'pitches', 'pitchClass',
                                        'primeForm', 'pcOrdered']):
                new_key = key.split('_')[0]

            if new_key in weights and weights[new_key] != 0:
                columns_to_retain.append(i)

                is_fixed = False
                if new_key in fixed_weights:
                    is_fixed = fixed_weights[new_key]
                fixed_per_column.append(is_fixed)

                weight = weights[new_key]
                if is_fixed:
                    weight = max(weights.values()) + 1
                weights_per_column.append(weight)

                feature_names_per_column.append(key)

        return columns_to_retain, weights_per_column, fixed_per_column, feature_names_per_column
