#!/usr/bin/env python3.7
"""
This script presents the class LineParser that processes the vertical relations of various lines
"""

import music21

import representation.utils as utils
from representation.event import Event
from representation.viewpoint import Viewpoint


class VerticalParser:
    """
    Class VerticalParser
    """

    def __init__(self, music_to_parse):
        self.music_to_parse = music_to_parse.chordify()
        self.events = []

    def parse_music(self):
        """
        Returns the events from vertical relations between parts
        """
        # self.music_to_parse.show('text')
        chords = self.music_to_parse.flat.getElementsByClass('Chord')
        for i, chord in enumerate(chords):
            self.events.append(Event(chord.offset))

            # self.extract_
            self.extract_duration(i, chord)
            self.extract_chord_table_info(i, chord)
            self.pitch_class_info(i, chord)

        return self.events

    def extract_duration(self, index, chord):
        """
        Processes the duration information for a chord
        """
        self.events[index].add_viewpoint(
            Viewpoint('duration_length', chord.duration.quarterLength))
        self.events[index].add_viewpoint(
            Viewpoint('duration_type', chord.duration.type))
        self.events[index].add_viewpoint(
            Viewpoint('dots', chord.duration.dots))

    def extract_chord_table_info(self, index, chord):
        """
        Processes the table information information for a chord
        """
        self.events[index].add_viewpoint(
            Viewpoint('cardinality', chord.chordTablesAddress.cardinality))
        self.events[index].add_viewpoint(
            Viewpoint('forteClass', chord.forteClass))
        self.events[index].add_viewpoint(
            Viewpoint('forteClassNumber', chord.chordTablesAddress.forteClass))
        self.events[index].add_viewpoint(
            Viewpoint('inversion', chord.chordTablesAddress.inversion))
        self.events[index].add_viewpoint(
            Viewpoint('pcOriginal', chord.chordTablesAddress.pcOriginal))

    def pitch_class_info(self, index, chord):
        """
        Processes the pitch class information information for a chord
        """
        self.events[index].add_viewpoint(
            Viewpoint('pc_cardinality', chord.pitchClassCardinality))
        self.events[index].add_viewpoint(
            Viewpoint('pitch_class', chord.pitchClasses))
