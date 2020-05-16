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

import representation.utils as rep_utils
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
    signal = QtCore.pyqtSignal(int)

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

    def parse_database(self):
        """
        Parses Music
        """
        pass

    def parse_files(self, filenames, interface):
        """
        Parses Music
        """
        self.signal.connect(interface.increase_progress_bar)

        reversed_filenames = reversed(filenames)

        n_processed = 0
        for filename in reversed_filenames:
            if '.mxl' in filename:
                self.music[filename] = MusicParser(filename)
                self.music[filename].parse()

                folder_name = ['Other']
                if self.music[filename].music.metadata.composer is not None:
                    folder_name = [
                        self.music[filename].music.metadata.composer.split(' ')[-1]]
                    folder_name[-1].capitalize()
                name = os.path.normpath(filename).split(os.path.sep)[-1]
                name = '.'.join(name.split('.')[:-1])
                folders = self.database_path.split(os.path.sep) + folder_name
                self.music[filename].to_pickle(name, folders)

                n_processed += 1
                perc = int((n_processed/len(filenames))*100)
                self.signal.emit(perc)

    def retrieve_database(self, folders):
        """
        Retrieves Music from Database
        """
        folders_in_database_path = [f.path for f in os.scandir(
            self.database_path) if f.is_dir() and any(folder in f.path for folder in folders)]
        for folder in folders_in_database_path:
            self.recover_parsed_folder(folder)

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
                        self.music[name] = music_parser

    def calculate_statistics(self):
        """
        Calculate Statistics For Viewpoints
        """
        entire_music_to_learn_statistics = []

        for music, parser in self.music.items():
            for key, part in parser.get_part_events().items():
                entire_music_to_learn_statistics.extend(part)

        print(len(entire_music_to_learn_statistics))

