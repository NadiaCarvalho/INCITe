#!/usr/bin/env python3.7
"""
This script presents the class LinearEvent that represents a linear (melodic) event in a piece of music
"""
import music21

from representation.events.event import Event


class LinearEvent(Event):
    """
    Class LinearEvent
    """

    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        super().__init__(offset, from_dict, from_list, features)

        default = {
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
            'tie_type': 'no tie',
            'tie_style': '',
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

        self.viewpoints = dict(list(default.items()) +
                               list(self.viewpoints.items()))

    def is_grace_note(self):
        """
        Returns value of 'grace' viewpoint for event
        """
        return self.viewpoints['grace']

    def convert_note_name(self, dnote):
        """
        Converts note names to integers and backwards
        """
        dnotes = {
            'C': 0,
            'D': 1,
            'E': 2,
            'F': 3,
            'G': 4,
            'A': 5,
            'B': 6
        }
        if type(dnote) is type(''):
            return dnotes[dnote]
        note_number = int(list(dnotes.values()).index(dnote))
        return list(dnotes.keys())[note_number]

    def from_feature_list(self, from_list, features):
        """
        Transforms list of features in an event
        """
        for i, feat in enumerate(features):
            if feat == 'offset':
                self.offset_time = from_list[i]
            elif from_list[i] == 1000:
                self.viewpoints[feat] = None
            elif feat in ['rest', 'is_grace', 'repeat_after', 'repeat_before', 'double_bar_before', 'fib']:
                self.viewpoints[feat] = bool(from_list[i])
            elif feat in ['articulation', 'expression', 'ornamentation', 'dynamic']:
                self.viewpoints[feat] = from_list[i].split('_')
            elif '=' in feat:
                if from_list[i] == 1.0:
                    info = feat.split('=')
                    self.viewpoints[info[0]] = info[1]
            elif feat == 'dnote':
                self.viewpoints[feat] = self.convert_note_name(from_list[i])
            else:
                self.viewpoints[feat] = from_list[i]

    def to_feature_dict(self, features=None, offset=True):
        """
        Transforms event in a dict of features
        """
        if features is None:
            features = list(self.viewpoints)
        
        features_dict = {}
        if offset:
            features_dict['offset'] = self.offset_time

        for feat in features:
            # add features that are arrays
            if feat in ['articulation', 'expression', 'ornamentation', 'dynamic']:
                for a_feat in enumerate(self.viewpoints[feat]):
                    features_dict[feat + '_' + a_feat] = True
            elif feat == 'dnote':
                features_dict[feat] = self.convert_note_name(
                    self.get_viewpoint(feat))
            else:
                features_dict[feat] = self.get_viewpoint(feat)
        return features_dict
