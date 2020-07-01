#!/usr/bin/env python3.7
"""
This script presents the application class
To comunicate with interface
"""

import math
import os
import json

import numpy as np
from PyQt5 import QtCore

import application.single_oracle as single_oracle
import application.multi_oracle as multi_oracle

import application.representation.utils.features as rep_utils
import application.representation.utils.statistics as statistics

from application.representation.parsers.music_parser import MusicParser
from application.representation.parsers.segmentation import (apply_segmentation_info,
                                                             get_phrases_from_events,
                                                             segmentation,
                                                             INTERPART_WEIGHTS,
                                                             LINE_WEIGHTS)


class Application(QtCore.QObject):
    """
    Class Application,
    Communicates with interface to deal with the
    main part of the logistics of the app
    """
    signal_parsed = QtCore.pyqtSignal(int)
    signal_viewpoints = QtCore.pyqtSignal(dict)
    signal_oracle = QtCore.pyqtSignal(int)

    def __init__(self, music):
        QtCore.QObject.__init__(self)

        self.database_path = os.sep.join([os.getcwd(), 'database'])
        if not os.path.exists(self.database_path):
            self.database_path = os.getcwd()

        self.principal_music_path = music
        self.principal_music = None

        # Music To Use
        self.music = {}

        # Viewpoints To Use
        self.model_viewpoints = {
            'line': {},
            'inter-part': {}
        }
        self.segmentation_viewpoints = {
            'line': {},
            'inter-part': {}
        }
        self.music_information = {
            'parts': {},
            'inter-part': {}
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
            if '.mxl' in filename or '.xml' in filename:
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

        if interface is not None:
            self.signal_parsed.connect(
                interface.handler_finish_parsing)
            self.signal_parsed.emit(1)

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
        # Add Principal Music To Music
        if self.principal_music is None:
            print(self.principal_music_path)
            if '.mxl' in self.principal_music_path or '.xml' in self.principal_music_path:
                self.principal_music = (MusicParser(
                    self.principal_music_path), self.principal_music_path, False)
                self.principal_music[0].parse()
                self.music[self.principal_music[1]] = self.principal_music
            else:
                if self.music == {}:
                    return -1, -1
                else:
                    self.principal_music = self.music[list(
                        self.music.keys())[-1]]

        self.indexes_first = {}

        parts_features = []
        interpart_features = []

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

            # For each music, process interpart part, if exists
            interpart_part = parser.get_interpart_events()
            if interpart_part is not None or interpart_part is not []:
                self.indexes_first[music]['inter-part'] = len(
                    interpart_features)
                interpart_features.extend(interpart_part)

        return parts_features, interpart_features

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

    def get_statistics(self, part_features, interpart_features):
        """
        Calculate Statistics From Processed Music
        """
        statistic_dict = {}
        self.return_statistics_part('parts', part_features, statistic_dict)
        self.return_statistics_part(
            'inter-part', interpart_features, statistic_dict)
        return statistic_dict

    def calculate_statistics(self, interface, calc_weights=False):
        """
        Calculate Statistics For Viewpoints
        """
        self.indexes_first = {}

        part_features, interpart_features = self.process_music()
        if part_features == -1 and interpart_features == -1 and interface is not None:
            self.signal_parsed.connect(
                interface.error_no_music)
            self.signal_parsed.emit('ERROR')
            return

        statistic_dict = self.get_statistics(part_features, interpart_features)

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
        if 'parts' not in weight_dict and 'inter-part' not in 'weight_dict':
            statistics_dict = self.calculate_statistics(None, True)

            weight_dict['parts'] = {}
            fixed_dict['parts'] = {}
            weight_dict['inter-part'] = {}
            fixed_dict['inter-part'] = {}

            for key, stats in statistics_dict['parts'].items():
                weight_dict['parts'][key] = stats['weight']
                fixed_dict['parts'][key] = stats['fixed']
            for key, stats in statistics_dict['inter-part'].items():
                weight_dict['inter-part'][key] = stats['weight']
                fixed_dict['inter-part'][key] = stats['fixed']

        self.model_viewpoints = weight_dict
        return fixed_dict

    def part_segmentation(self, events, interpart_offsets, interpart_events):
        """
        Segmentation for a Part
        """
        if interpart_offsets is not None and self.segmentation_viewpoints['inter-part'] is not None:
            ev_offsets = [ev.get_offset() for ev in events]
            interpart_start_indexes = [
                interpart_offsets.index(off) for off in ev_offsets]
            segmentation(events, weights_line=self.segmentation_viewpoints['parts'],
                         weights_vert=self.segmentation_viewpoints['inter-part'],
                         interpart_events=interpart_events,
                         indexes=interpart_start_indexes)
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
            interpart_offsets = None

            # If interpart Elements exist, use them to calculate Segmentation
            if parser.get_interpart_events() is not None:
                interpart_offsets = [ev.get_offset()
                                    for ev in parser.get_interpart_events()]

            number_part = 0
            for key, events in parser.get_part_events().items():
                if len(events) > 0:
                    # Segment Part
                    self.part_segmentation(
                        events, interpart_offsets, parser.get_interpart_events())

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
        self.segmentation_viewpoints = {'inter-part': None}
        if 'parts' in weight_dict:
            self.segmentation_viewpoints['parts'] = {}
            for key in LINE_WEIGHTS:
                if key in weight_dict and weight_dict['parts'][key] != 0:
                    self.segmentation_viewpoints['parts'][key] = weight_dict['parts'][key]

        max_weight = max(list(weight_dict['parts'].values()))
        res_weights = {
            'derived.intphrase': max_weight,
            'phrase.boundary': max_weight,
            'phrase.length': max_weight
        }
        self.process_and_segment_parts(res_weights)
        self.model_viewpoints['parts'] = {**self.model_viewpoints['parts'], **res_weights}

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

            # file_path = r'data\myexamples\viewpoints' + '_' + str(key_part)
            # with open(file_path + '.json', 'w') as handle:
            #     json.dump(
            #         information['selected_features_names'], handle, indent=2)
            #     json.dump(information['fixed_weights'], handle, indent=2)
            #     json.dump(information['normed_weights'], handle, indent=2)
            #     handle.close()

    def apply_viewpoint_weights(self, weight_dict, fixed_dict):
        """
        Apply Choosen Weights
        """
        fixed_dict = self.process_weights(weight_dict, fixed_dict)
        self.segment(weight_dict)
        self.prepare_parts(fixed_dict, 'parts')
        self.prepare_parts(fixed_dict, 'inter-part')

    def generate_oracle(self, interface, line_oracle, line=0):
        """
        Construct Oracle Handler
        """
        if line_oracle:
            single_oracle.construct_single_oracle(self, line)
        else:
            multi_oracle.construct_multi_oracles(self)

        if interface is not None:
            self.signal_oracle.connect(
                interface.handler_create_sequence)
            self.signal_oracle.emit(1)

    def generate_sequences(self, line_oracle, num_seq):
        """
        Generate Sequences Handler
        """
        if line_oracle:
            single_oracle.generate_from_single(self, num_seq)
        else:
            multi_oracle.generate_from_multiple(self, num_seq)
