#!/usr/bin/env python3.7
"""
This script presents the class VerticalEvent that represents a vertical (harmonic) event in a piece of music
"""
from representation.events.event import Event

class VerticalEvent(Event):
    """
    Class VerticalEvent
    """
    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        super().__init__(offset, from_dict, from_list, features)

        default = {
            'dur_length': 1,
            'dur_type': 'quarter',
            'dots': 0,
            'tied': '',
            'cardinality': 0,
            'forteClass': '',
            'forteClassNumber': 0,
            'inversion': '',
            'pc_cardinality': 0,
            'pitch_class': '',
            'prime_form': '',
            'pc_original': '',
            'pitches': [],
            'quality': '',
            'root': '',
            'is_consonant': False,
            'is_major_triad': False,
            'is_incomplete_major_triad': False,
            'is_minor_triad': False,
            'is_incomplete_minor_triad': False,
            'is_augmented_sixth': False,
            'is_french_augmented_sixth': False,
            'is_german_augmented_sixth': False,
            'is_italian_augmented_sixth': False,
            'is_swiss_augmented_sixth': False,
            'is_augmented_triad': False,
            'is_half_diminished_seventh': False,
            'is_diminished_seventh': False,
            'is_dominant_seventh': False,
            'keysign': 0,
            'key_ks': 'C major',
            'key_ks_TC': 0,
            'harmfunc_ks': 'I',
            'key_ms': 'C major',
            'key_ms_TC': 0,
            'harmfunc_ms': 'I',
        }
        
        self.viewpoints = dict(list(default.items()) + list(self.viewpoints.items()))
