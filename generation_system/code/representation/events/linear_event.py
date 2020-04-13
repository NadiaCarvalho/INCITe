#!/usr/bin/env python3.7
"""
This script presents the class LinearEvent that represents a linear (melodic) event in a piece of music
"""
import music21

from representation.events.event import Event

DNOTES = {
    'C': 0,
    'D': 1,
    'E': 2,
    'F': 3,
    'G': 4,
    'A': 5,
    'B': 6
}


class LinearEvent(Event):
    """
    Class LinearEvent
    """

    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        super().__init__(offset, from_dict, from_list, features)
        if len(list(self.viewpoints)) == 0:
            self.viewpoints = {
                'part': '',
                'voice': '',
                'rest': False,
                'grace': False,
                'dur_length': 1,
                'dur_type': 'quarter',
                'dots': 0,
                'expression': [],
                'ornamentation': [],
                'fermata': False,
                'rehearsal': False,
                'pitch': 60.0,
                'dnote': 'C',  # DNOTES dict values
                'accidental': music21.pitch.Accidental('natural').modifier,
                'octave': 4,
                'microtonal': 0.0,
                'pitch_class': 0,
                'notehead': 'normal',
                'noteheadfill': True,
                'noteheadparenthesis': False,
                'articulation': [],
                'volume': 100,
                'tie': False,
                'seq_int': 0,
                'contour': 0,
                'contour_hd': 0,
                'fib': True,
                'intfib': 0,
                'thrbar': 0,
                'posinbar': 0,
                'beat_strength': 0.0,
                'dynamic': [],
                'keysig': 0,
                'key_ks': 'C major',
                'scale_degree_ks': 0,
                'key_ms': 'C major',
                'scale_degree_ms': 0,
                'timesig': '4/4',
                'metronome': 100,
                'metro_sound': 100,
                'metro_ref_value': 1,
                'metro_ref_type': 'quarter',
                'double_bar': False,
                'repeat_before': False,
                'repeat_direction': 'end',
                'end_repeat': False,
            }


    def is_grace_note(self):
        """
        Returns value of 'grace' viewpoint for event
        """
        return self.viewpoints['grace']
