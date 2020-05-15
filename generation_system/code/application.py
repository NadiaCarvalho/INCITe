#!/usr/bin/env python3.7
"""
This script presents the application class 
To comunicate with interface
"""

import os

import numpy as np

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

class Application():
    """
    Class Application,
    Communicates with interface to deal with the 
    main part of the logistics of the app
    """
    def __init__(self):

        self.database_path = os.getcwd()

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

    def parse_files(self, filenames):
        """
        Parses Music
        """
        print(self.database_path)
        for filename in filenames:
            if '.mxl' in filename:
                self.music[filename] = MusicParser(filename)
                self.music[filename].parse()

                folder_name = ['']
                if self.music[filename].music.metadata.composer is not None:
                    folder_name = [self.music[filename].music.metadata.composer.split(' ')[-1]]
                
                name = os.path.normpath(filename).split(os.path.sep)[-1]
                name = '.'.join(name.split('.')[:-1])

                folders = self.database_path.split(os.path.sep) + folder_name


                self.music[filename].to_pickle(name, folders)
                
