#!/usr/bin/env python3.7
"""
This script presents the class VerticalEvent that represents a vertical (harmonic) event in a piece of music
"""
import representation.events.utils as utils
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
            'basic': {
                'root': '',
                'pitches': [],
                'cardinality': 0,
                'inversion': '',
                'prime_form': '',
                'quality': '',
            },
            'classes': {
                'pc_ordered': '',
                'pc_cardinality': 0,
                'pitch_class': '',
                'forte_class': '',
                'forte_class_number': 0,
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

        self.viewpoints = dict(list(default.items()) +
                               list(self.viewpoints.items()))
        self._init_from_list_or_dict(offset, from_dict, from_list, features)

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
            if real_feat in ['pitches', 'pitch_class', 'prime_form', 'pc_ordered']:
                for a_feat in enumerate(self.get_viewpoint(real_feat, category)):
                    if isinstance(a_feat, tuple):
                        a_feat = a_feat[1]
                    features_dict[real_feat + '_' + str(a_feat)] = True
            else:
                features_dict[feat] = self.get_viewpoint(real_feat, category)
        return features_dict
