#!/usr/bin/env python3.7
"""
This script presents the class LineParser that processes the vertical relations of various lines
"""
from collections import defaultdict

import music21

import representation.utils as utils
from representation.events.vertical_event import VerticalEvent


class VerticalParser:
    """
    Class VerticalParser
    """

    def __init__(self, music_to_parse):
        self.music_to_parse = music_to_parse.chordify()
        self.events = []

        self.keys = defaultdict(list)
        for k, val in list((key.offset, key) for key in music_to_parse.flat.getElementsByClass(
                music21.key.KeySignature)):
            self.keys[k].append(val)

        ka = music21.analysis.floatingKey.KeyAnalyzer(music_to_parse)
        self.measure_keys = ka.getRawKeyByMeasure()

        key_offsets = list(self.keys) + [self.music_to_parse.highestTime]
        self.ks_keys = dict(utils.get_analysis_keys_stream_bet_offsets(
            self.music_to_parse, offset, key_offsets[key+1])
            for key, offset in enumerate(key_offsets[:-1]))

    def parse_music(self):
        """
        Returns the events from vertical relations between parts
        """
        # self.music_to_parse.show('text')
        chords = self.music_to_parse.flat.getElementsByClass('Chord')
        for i, chord in enumerate(chords):
            self.events.append(VerticalEvent(chord.offset))

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
            'dur_length', chord.duration.quarterLength)
        self.events[index].add_viewpoint(
            'dur_type', chord.duration.type)
        self.events[index].add_viewpoint(
            'dots', chord.duration.dots)

        if chord.tie is not None:
            self.events[index].add_viewpoint('tie_type', chord.tie.type)
            self.events[index].add_viewpoint(
                'tie_style', chord.tie.style)

    def extract_chord_table_info(self, index, chord):
        """
        Processes the table information for a chord
        """
        self.events[index].add_viewpoint(
            'cardinality', chord.chordTablesAddress.cardinality)
        self.events[index].add_viewpoint(
            'forteClass', chord.forteClass)
        self.events[index].add_viewpoint(
            'forteClassNumber', chord.chordTablesAddress.forteClass)
        self.events[index].add_viewpoint(
            'inversion', chord.chordTablesAddress.inversion)

    def pitch_class_info(self, index, chord):
        """
        Processes the pitch class information for a chord
        """
        self.events[index].add_viewpoint(
            'pc_cardinality', chord.pitchClassCardinality)
        self.events[index].add_viewpoint(
            'pitch_class', chord.pitchClasses)
        self.events[index].add_viewpoint(
            'prime_form', chord.primeForm)
        self.events[index].add_viewpoint(
            'pc_original', chord.chordTablesAddress.pcOriginal)

    def chord_info(self, index, chord):
        """
        Processes the information for a chord
        """
        self.events[index].add_viewpoint(
            'pitches', [p.ps for p in chord.pitches])
        self.events[index].add_viewpoint(
            'quality', chord.quality)
        # self.events[index].add_viewpoint(
        #   'scale_degrees', chord.scaleDegrees)
        self.events[index].add_viewpoint(
            'root', chord.root().ps)

    def chord_elements_info(self, index, chord):
        """
        Processes the information for the elements of a chord
        """
        self.events[index].add_viewpoint(
            'is_consonant', chord.isConsonant())
        self.events[index].add_viewpoint(
            'is_major_triad', chord.isMajorTriad())
        self.events[index].add_viewpoint(
            'is_incomplete_major_triad', chord.isIncompleteMajorTriad())
        self.events[index].add_viewpoint(
            'is_minor_triad', chord.isMinorTriad())
        self.events[index].add_viewpoint(
            'is_incomplete_minor_triad', chord.isIncompleteMinorTriad())
        self.events[index].add_viewpoint(
            'is_augmented_sixth', chord.isAugmentedSixth())
        self.events[index].add_viewpoint(
            'is_french_augmented_sixth', chord.isFrenchAugmentedSixth())
        self.events[index].add_viewpoint(
            'is_german_augmented_sixth', chord.isGermanAugmentedSixth())
        self.events[index].add_viewpoint(
            'is_italian_augmented_sixth', chord.isItalianAugmentedSixth())
        self.events[index].add_viewpoint(
            'is_swiss_augmented_sixth', chord.isItalianAugmentedSixth())
        self.events[index].add_viewpoint(
            'is_augmented_triad', chord.isAugmentedTriad())
        self.events[index].add_viewpoint(
            'is_half_diminished_seventh', chord.isHalfDiminishedSeventh())
        self.events[index].add_viewpoint(
            'is_diminished_seventh', chord.isDiminishedSeventh())
        self.events[index].add_viewpoint(
            'is_dominant_seventh', chord.isDominantSeventh())

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
        _ = [uniq_keys_off.append(key) for key in self.keys[k_offset]
             if key not in uniq_keys_off]

        key = music21.key.KeySignature()
        if len(uniq_keys_off) > 0:
            key = uniq_keys_off[0]

        return key

    def key_signatures_parsing(self, index, chord):
        """
        Parses the existent key signatures information
        """
        nearest_key_sign = self.get_key_sign_at_offset(
            self.events[index].get_offset())
        self.events[index].add_viewpoint(
            'keysign', nearest_key_sign.sharps)
        self.events[index].add_viewpoint(
            'key_ks', str(self.ks_keys[nearest_key_sign.offset]))
        self.events[index].add_viewpoint(
            'key_ks_TC', self.ks_keys[nearest_key_sign.offset].tonalCertainty())
        harm_f_ks = utils.harmonic_functions_key(
            chord, self.ks_keys[nearest_key_sign.offset])
        self.events[index].add_viewpoint(
            'harmfunc_ks', harm_f_ks.figure)

    def perceived_key_at_measure_parsing(self, index, chord):
        """
        Parses the perceived key at measure information
        """
        measure_key = self.measure_keys[chord.measureNumber-1]
        if measure_key is not None:
            self.events[index].add_viewpoint(
                'key_ms', str(measure_key))
            self.events[index].add_viewpoint(
                'key_ms_TC', measure_key.tonalCertainty())
            harm_f_ms = utils.harmonic_functions_key(chord, measure_key)
            self.events[index].add_viewpoint(
                'harmfunc_ms', harm_f_ms.figure)
