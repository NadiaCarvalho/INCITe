#!/usr/bin/env python3.7
"""
This script presents the class LineParser that processes the vertical relations of various lines
"""
from collections import defaultdict

import music21
import numpy as np

#import representation.utils as utils
from representation.event import Event
from representation.viewpoint import Viewpoint


class VerticalParser:
    """
    Class VerticalParser
    """

    def __init__(self, music_to_parse):
        self.music_to_parse = music_to_parse.chordify()
        self.events = []

        self.keys = defaultdict(list)
        for k, v in list((key.offset, key) for key in music_to_parse.flat.getElementsByClass(
                music21.key.KeySignature)):
            self.keys[k].append(v)

        measures = self.music_to_parse.getElementsByClass('Measure')
        self.measure_keys = dict(self.get_analysis_keys_measure(
            measure) for measure in measures)

        key_offsets = list(self.keys) + [self.music_to_parse.highestTime]
        self.ks_keys = dict(self.get_analysis_keys_stream_bet_offsets(
            offset, key_offsets[key+1]) for key, offset in enumerate(key_offsets[:-1]))

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
            self.chord_info(i, chord)
            self.chord_elements_info(i, chord)
            self.key_signatures_parsing(i, chord)
            self.perceived_key_at_measure_parsing(i, chord)

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
        self.events[index].add_viewpoint(
            Viewpoint('tied', chord.tie))

    def extract_chord_table_info(self, index, chord):
        """
        Processes the table information for a chord
        """
        self.events[index].add_viewpoint(
            Viewpoint('cardinality', chord.chordTablesAddress.cardinality))
        self.events[index].add_viewpoint(
            Viewpoint('forteClass', chord.forteClass))
        self.events[index].add_viewpoint(
            Viewpoint('forteClassNumber', chord.chordTablesAddress.forteClass))
        self.events[index].add_viewpoint(
            Viewpoint('inversion', chord.chordTablesAddress.inversion))

    def pitch_class_info(self, index, chord):
        """
        Processes the pitch class information for a chord
        """
        self.events[index].add_viewpoint(
            Viewpoint('pc_cardinality', chord.pitchClassCardinality))
        self.events[index].add_viewpoint(
            Viewpoint('pitch_class', chord.pitchClasses))
        self.events[index].add_viewpoint(
            Viewpoint('prime_form', chord.primeForm))
        self.events[index].add_viewpoint(
            Viewpoint('pcOriginal', chord.chordTablesAddress.pcOriginal))

    def chord_info(self, index, chord):
        """
        Processes the information for a chord
        """
        self.events[index].add_viewpoint(
            Viewpoint('pitches', [p.ps for p in chord.pitches]))
        self.events[index].add_viewpoint(
            Viewpoint('quality', chord.quality))
        self.events[index].add_viewpoint(
            Viewpoint('scale_degrees', chord.scaleDegrees))
        self.events[index].add_viewpoint(
            Viewpoint('root', chord.root()))

    def chord_elements_info(self, index, chord):
        """
        Processes the information for the elements of a chord
        """
        self.events[index].add_viewpoint(
            Viewpoint('is_consonant', chord.isConsonant()))
        self.events[index].add_viewpoint(
            Viewpoint('is_major_triad', chord.isMajorTriad()))
        self.events[index].add_viewpoint(
            Viewpoint('is_incomplete_major_triad', chord.isIncompleteMajorTriad()))
        self.events[index].add_viewpoint(
            Viewpoint('is_minor_triad', chord.isMinorTriad()))
        self.events[index].add_viewpoint(
            Viewpoint('is_incomplete_minor_triad', chord.isIncompleteMinorTriad()))
        self.events[index].add_viewpoint(
            Viewpoint('is_augmented_sixth', chord.isAugmentedSixth()))
        self.events[index].add_viewpoint(
            Viewpoint('is_french_augmented_sixth', chord.isFrenchAugmentedSixth()))
        self.events[index].add_viewpoint(
            Viewpoint('is_german_augmented_sixth', chord.isGermanAugmentedSixth()))
        self.events[index].add_viewpoint(
            Viewpoint('is_italian_augmented_sixth', chord.isItalianAugmentedSixth()))
        self.events[index].add_viewpoint(
            Viewpoint('is_swiss_augmented_sixth', chord.isItalianAugmentedSixth()))
        self.events[index].add_viewpoint(
            Viewpoint('is_augmented_triad', chord.isAugmentedTriad()))
        self.events[index].add_viewpoint(
            Viewpoint('is_half_diminished_seventh', chord.isHalfDiminishedSeventh()))
        self.events[index].add_viewpoint(
            Viewpoint('is_diminished_seventh', chord.isDiminishedSeventh()))
        self.events[index].add_viewpoint(
            Viewpoint('is_dominant_seventh', chord.isDominantSeventh()))

    def get_key_sign_at_offset(self, offset):
        """
        Returns key signature at offset
        """
        key_offsets = list(self.keys)
        index = key_offsets.index(
            min(key_offsets, key=lambda x: abs(offset - x)))
        k_offset = key_offsets[(index, index-1)
                               [bool(offset < key_offsets[index])]]

        uniq_keys_off = []
        [uniq_keys_off.append(key) for key in self.keys[k_offset]
         if key not in uniq_keys_off]

        if len(uniq_keys_off) == 1:
            key = uniq_keys_off[0]

        return key

    def harmonic_functions_key(self, chord, key):
        """
        Parses the harmonic key signatures information for a key
        """
        return music21.roman.romanNumeralFromChord(chord, key)

    def key_signatures_parsing(self, index, chord):
        """
        Parses the existent key signatures information
        """
        nearest_key_sign = self.get_key_sign_at_offset(
            self.events[index].get_offset())
        self.events[index].add_viewpoint(
            Viewpoint('keysign', nearest_key_sign))
        self.events[index].add_viewpoint(
            Viewpoint('keyKS', self.ks_keys[nearest_key_sign.offset]))
        harm_f_ks = self.harmonic_functions_key(
            chord, self.ks_keys[nearest_key_sign.offset])
        self.events[index].add_viewpoint(
            Viewpoint('harmfuncKS', harm_f_ks))

    def perceived_key_at_measure_parsing(self, index, chord):
        """
        Parses the perceived key at measure information
        """
        measure_key = self.measure_keys[chord.measureNumber]
        self.events[index].add_viewpoint(
            Viewpoint('keyMS', measure_key))
        harm_f_ms = self.harmonic_functions_key(chord, measure_key)
        self.events[index].add_viewpoint(
            Viewpoint('harmfuncMS', harm_f_ms))

    def get_analysis_keys_measure(self, measure):
        """
        Gets an analysis of key for a measure
        """
        k = measure.analyze('key')
        return (measure.number, k)

    def get_analysis_keys_stream_bet_offsets(self, off1, off2):
        """
        Gets an analysis of key for a stream
        """
        k = self.music_to_parse.getElementsByOffset(
            off1, off2).stream().analyze('key')
        return (off1, k)
