#!/usr/bin/env python3.7
"""
This script presents the application class
To comunicate with interface
"""

import os

import numpy as np
from PyQt5 import QtCore

import generation.gen_algorithms.generation as gen
import generation.gen_algorithms.multi_oracle_gen as multi_gen
import generation.plot_fo as gen_plot
import generation.utils as gen_utils

import representation.utils.features as rep_utils
import representation.utils.statistics as statistics

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
                self.music[filename] = (MusicParser(filename), filenames)
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

        for key in list(self.music.keys()) and folders_in_database_path:
            if self.music[key][1] not in folders_in_database_path:
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
                        self.music[name] = (music_parser, folder)

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
            if vertical_part is not None:
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
            for key, stats in statistic_dict['parts'].items():
                statistic_dict['parts'][key]['weight'] = 1
            for key, stats in statistic_dict['vertical'].items():
                statistic_dict['vertical'][key]['weight'] = 1

        if interface is not None:
            self.signal_viewpoints.connect(
                interface.create_statistics_overview)
            self.signal_viewpoints.emit(statistic_dict)
        else:
            return statistic_dict

    def apply_viewpoint_weights(self, weight_dict):
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

        res_weights = {
            'intphrase': 1,
            'phrase.boundary': 1,
            'phrase.length': 1
        }
        self.total_information_part_features = self.process_and_segment_parts(
            res_weights)

        part_columns, non_norm_part_weights, self.feat_part_names = self.get_columns_from_weights(
            self.model_viewpoints['parts'], self.part_features_names)
        vertical_columns, non_norm_vert_weights, self.feat_vert_names = self.get_columns_from_weights(
            self.model_viewpoints['vertical'], self.vert_features_names)

        self.selected_part_o_feats = self.total_information_part_features[:, part_columns]
        self.selected_vert_o_feats = self.vertical_features[:,
                                                            vertical_columns]

        self.normed_part_feats = rep_utils.normalize(
            self.selected_part_o_feats, -1, 1)
        self.normed_vertical_feats = rep_utils.normalize(
            self.selected_vert_o_feats, -1, 1)
        self.normalized_part_weights = rep_utils.normalize_weights(
            non_norm_part_weights)
        self.normalized_vert_weights = rep_utils.normalize_weights(
            non_norm_vert_weights)

        self.construct_oracles()

    def construct_oracles(self):
        """
        Construct Oracle from Information
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
                        self.selected_part_o_feats[start_index:finish_index])
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
            if key == 'vertical':
                features_names = self.feat_vert_names
                weights = self.normalized_vert_weights

            thresh = gen_utils.find_threshold(
                part, weights=weights, dim=len(features_names), entropy=True)
            self.oracles[key] = gen_utils.build_oracle(
                part, flag='a', features=features_names,
                weights=weights, dim=len(features_names),
                dfunc='cosine', threshold=thresh[0][1])

        image = gen_plot.start_draw(self.oracles, self.ev_offsets)
        name = r'data\myexamples\oracle' + '.PNG'
        image.save(name)

        sequences, ktraces = multi_gen.sync_generate(
            self.oracles, self.ev_offsets, seq_len=100, p=0.2, k=0)
        score = ScoreConversor()
        for key, sequence in sequences.items():
            if key != 'vertical':
                sequenced_events = [LinearEvent(
                    from_list=self.orig_info[key][state-2], features=self.feat_part_names) for state in sequence]
                if len(sequenced_events) > 0:
                    score.parse_events(
                        sequenced_events, new_part=True, new_voice=True)
        score.stream.show()

    def get_columns_from_weights(self, weights, features_names):
        """
        Get Columns and Weights (non-normalized)
        per weighted_viewpoints and features_names
        """
        columns_to_retain = []
        weights_per_column = []
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
                weights_per_column.append(weights[new_key])
                feature_names_per_column.append(key)

        return columns_to_retain, weights_per_column, feature_names_per_column

    def process_and_segment_parts(self, res_weights):
        """
        Segment Parts and join segmentation
        information to part features,
        not yet normalized
        """
        new_part_features = []
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
                    concatenated = list(np.concatenate(
                        (self.part_features[first_ind:last_ind], features), axis=1))
                    new_part_features.extend(concatenated)
                    number_part += 1
        self.part_features_names.extend(res_weights.keys())
        return np.array(new_part_features)

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
