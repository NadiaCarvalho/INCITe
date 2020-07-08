#!/usr/bin/env python3.7
"""
This script presents the class InterPartEvent
that represents a interpart (harmonic) event in a piece of music
"""
from fractions import Fraction

import  application.logic.representation.events.utils as utils
from application.logic.representation.events.event import Event

ARRAY_VALUES = ['pitches', 'pitchClass', 'primeForm', 'pcOrdered']


class InterPartEvent(Event):
    """
    Class InterPartEvent
    """

    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        super().__init__(offset, from_dict, from_list, features)

        default = {
            'metadata': {
                'composer': '',
                'piece_title': '',
            },
            'duration': {
                'length': 1,
                'type': 'quarter',
                'dots': 0,
                'tie': {
                    'type': 'no tie',
                    'style': 'normal',
                },
            },
            'basic': {
                'root': '',
                'pitches': [],
                'cardinality': 0,
                'inversion': '',
                'primeForm': '',
                'quality': '',
            },
            'classes': {
                'pcOrdered': '',
                'pc_cardinality': 0,
                'pitchClass': '',
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

            # add features that are arrays~
            if isinstance(content, Fraction):
                features_dict[feat] = float(content)
            elif (content is not None and
                    any(s in ARRAY_VALUES for s in feat.split('.'))):
                for a_feat in enumerate(content):
                    if isinstance(a_feat, tuple):
                        a_feat = a_feat[1]
                    features_dict[feat + '_' + str(a_feat)] = True
            else:
                features_dict[feat] = content
        return features_dict
