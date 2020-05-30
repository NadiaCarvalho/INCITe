#!/usr/bin/env python3.7
"""
This script presents the class Parser that tries different approaches to segment a melodic line
"""

import bz2
import json
import os
import pickle

import music21

import representation.parsers.utils as utils
import representation.utils.printing as printing
import representation.utils.voice as voice_utils
from representation.events.linear_event import LinearEvent
from representation.events.vertical_event import VerticalEvent
from representation.parsers.line_parser import LineParser
from representation.parsers.vertical_parser import VerticalParser

FOLDER_DEFAULT = ['data', 'myexamples']
LINEAR_INSTRUMENTS = ['WoodwindInstrument', 'BrassInstrument', 'Vocalist']


class MusicParser:
    """
    A class used to parse a musical file.

    Attributes
    ----------
    """

    def __init__(self, filename=None, folders=None):

        if folders is None:
            folders = FOLDER_DEFAULT

        self.music = None
        self.music_parts = []

        self.music_events = {
            'part_events': {},
            'vertical_events': []
        }

        self.first_part = None

        if filename is not None:
            if not os.path.exists(filename):
                file_path = os.sep.join(folders + [filename])
                if os.path.realpath('.').find('code') != -1:
                    file_path.replace('code', '')
                    file_path = os.sep.join(['..', file_path])
            else:
                file_path = filename

            self.music = music21.converter.parse(file_path)
            if filename.endswith('.mid'):
                try:
                    self.music = music21.converter.parse(
                        file_path, makeNotation=False)
                    self.music.makeNotation(inPlace=True)
                    len(self.music.getElementsByClass('Measure'))

                    for part in self.music.parts:
                        part.makeNotation(inPlace=True)
                except music21.exceptions21.StreamException:
                    self.music.show()

            self.clean_hidden_music()

    def parse(self, parts=True, vertical=True, number_parts=None):
        """
        Parse music
        """
        if parts:
            self.music.makeVoices(inPlace=True)
            self.music.flattenUnnecessaryVoices(inPlace=True)
            if self.music.hasVoices():
                self.music = self.music.voicesToParts(separateById=True)

            self.music_parts = self.music.parts
            if number_parts is None or number_parts > len(self.music_parts):
                number_parts = len(self.music_parts)
            for i in range(number_parts):
                part = self.music_parts[i]

                instrument = utils.instrument_for_voices(
                    part.getInstrument().instrumentName)
                is_linear_instrument = any(val in instrument.classes for
                                           val in LINEAR_INSTRUMENTS)
                if (is_linear_instrument and
                        (len(part.recurse(classFilter='Chord')) > 0 or part.hasVoices())):
                    self.process_voiced_part_linear_instruments(
                        part, i, instrument)
                elif not part.isSequence() or part.hasVoices():
                    self.process_voiced_part(part, i, instrument)
                else:
                    self.music_events['part_events'][i] = self.parse_sequence_part(
                        part, name=str(instrument), first=(False, True)[i == 0])

        if vertical and (len(self.music.parts) > 1 or
                         len(self.music.getOverlaps()) > 0 or
                         len(self.music.recurse(classFilter='Chord')) > 0):
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

        parser = LineParser(part, self.music.metadata)
        parsed = parser.parse_line()

        first_metro_marks = list(
            self.music.parts[0].flat.metronomeMarkBoundaries())
        if not first and first_metro_marks != list(part.flat.metronomeMarkBoundaries()):
            parser.metronome_marks_parsing(first_metro_marks, parsed)

        if verbose:
            print('End of Processing part {}'.format(name))

        return parsed

    def process_voiced_part_linear_instruments(self, part, i, real_in):
        """
        Process a part that has overlappings
        """
        max_voice_count = voice_utils.get_number_voices(part)

        for measure in list(part.recurse(classFilter='Measure')):
            measure.flattenUnnecessaryVoices(inPlace=True)
            if measure.hasVoices():
                voice_utils.process_voiced_measure(measure, max_voice_count)
            else:
                voice_utils.make_voices(measure, in_place=True,
                                        number_voices=max_voice_count)

        #part.flattenUnnecessaryVoices(inPlace=True)
        new_parts = part.voicesToParts()
        for j, voice in enumerate(new_parts.parts):
            voice.append(real_in)
            index = str(real_in) + '.' + str(j)
            name = str(real_in) + ', voice ' + str(j)
            self.music_events['part_events'][index] = self.parse_sequence_part(
                voice, name=name, first=(False, True)[i == 0])

    def process_voiced_part(self, part, i, real_in):
        """
        Process a part that has voices: divide voices in new parts
        """
        part.recurse().flattenUnnecessaryVoices(inPlace=True, force=True)

        new_parts = part
        if len(part.recurse(classFilter='Voice')) > 0:
            try:
                new_parts = part.voicesToParts(separateById=True)
            except Exception:
                new_parts = part.voicesToParts(separateById=False)

        for j, voice in enumerate(new_parts.parts):
            voice.append(real_in)
            index = str(real_in) + '.' + str(j)
            name = str(real_in) + ', voice ' + str(j)
            self.music_events['part_events'][index] = self.parse_sequence_part(
                voice, name=name, first=(False, True)[i == 0])

    def clean_hidden_music(self):
        """
        Clean Hidden Elements From Score
        """
        for _elm in self.music.recurse():
            if not isinstance(_elm.style, str) and _elm.style.hideObjectOnPrint:
                self.music.remove(_elm, recurse=True)

    def show_events(self, events='all parts', part_number=0,
                    parts=None, viewpoints='all', offset=False):
        """
        Show sequence of events
        """
        if viewpoints == 'all':
            self.show_all_viewpoints(events, parts, part_number)
        else:
            _ = [self.show_single_viewpoints(
                viewpoint, events, part_number, parts, offset) for viewpoint in viewpoints]

    def show_all_viewpoints(self, events='all parts', parts=None, part_number=0):
        """
        Show all viewpoints
        """
        if events == 'one part':
            _ = [print(str(ev) + '\n')
                 for ev in self.music_events['part_events'][part_number]]
        elif events == 'some parts' and parts is not None:
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

    def show_single_viewpoints(self, viewpoint, events='all parts',
                               part_number=0, parts=None, offset=False):
        """
        Shows only a viewpoint sequence
        """
        if events == 'one part':
            printing.show_part_viewpoint(
                viewpoint, self.music_events['part_events'][part_number], offset)
        elif events == 'some parts':
            for part in parts:
                print('Part ' + str(part))
                printing.show_part_viewpoint(
                    viewpoint, self.music_events['part_events'][part], offset)
                print('')
            print('')
        if events in ('all parts', 'all'):
            _ = [printing.show_part_viewpoint(viewpoint, part, offset)
                 for key, part in self.music_events['part_events'].items()]
        if events in ('vertical', 'all'):
            printing.show_part_viewpoint(
                viewpoint, self.music_events['vertical_events'], offset)

    def get_part_events(self):
        """
        Returns the parts events
        """
        if 'part_events' in self.music_events:
            return self.music_events['part_events']
        return None

    def get_vertical_events(self):
        """
        Returns the vertical events
        """
        if 'vertical_events' in self.music_events:
            return self.music_events['vertical_events']
        return None

    def to_json(self, filename, folders=None, indent=2):
        """
        Parses Music To json object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        to_dump = {
            'part_events': {},
            'vertical_events': [
                event.to_feature_dict() for event in self.music_events['vertical_events']]
        }

        for key, part in self.music_events['part_events'].items():
            to_dump['part_events'][key] = [event.to_feature_dict() for event in part]

        with open(file_path + '.json', 'w') as handle:
            json.dump(to_dump, handle, indent=indent)
            handle.close()
        print('Dumped to json')

    def from_json(self, filename, folders=None):
        """
        Parses Music from json object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

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

    def to_pickle(self, filename, folders=None):
        """
        Parses Music To cpickle object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

        if not os.path.exists(os.sep.join(folders)):
            os.makedirs(os.sep.join(folders))

        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        # .pbz2 is even better for compression than pickle
        with bz2.BZ2File(file_path + '.pbz2', 'wb') as handle:
            pickle.dump(self.music_events, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
            handle.close()
        print('Dumped to pickle')

    def from_pickle(self, filename, folders=None):
        """
        Parses Music To cpickle object
        """
        if folders is None:
            folders = FOLDER_DEFAULT

        file_path = os.sep.join(folders + [filename])
        if os.path.realpath('.').find('code') != -1:
            file_path.replace('code', '')
            file_path = os.sep.join(['..', file_path])

        with bz2.BZ2File(file_path + '.pbz2', 'rb') as handle:
            self.music_events = pickle.load(handle)
            handle.close()
