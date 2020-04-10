#!/usr/bin/env python3.7
"""
This script presents the class Parser that tries different approaches to segment a melodic line
"""

import os

from music21 import converter

import representation.utils as utils
from representation.line_parser import LineParser
from representation.vertical_parser import VerticalParser


class Parser:
    """
    A class used to parse a musical file.

    Attributes
    ----------
    """

    def __init__(self, filename):
        file_path = os.sep.join(['data', 'myexamples', filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        self.music = converter.parse(file_path)
        self.music_parts = self.music.parts
        self.part_events = {}
        self.vertical_events = []

    def parse(self, parts=True, vertical=True):
        """
        Parse music
        """
        if parts:
            self.music_parts = self.music.voicesToParts()
            self.music_parts.flattenUnnecessaryVoices(inPlace=True)

            for i, part in enumerate(self.music_parts):
                if part.isSequence():
                    self.part_events[i] = self.parse_sequence_part(
                        part, name=str(i), first=(False, True)[i == 0])
                else:
                    self.process_voiced_part(part, i)

        if vertical and len(self.music.getOverlaps()) > 0 and len(self.music_parts) > 1:
            print('Processing Vertical Events')
            self.vertical_events = VerticalParser(self.music).parse_music()
            print('End of Processing {} Vertical Events'.format(
                len(self.vertical_events)))

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
            self.part_events[i] = {}
            if not voice.isSequence():
                voice.makeVoices(inPlace=True)
                self.part_events[i][j] = {}
                for k, voc in voice.voices:
                    name = str(i) + ', voice ' + str(j) + \
                        ', internal voice ' + str(k)
                    self.part_events[i][j][k] = self.parse_sequence_part(
                        voc, name=name, first=(False, True)[i == 0])
            else:
                name = str(i) + ', voice ' + str(j)
                self.part_events[i][j] = self.parse_sequence_part(
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
            _ = [print(str(ev)) for ev in self.part_events[part_number]]
        elif events == 'some parts':
            for part in parts:
                print('Part ' + str(part))
                _ = [print(str(ev)) for ev in self.part_events[part]]
                print('')
            print('')
        if events in ('all parts', 'all'):
            for part, part_events in self.part_events.items():
                print('Part ' + str(part))
                _ = [print(str(ev)) for ev in part_events]
                print('')
            print('')
        if events in ('vertical', 'all'):
            print('Vertical Events ')
            _ = [print(str(ev)) for ev in self.vertical_events]

    def show_single_viewpoints(self, viewpoint, events='all parts', part_number=0, parts=[], offset=False):
        """
        Shows only a viewpoint sequence
        """
        if events == 'one part':
            utils.show_part_viewpoint(
                viewpoint, self.part_events[part_number], offset)
        elif events == 'some parts':
            for part in parts:
                print('Part ' + str(part))
                utils.show_part_viewpoint(
                    viewpoint, self.part_events[part], offset)
                print('')
            print('')
        if events in ('all parts', 'all'):
            _ = [utils.show_part_viewpoint(viewpoint, part, offset)
                 for key, part in self.part_events.items()]
        if events in ('vertical', 'all'):
            utils.show_part_viewpoint(viewpoint, self.vertical_events, offset)

    def get_part_events(self):
        """
        Returns the parts events
        """
        return self.part_events

    def get_vertical_events(self):
        """
        Returns the vertical events
        """
        return self.vertical_events
