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
            'duration': {
                'length': 1,
                'type': 'quarter',
                'dots': 0,
            },
            'tie': {
                'type': 'no tie',
                'style': 'normal',
            },
            'quality': {
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
            },
            'basic': {
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
            },
            'key': {
                'keysig': 0,
                'signatures': {
                    'key': 'C major',
                    'certainty': 0,
                    'function': 'I',
                },
                'measure': {
                    'key': 'C major',
                    'certainty': 0,
                    'function': 'I',
                },
            },
        }
        
        self.viewpoints = dict(list(default.items()) + list(self.viewpoints.items()))
        self._init_from_list_or_dict(offset, from_dict, from_list, features)

