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
        self.music_information = {
            'parts': {},
            'vertical': {}
        }
        self.oracles_information = {
            'single_oracle': {},
            'multiple_oracles': {}
        }

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
                self.music[filename][0].to_json(name, folders)

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
        Recover Parsed Music in Folder
        """
        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for filename in files:
                    name = '.'.join(filename.split('.')[:-1])
                    if not name in self.music and '.pbz2' in filename:
                        music_parser = MusicParser()
                        music_parser.from_pickle(name, root.split(os.sep))
                        self.music[name] = (music_parser, folder, True)

    def process_music(self):
        """
        Process Music To Learn Statistics
        And Construct Oracles
        """
        self.indexes_first = {}

        parts_features = []
        vertical_features = []

        for music, _tuple in self.music.items():
            parser = _tuple[0]
            self.indexes_first[music] = {}

            # For each music, process all parts
            for key, part in parser.get_part_events().items():
                if 'parts' not in self.indexes_first[music]:
                    self.indexes_first[music]['parts'] = []
                if len(part) > 0:
                    self.indexes_first[music]['parts'].append(len(
                        parts_features))
                    parts_features.extend(part)

            # For each music, process vertical part, if exists
            vertical_part = parser.get_vertical_events()
            if vertical_part is not None or vertical_part is not []:
                self.indexes_first[music]['vertical'] = len(
                    vertical_features)
                vertical_features.extend(vertical_part)

        return parts_features, vertical_features

    def return_statistics_part(self, key_part, features, statistic_dict):
        """
        Generate Statistic from Information
        """
        if len(features) > 0:
            # Calculate Statistics
            stats, original, feat_names = statistics.statistic_features(
                features)

            # Save Information
            information = self.music_information[key_part]
            information['original_features'] = original
            information['original_features_names'] = feat_names
            statistic_dict[key_part] = stats

    def get_statistics(self, part_features, vertical_features):
        """
        Calculate Statistics From Processed Music
        """
        statistic_dict = {}
        self.return_statistics_part('parts', part_features, statistic_dict)
        self.return_statistics_part(
            'vertical', vertical_features, statistic_dict)
        return statistic_dict

    def calculate_statistics(self, interface, calc_weights=False):
        """
        Calculate Statistics For Viewpoints
        """
        self.indexes_first = {}

        part_features, vertical_features = self.process_music()
        statistic_dict = self.get_statistics(part_features, vertical_features)

        # TODO: Calculate measurement for better viewpoints
        if calc_weights:
            statistics.calculate_automatic_viewpoints(statistic_dict)

        if interface is not None:
            self.signal_viewpoints.connect(
                interface.create_statistics_overview)
            self.signal_viewpoints.emit(statistic_dict)
        else:
            return statistic_dict

    def process_weights(self, weight_dict, fixed_dict):
        """
        Process Incoming Weights
        """
        # Non incoming weights
        if weight_dict['parts'] == {} and weight_dict['vertical'] == {}:
            statistics_dict = self.calculate_statistics(None, True)
            for key, stats in statistics_dict['parts'].items():
                weight_dict['parts'][key] = stats['weight']
            for key, stats in statistics_dict['vertical'].items():
                weight_dict['vertical'][key] = stats['weight']

        self.model_viewpoints = weight_dict

    def part_segmentation(self, events, vertical_offsets, vertical_events):
        """
        Segmentation for a Part
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

    def process_and_segment_parts(self, res_weights):
        """
        Segment Parts and join segmentation
        information to part features,
        not yet normalized
        """
        part_features = self.music_information['parts']['original_features']
        part_features_names = self.music_information['parts']['original_features_names']

        index_of_res_weights = [part_features_names.index(
            key) for key in res_weights.keys() if key in part_features_names]

        for music, _tuple in self.music.items():
            parser = _tuple[0]
            vertical_offsets = None

            # If vertical Elements exist, use them to calculate Segmentation
            if parser.get_vertical_events() is not None:
                vertical_offsets = [ev.get_offset()
                                    for ev in parser.get_vertical_events()]

            number_part = 0
            for key, events in parser.get_part_events().items():
                if len(events) > 0:
                    # Segment Part
                    self.part_segmentation(
                        events, vertical_offsets, parser.get_vertical_events())

                    # Get Features For Weights
                    features, _ = rep_utils.create_feat_array(
                        events, res_weights, False)
                    first_ind = self.indexes_first[music]['parts'][number_part]
                    last_ind = first_ind + len(events)
                    part_features[first_ind:last_ind,
                                  index_of_res_weights] = features
                    number_part += 1

    def segment(self, weight_dict):
        """
        Segment Music
        """
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

    def prepare_parts(self, fixed_dict, key_part):
        """
        Prepare Parts
        """
        if key_part in self.model_viewpoints:
            information = self.music_information[key_part]

            cols, weights, fixed_weights, feature_names = self.get_columns_from_weights(
                self.model_viewpoints[key_part],
                fixed_dict[key_part],
                information['original_features_names'])

            information['fixed_weights'] = fixed_weights
            information['selected_features_names'] = feature_names

            sel_part_features = information['original_features'][:, cols]
            information['selected_original'] = sel_part_features
            information['selected_normed'] = rep_utils.normalize(
                sel_part_features, -1, 1)
            information['normed_weights'] = rep_utils.normalize_weights(
                weights)

    def apply_viewpoint_weights(self, weight_dict, fixed_dict):
        """
        Apply Choosen Weights
        """
        self.process_weights(weight_dict, fixed_dict)
        self.segment(weight_dict)
        self.prepare_parts(fixed_dict, 'parts')
        self.prepare_parts(fixed_dict, 'vertical')

    def generate_oracle(self, interface, line_oracle, line=0):
        """
        Construct Oracle Handler
        """
        if line_oracle:
            self.construct_single_oracle(line)
        else:
            self.construct_multi_oracles()

        if interface is not None:
            self.signal_parsed.connect(
                interface.handler_create_sequence)
            self.signal_parsed.emit(1)

    def generate_sequences(self, line_oracle, num_seq):
        """
        Generate Sequences Handler
        """
        if line_oracle:
            self.generate_from_single(num_seq)
        else:
            self.generate_from_multiple(num_seq)

    def get_single_part_features(self, information, line):
        """
        Get Part Features
        """
        normed_features = []
        original_features = []

        for music, _tuple in self.music.items():
            parser = _tuple[0]

            i = 0
            for key, events in parser.get_part_events().items():
                if len(events) > 0 and i == line:

                    # Get Start and End Indexes
                    start_index = self.indexes_first[music]['parts'][i]
                    finish_index = start_index + len(events)

                    normed_features.extend(
                        information['selected_normed'][start_index:finish_index])
                    original_features.extend(
                        information['selected_original'][start_index:finish_index])
                    break
                elif len(events) > 0:
                    i += 1

        return normed_features, original_features

    def get_multiple_part_features(self, part_info, vert_info):
        """
        Get Multiple Part Features
        """
        ev_offsets = {}
        normed_features = {}
        original_features = {}

        for music, _tuple in self.music.items():
            parser = _tuple[0]
            last_offset = 0
            if ev_offsets != {}:
                last_offset = max([part_off[-1]
                                   for part_off in ev_offsets.values()])

            i = 0
            for key, events in parser.get_part_events().items():
                if len(events) > 0:
                    start_index = self.indexes_first[music]['parts'][i]
                    finish_index = start_index + len(events)

                    if i not in normed_features:
                        normed_features[i] = []
                        ev_offsets[i] = []
                        original_features[i] = []

                    normed_features[i].extend(
                        part_info['selected_normed'][start_index:finish_index])
                    original_features[i].extend(
                        part_info['selected_original'][start_index:finish_index])
                    ev_offsets[i].extend(
                        [ev.get_offset() + last_offset for ev in events])

                    i += 1

            vertical_events = parser.get_vertical_events()
            if len(vertical_events) > 0:
                start_index = self.indexes_first[music]['vertical']
                finish_index = start_index + len(vertical_events)

                if 'vertical' not in normed_features:
                    normed_features['vertical'] = []
                    ev_offsets['vertical'] = []

                normed_features['vertical'].extend(
                    vert_info['selected_normed'][start_index:finish_index])
                ev_offsets['vertical'].extend(
                    [ev.get_offset() + last_offset for ev in vertical_events])

        return normed_features, original_features, ev_offsets

    def construct_single_oracle(self, line):
        """
        Construct Oracle from Information
        """
        part_information = self.music_information['parts']
        features_names = part_information['selected_features_names']
        weights = part_information['normed_weights']
        fixed_weights = part_information['fixed_weights']

        # Get Normed and Original Features
        normed_features, original_features = self.get_single_part_features(
            part_information, line)

        thresh = gen_utils.find_threshold(
            normed_features, weights=weights,
            fixed_weights=fixed_weights,
            dim=len(features_names), entropy=True)

        oracle = gen_utils.build_oracle(
            normed_features, flag='a', features=features_names,
            weights=weights, fixed_weights=fixed_weights,
            dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])

        image = gen_plot.start_draw(oracle)
        name = r'data\myexamples\oracle' + '.PNG'
        image.save(name)

        self.oracles_information['single_oracle'] = {
            'oracle': oracle,
            'normed_features': normed_features,
            'original_features': original_features,
            'features_names': features_names
        }

    def generate_sequences_single(self, information, num_seq):
        """
        Generate Sequences
        """
        ordered_sequences = []

        i = 0
        while i < num_seq:
            sequence, kend, ktrace = gen.generate(
                oracle=information['oracle'], seq_len=100, p=0.5, k=0, LRS=3)
            if len(sequence) > 0:
                dist = distance_between_windowed_features(
                    [information['normed_features'][state-1]
                        for state in sequence],
                    information['normed_features'])
                ordered_sequences.append((sequence, dist))
                i += 1

        ordered_sequences.sort(key=lambda tup: tup[1])
        return ordered_sequences

    def generate_from_single(self, num_seq):
        """
        Generate Music From a Single Oracle
        """
        information = self.oracles_information['single_oracle']

        original_sequence = range(len(information['original_features']))
        self.linear_score_generator(original_sequence, information['original_features'],
                                    information['features_names'], name='original', start=0)

        localtime = time.asctime(time.localtime(time.time()))
        localtime = '_'.join(localtime.split(' '))
        localtime = '-'.join(localtime.split(':'))

        ordered_sequences = self.generate_sequences_single(
            information, num_seq)
        # Generate Scores of Ordered Sequences
        for i, (sequence, dist) in enumerate(ordered_sequences):
            name = 'gen_' + localtime + '_' + \
                str(i) + '_distance_' + str(dist) + '.xml'
            self.linear_score_generator(
                sequence, information['original_features'],
                information['features_names'], name=name)

    def construct_multi_oracles(self):
        """
        Construct Multiple Oracles from Information
        """
        part_information = self.music_information['parts']
        vert_information = self.music_information['vertical']

        normed_features, original_features, ev_offsets = self.get_multiple_part_features(
            part_information, vert_information)

        oracles = {}

        for key, part in normed_features.items():
            features_names = part_information['selected_features_names']
            weights = part_information['normed_weights']
            fixed_weights = part_information['fixed_weights']
            if key == 'vertical':
                features_names = vert_information['selected_features_names']
                weights = vert_information['normed_weights']
                fixed_weights = vert_information['fixed_weights']

            thresh = gen_utils.find_threshold(
                part, weights=weights, fixed_weights=fixed_weights,
                dim=len(features_names), entropy=True)
            oracles[key] = gen_utils.build_oracle(
                part, flag='a', features=features_names,
                weights=weights, fixed_weights=fixed_weights,
                dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])

        image = gen_plot.start_draw(oracles, ev_offsets)
        name = r'data\myexamples\oracle' + '.PNG'
        image.save(name)

        self.oracles_information['multiple_oracles'] = {
            'oracles': oracles,
            'normed_features': normed_features,
            'original_features': original_features,
            'features_names': part_information['selected_features_names'],
            'offsets': ev_offsets
        }

    def generate_from_multiple(self, num_seq):
        """
        Generate Sequences From a Multiple Oracle
        """
        information = self.oracles_information['multiple_oracles']

        # Save original Score
        original_sequences = {}
        for key, part in information['original_features'].items():
            original_sequences[key] = range(len(part))
        self.multi_sequence_score_generator(
            original_sequences, information['original_features'],
            information['features_names'], name='original', start=0)

        localtime = time.asctime(time.localtime(time.time()))
        localtime = '_'.join(localtime.split(' '))
        localtime = '-'.join(localtime.split(':'))
        for i in range(num_seq):
            sequences, ktraces = multi_gen.sync_generate(
                information['oracles'], information['offsets'], seq_len=50, p=0.5, k=0)
            self.multi_sequence_score_generator(
                sequences, information['original_features'],
                information['features_names'],
                name='gen_' + localtime + '_' + str(i))

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

    def linear_score_generator(self, sequence, o_information, feature_names, name='', start=-1):
        sequenced_events = [LinearEvent(
            from_list=o_information[state+start], features=feature_names) for state in sequence]
        if len(sequenced_events) > 0:
            score = ScoreConversor()
            score.parse_events(
                sequenced_events, new_part=True, new_voice=True)
            # score.stream.show()
            path = os.sep.join([os.getcwd(), 'data', 'generations', name])
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
