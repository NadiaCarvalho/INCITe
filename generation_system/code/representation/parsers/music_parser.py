#!/usr/bin/env python3.7
"""
This script presents the class Parser that tries different approaches to segment a melodic line
"""

import os
import bz2
import pickle
import json

from music21 import converter

import representation.utils as utils
from representation.parsers.line_parser import LineParser
from representation.parsers.vertical_parser import VerticalParser

from representation.events.linear_event import LinearEvent
from representation.events.vertical_event import VerticalEvent


class MusicParser:
    """
    A class used to parse a musical file.

    Attributes
    ----------
    """

    def __init__(self, filename=None, folders=['data', 'myexamples']):

        self.music = None
        self.music_parts = []

        self.music_events = {
            'part_events': {},
            'vertical_events': []
        }

        if filename is not None:
            file_path = os.sep.join(folders + [filename])
            if os.path.realpath('.').find('code') != -1:
                file_path.replace('code', '')
                file_path = os.sep.join(['..', file_path])

            self.music = converter.parse(file_path)
            self.music_parts = self.music.parts

    def parse(self, parts=True, vertical=True):
        """
        Parse music
        """
        if parts:
            self.music_parts = self.music.voicesToParts()
            self.music_parts.flattenUnnecessaryVoices(inPlace=True)

            for i, part in enumerate(self.music_parts):
                if part.isSequence():
                    self.music_events['part_events'][i] = self.parse_sequence_part(
                        part, name=str(i), first=(False, True)[i == 0])
                else:
                    self.process_voiced_part(part, i)

        if vertical and len(self.music.getOverlaps()) > 0 and len(self.music_parts) > 1:
            print('Processing Vertical Events')
            self.music_events['vertical_events'] = VerticalParser(
                self.music).parse_music()
            print('End of Processing {} Vertical Events'.format(
                len(self.music_events['vertical_events'])))

    def parse_sequence_part(self, part, name=None, first=False, verbose=True):
        """
        Parse sequence
        """
        if name is None:
            name = part.partName

        if verbose:
            print('Processing part {}'.format(name))

        parser = LineParser(part)
        parsed = parser.parse_line()

        if not first and not utils.has_value_viewpoint_events(parsed, 'metronome'):
            parser.metronome_marks_parsing(self.music_parts[0], parsed)

        if verbose:
            print('End of Processing part {}'.format(name))

        return parsed

    def process_voiced_part(self, part, i):
        """
        Process a part that has overlappings
        """
        part.makeVoices(inPlace=True, fillGaps=True)
        for j, voice in enumerate(part.voices):
            self.music_events['part_events'][i] = {}
            if not voice.isSequence():
                voice.makeVoices(inPlace=True)
                self.music_events['part_events'][i][j] = {}
                for k, voc in voice.voices:
                    name = str(i) + ', voice ' + str(j) + \
                        ', internal voice ' + str(k)
                    self.music_events['part_events'][i][j][k] = self.parse_sequence_part(
                        voc, name=name, first=(False, True)[i == 0])
            else:
                name = str(i) + ', voice ' + str(j)
                self.music_events['part_events'][i][j] = self.parse_sequence_part(
                    voice, name=name, first=(False, True)[i == 0])

    def show_events(self, events='all parts', part_number=0, parts=[], viewpoints='all', offset=False):
        """
        Show sequence of events
        """
        if viewpoints == 'all':
            self.show_all_viewpoints(events, parts, part_number)
        else:
            _ = [self.show_single_viewpoints(
                viewpoint, events, part_number, parts, offset) for viewpoint in viewpoints]

    def show_all_viewpoints(self, events='all parts', parts=[], part_number=0):
        """
        Show all viewpoints
        """
        if events == 'one part':
            _ = [print(str(ev) + '\n')
                 for ev in self.music_events['part_events'][part_number]]
        elif events == 'some parts':
            for part in parts:
                print('Part ' + str(part))
                _ = [print(str(ev) + '\n')
                     for ev in self.music_events['part_events'][part]]
                print('')
            print('')
        if events in ('all parts', 'all'):
            for part, part_events in self.music_events['part_events'].items():
                print('Part ' + str(part))
                _ = [print(str(ev) + '\n') for ev in part_events]
                print('')
            print('')
        if events in ('vertical', 'all'):
            print('Vertical Events ')
            _ = [print(str(ev) + '\n')
                 for ev in self.music_events['vertical_events']]

    def show_single_viewpoints(self, viewpoint, events='all parts', part_number=0, parts=[], offset=False):
        """
        Shows only a viewpoint sequence
        """
        if events == 'one part':
            utils.show_part_viewpoint(
                viewpoint, self.music_events['part_events'][part_number], offset)
        elif events == 'some parts':
            for part in parts:
                print('Part ' + str(part))
                utils.show_part_viewpoint(
                    viewpoint, self.music_events['part_events'][part], offset)
                print('')
            print('')
        if events in ('all parts', 'all'):
            _ = [utils.show_part_viewpoint(viewpoint, part, offset)
                 for key, part in self.music_events['part_events'].items()]
        if events in ('vertical', 'all'):
            utils.show_part_viewpoint(
                viewpoint, self.music_events['vertical_events'], offset)

    def get_part_events(self):
        """
        Returns the parts events
        """
        return self.music_events['part_events']

    def get_vertical_events(self):
        """
        Returns the vertical events
        """
        return self.music_events['vertical_events']

    def to_json(self, filename, folders=['data', 'myexamples'], indent=2):
        """
        Parses Music To json object
        """
        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        to_dump = {
            'part_events': {},
            'vertical_events': [
                dict(event) for event in self.music_events['vertical_events']]
        }

        for num, part in self.music_events['part_events'].items():
            to_dump['part_events'][num] = [dict(event) for event in part]

        with open(file_path + '.json', 'w') as handle:
            json.dump(to_dump, handle, indent = indent)
            handle.close()

    def from_json(self, filename, folders=['data', 'myexamples']):
        """
        Parses Music from json object
        """
        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        with open(file_path + '.json', 'rb') as handle:
            to_load = json.load(handle)
            print(to_load['vertical_events'])
            self.music_events['vertical_events'] = [
                VerticalEvent(from_dict=event) for event in to_load['vertical_events']]
            for key, part in to_load['part_events'].items():
                self.music_events['part_events'][int(key)] = [
                    LinearEvent(from_dict=event) for event in part]
            handle.close()

    def to_pickle(self, filename, folders=['data', 'myexamples']):
        """
        Parses Music To cpickle object
        """
        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])
        
        # .pbz2 is even better for compression than pickle
        with bz2.BZ2File(file_path + '.pbz2', 'wb') as handle: 
            pickle.dump(self.music_events, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
            handle.close()

    def from_pickle(self, filename, folders=['data', 'myexamples']):
        """
        Parses Music To cpickle object
        """
        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        with bz2.BZ2File(file_path + '.pbz2', 'rb') as handle:
            self.music_events = pickle.load(handle)
            handle.close()
