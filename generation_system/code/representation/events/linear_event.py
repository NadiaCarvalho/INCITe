#!/usr/bin/env python3.7
"""
This script presents the class LinearEvent that represents a linear (melodic) event in a piece of music
"""
import music21

import representation.events.utils as utils
from representation.events.event import Event


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
            },
            'basic': {
                'rest': False,
                'grace': False,
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
                },
            },
            'pitch': {
                'cpitch': 60.0,
                'dnote': 'C',  # DNOTES dict values
                'octave': 4,
                'accidental': music21.pitch.Accidental('natural').modifier,
                'microtonal': 0.0,
                'pitch_class': 0,
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

    def from_feature_list(self, from_list, features):
        """
        Transforms list of features in an event
        """
        for i, feat in enumerate(features):
            category = None
            if '.' in feat:
                feat = feat.split('.')[1]
                category = feat.split('.')[0]

            if feat == 'offset':
                self.offset_time = from_list[i]
            elif from_list[i] == 1000:
                self.add_viewpoint(feat, None, category)
            elif feat in ['rest', 'grace', 'exists_before', 'is_end', 'double', 'fib']:
                self.add_viewpoint(feat, bool(from_list[i]), category)
            elif feat in ['articulation', 'expression.other', 'ornamentation', 'dynamic']:
                self.add_viewpoint(feat, from_list[i].split('_'), category)
            elif '=' in feat:
                if from_list[i] == 1.0:
                    info = feat.split('=')
                    self.add_viewpoint(info[0], info[1], category)
            elif feat == 'dnote':
                self.add_viewpoint(
                    self.viewpoints[feat], utils.convert_note_name(from_list[i]), category)
            else:
                self.add_viewpoint(
                    self.viewpoints[feat], from_list[i], category)

    def to_feature_dict(self, features=None, offset=True):
        """
        Transforms event in a dict of features
        """
        if features is None:
            features = ['.'.join(path.split('.')[-2:])
                        for path in utils.get_all_inner_keys(self.viewpoints)]

        features_dict = {}
        if offset:
            features_dict['offset'] = self.offset_time

        for feat in features:
            category = None
            if '.' in feat:
                feat = feat.split('.')[1]
                category = feat.split('.')[0]

            # add features that are arrays
            if feat in ['articulation', 'expression.other', 'ornamentation', 'dynamic']:
                for a_feat in enumerate(self.get_viewpoint(feat, category)):
                    features_dict[feat + '_' + a_feat] = True
            elif feat == 'dnote':
                features_dict[feat] = utils.convert_note_name(
                    self.get_viewpoint(feat, category))
            else:
                features_dict[feat] = self.get_viewpoint(feat, category)
        return features_dict
