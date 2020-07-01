#!/usr/bin/env python3.7
"""
This script presents the class LineParser that processes the vertical relations of various lines
"""
from collections import defaultdict

import music21

import application.representation.parsers.utils as utils
from application.representation.events.vertical_event import VerticalEvent


class VerticalParser:
    """
    Class VerticalParser
    """

    def __init__(self, music_to_parse):
        print('Chordifying music...')
        self.music_to_parse = music_to_parse.chordify(toSoundingPitch=True)
        self.events = []

        self.metadata = {
            'composer': music_to_parse.metadata.composer,
            'piece_title': music_to_parse.metadata.title
        }

        self.keys = defaultdict(list)
        for k, val in list((key.offset, key) for key in music_to_parse.flat.getElementsByClass(
                music21.key.KeySignature)):
            self.keys[k].append(val)

        key_analysis = music21.analysis.floatingKey.KeyAnalyzer(music_to_parse)
        self.measure_keys = key_analysis.getRawKeyByMeasure()

        key_offsets = list(self.keys) + [self.music_to_parse.highestTime]
        self.ks_keys = dict([utils.get_analysis_keys_stream_bet_offsets(
            self.music_to_parse, offset, key_offsets[key+1])
                             for key, offset in enumerate(key_offsets[:-1])])

    def parse_music(self):
        """
        Returns the events from vertical relations between parts
        """
        print('Parsing chords')
        chords = self.music_to_parse.flat.getElementsByClass(['Chord', 'Rest'])
        for i, chord in enumerate(chords):
            self.events.append(VerticalEvent(chord.offset))

            # Metadata
            for key, value in self.metadata.items():
                self.events[i].add_viewpoint(key, value)

            self.extract_duration(i, chord)
            if not isinstance(chord, music21.note.Rest):
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

        try:
            self.events[index].add_viewpoint(
                'duration.length', chord.duration.quarterLength)
            self.events[index].add_viewpoint(
                'duration.type', chord.duration.type)
            self.events[index].add_viewpoint(
                'dots', chord.duration.dots)
        except music21.duration.DurationException:
            print("Can't return duration types smaller than 2048th")
            self.events[index].add_viewpoint(
                'duration.length', 1/1120)
            self.events[index].add_viewpoint(
                'duration.type', '2048th')
            self.events[index].add_viewpoint(
                'dots', 0)

        if chord.tie is not None:
            self.events[index].add_viewpoint('type', chord.tie.type, 'tie')
            self.events[index].add_viewpoint(
                'style', chord.tie.style, 'tie')

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
            'pitchClass', chord.pitchClasses)
        self.events[index].add_viewpoint(
            'primeForm', chord.primeForm)
        self.events[index].add_viewpoint(
            'pcOrdered', chord.orderedPitchClasses)

    def chord_info(self, index, chord):
        """
        Processes the information for a chord
        """
        self.events[index].add_viewpoint(
            'pitches', [p.ps for p in chord.pitches])
        self.events[index].add_viewpoint(
            'basic.quality', chord.quality)
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

        return k_offset, key

    def key_signatures_parsing(self, index, chord):
        """
        Parses the existent key signatures information
        """
        k_offset, nearest_key_sign = self.get_key_sign_at_offset(
            self.events[index].get_offset())
        self.events[index].add_viewpoint(
            'key.keysig', nearest_key_sign.sharps)

        self.events[index].add_viewpoint(
            'signatures.key', str(self.ks_keys[k_offset]))
        self.events[index].add_viewpoint(
            'signatures.certainty', self.ks_keys[k_offset].tonalCertainty())
        harm_f_ks = utils.harmonic_functions_key(
            chord, self.ks_keys[k_offset])
        self.events[index].add_viewpoint(
            'signatures.function', harm_f_ks.figure)

    def perceived_key_at_measure_parsing(self, index, chord):
        """
        Parses the perceived key at measure information
        """
        measure_key = self.measure_keys[chord.measureNumber-1]
        if measure_key is not None:
            self.events[index].add_viewpoint(
                'measure.key', str(measure_key))
            self.events[index].add_viewpoint(
                'measure.certainty', measure_key.tonalCertainty())
            harm_f_ms = utils.harmonic_functions_key(chord, measure_key)
            self.events[index].add_viewpoint(
                'measure.function', harm_f_ms.figure)
