#!/usr/bin/env python3.7
"""
This script presents the class LinearEvent
that represents a linear (melodic) event in a piece of music
"""
from fractions import Fraction

import music21

import  application.representation.events.utils as utils
from application.representation.events.event import Event

ARRAY_VALUES = ['articulation', 'expression',
                'ornamentation', 'dynamic', 'chordPitches']

BOOL_VALUES = ['rest', 'grace', 'chord',
               'exists_before', 'is_end', 'double', 'fib', 'anacrusis']


class LinearEvent(Event):
    """
    Class LinearEvent
    """

    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        super().__init__(offset, from_dict, from_list, features)

        default = {
            'metadata': {
                'part': '',
                'voice': '',
                'piece_title': '',
                'composer': '',
                'instrument': '',
            },
            'basic': {
                'rest': False,
                'grace': False,
                'chord': False,
                'bioi': 0,
            },
            'duration': {
                'length': 1,
                'type': 'quarter',
                'dots': 0,
                'slash': False,
            },
            'expressions': {
                'articulation': [],
                'breath_mark': False,
                'dynamic': [],
                'fermata': False,
                'expression': [],
                'ornamentation': [],
                'rehearsal': False,
                'volume': 100,
                'notehead': {
                    'type': 'normal',
                    'fill': True,
                    'parenthesis': False,
                },
                'tie': {
                    'type': 'no tie',
                    'style': 'normal',
                },
                'slur': {
                    'begin': False,
                    'end': False,
                    'between': False,
                },
                'clef': str(music21.clef.TrebleClef().sign) + str(music21.clef.TrebleClef().line),
            },
            'pitch': {
                'cpitch': None,
                'dnote': None,  # DNOTES dict values
                'octave': 4,
                'accidental': music21.pitch.Accidental('natural').modifier,
                'microtonal': 0.0,
                'pitch_class': 0,
                'chordPitches': [],
            },
            'key': {
                'keysig': 0,
                'signatures': {
                    'key': 'C major',
                    'scale_degree': 0,
                },
                'measure': {
                    'key': 'C major',
                    'scale_degree': 0,
                },
            },
            'time': {
                'timesig': '4/4',
                'pulses': 4,
                'barlength': 4,
                'metro': {
                    'text': None,
                    'value': None,
                    'sound': 100,
                },
                'ref': {
                    'value': 1,
                    'type': 'quarter',
                },
                'barlines': {
                    'double': False,
                    'repeat': {
                        'exists_before': False,
                        'direction': 'end',
                        'is_end': False,
                    }
                },
            },
            'phrase': {
                'boundary': 0,
                'length': 0,
            },
            'derived': {
                'seq_int': 0,
                'contour': 0,
                'contour_hd': 0,
                'closure': 0,
                'registral_direction': False,
                'intervallic_difference': False,
                'upwards': False,
                'downwards': False,
                'no_movement': False,
                'fib': True,
                'posinbar': 0,
                'beat_strength': 0.0,
                'tactus': False,
                'intfib': 0,
                'thrbar': 0,
                'intphrase': 0,
                'anacrusis': False,
            },
        }
        self.viewpoints = dict(list(default.items()) +
                               list(self.viewpoints.items()))
        self._init_from_list_or_dict(offset, from_dict, from_list, features)

    def is_grace_note(self):
        """
        Returns value of 'grace' viewpoint for event
        """
        return self.get_viewpoint('grace')

    def is_chord(self):
        """
        Returns value of 'chord' viewpoint for event
        """
        return self.get_viewpoint('chord')

    def not_rest_or_grace(self):
        """
        Returns True/False if is not rest or grace note
        """
        return not (self.is_grace_note() or self.is_rest())

    def from_feature_list(self, from_list, features, nan_value=10000):
        """
        Transforms list of features in an event
        """
        for i, feat in enumerate(features):
            category = None
            if '.' in feat:
                category = feat.split('.')[0]
                feat = feat.split('.')[1]

            if feat == 'offset':
                self.offset_time = from_list[i]
            elif from_list[i] == nan_value:
                self.add_viewpoint(feat, None, category)
            elif feat in BOOL_VALUES:
                self.add_viewpoint(feat, bool(from_list[i]), category)
            elif any(val in feat for val in ARRAY_VALUES) and from_list[i] == 1.0:
                self.add_viewpoint(feat.split(
                    '_')[0], feat.split('_')[1:], category)
            elif '=' in feat and from_list[i] == 1.0:
                info = feat.split('=')
                if info[0] == 'instrument' and info[1] != ': ':
                    info[1] = utils.instrument_converter(info[1])
                self.add_viewpoint(info[0], info[1], category)
            elif feat == 'dnote':
                self.add_viewpoint(
                    feat, utils.convert_note_name(from_list[i]), category)
            else:
                self.add_viewpoint(feat, from_list[i], category)

    def to_feature_dict(self, features=None, offset=True):
        """
        Transforms event in a dict of features
        """
        viewpoints_flat = utils.flatten_dict(self.viewpoints, sep='.')
        if features is None:
            features = viewpoints_flat.keys()

        features_dict = {}
        if offset:
            features_dict['offset'] = float(self.offset_time)

        for feat in features:
            content = None
            views = [v for v in viewpoints_flat if feat in v]
            if views != []:
                content = viewpoints_flat[views[0]]

            # add features that are arrays
            if isinstance(content, Fraction):
                features_dict[feat] = float(content)
            elif content is not None and any(s in ARRAY_VALUES for s in feat.split('.')):
                for a_feat in enumerate(content):
                    if isinstance(a_feat, tuple):
                        a_feat = a_feat[1]
                    features_dict[feat + '_' + a_feat] = True
            elif 'dnote' in feat:
                if content is None:
                    features_dict[feat] = None
                else:
                    features_dict[feat] = utils.convert_note_name(content)
            elif 'instrument' in feat:
                features_dict[feat] = content.instrumentName
            else:
                features_dict[feat] = content

        return features_dict
