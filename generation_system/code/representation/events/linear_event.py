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
                'instrument': '',
            },
            'basic': {
                'rest': False,
                'grace': False,
                'chord': False
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
            },
            'pitch': {
                'cpitch': 60.0,
                'dnote': 'C',  # DNOTES dict values
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

    def from_feature_list(self, from_list, features):
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
            elif from_list[i] == 10000.0:
                if 'instrument' in feat:
                    self.add_viewpoint('instrument', music21.instrument.Instrument(), category)
                else:
                    self.add_viewpoint(feat, None, category)
            elif feat in ['rest', 'grace', 'chord', 'exists_before', 'is_end', 'double', 'fib']:
                self.add_viewpoint(feat, bool(from_list[i]), category)
            elif any(val in feat for val in ['articulation', 'expression', 'ornamentation', 'dynamic', 'chordPitches']):
                if from_list[i] == 1.0:
                    self.add_viewpoint(feat.split('_')[0], feat.split('_')[1:], category)
            elif '=' in feat:
                if from_list[i] == 1.0:
                    info = feat.split('=')
                    if info[0] == 'instrument' and  info[1] != ': ':
                        if 'Instrument' in info[1]:
                            info[1] = 'Instrument'
                        elif info[1] in ['Brass', 'Woodwind', 'Keyboard', 'String']:
                            info[1] += 'Instrument'
                        try:
                            info[1] = getattr(music21.instrument, info[1])()
                        except AttributeError:
                            print('Wrong Instrument: ' + info[1])
                            try:
                                info[1] = music21.instrument.fromString(info[1])
                            except music21.exceptions21.InstrumentException:
                                print("Can't convert from this instrument: " + info[1])
                                info[1] = music21.instrument.Instrument()

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
        if features is None:
            features = ['.'.join(path.split('.')[-2:])
                        for path in utils.get_all_inner_keys(self.viewpoints)]

        features_dict = {}
        if offset:
            features_dict['offset'] = self.offset_time

        for feat in features:
            category = None
            real_feat = feat
            if '.' in feat:
                category = feat.split('.')[0]
                real_feat = feat.split('.')[1]

            # add features that are arrays
            if real_feat in ['articulation', 'expression', 'ornamentation', 'dynamic', 'chordPitches']:
                for a_feat in enumerate(self.get_viewpoint(real_feat, category)):
                    if isinstance(a_feat, tuple):
                        a_feat = a_feat[1]
                    features_dict[real_feat + '_' + a_feat] = True
            elif real_feat == 'dnote':
                features_dict[feat] = utils.convert_note_name(
                    self.get_viewpoint(real_feat, category))
            elif real_feat == 'instrument':
                features_dict[feat] = self.get_viewpoint(real_feat, category).instrumentName
            else:
                features_dict[feat] = self.get_viewpoint(real_feat, category)
        return features_dict
