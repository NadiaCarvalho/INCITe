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

import representation.utils.features as rep_utils
import representation.utils.statistics as statistics
import single_oracle as single
import multi_oracle as multi
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

    signal_oracle_start = QtCore.pyqtSignal(int)

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

            cols, weights, fixed_weights, feature_names = rep_utils.get_columns_from_weights(
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
            single.construct_single_oracle(self, line)
        else:
            multi.construct_multi_oracles(self)

        if interface is not None:
            self.signal_parsed.connect(
                interface.handler_create_sequence)
            self.signal_parsed.emit(1)

    def generate_sequences(self, line_oracle, num_seq):
        """
        Generate Sequences Handler
        """
        if line_oracle:
            single.construct_single_oracle(self, num_seq)
        else:
            multi.generate_from_multiple(self, num_seq)
