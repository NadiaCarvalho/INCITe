#!/usr/bin/env python3.7
"""
This script presents the class Event that represents an event in a piece of music
"""

import representation.utils as utils


class Event:
    """
    Class Event
    """

    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        self.offset_time = offset
        self.viewpoints = {}
        self._init_from_list_or_dict(offset, from_dict, from_list, features)

    def _init_from_list_or_dict(self, offset=None, from_dict=None, from_list=None, features=None):
        if from_dict is not None:
            self.from_feature_dict(from_dict, features)
        elif (from_list is not None) and (features is not None):
            self.from_feature_list(from_list, features)

    def add_viewpoint(self, name, info):
        """
        Adds a viewpoint to event
        """
        if (name in self.viewpoints and
                isinstance(self.viewpoints[name], list)):
            self.viewpoints[name].append(info)
            self.viewpoints[name] = utils.flatten(self.viewpoints[name])
        else:
            self.viewpoints[name] = info

    def get_viewpoint(self, name):
        """
        Returns a viewpoint of event
        """
        if name in self.viewpoints:
            return self.viewpoints[name]
        return None

    def check_viewpoint(self, name):
        """
        Returns a viewpoint of event
        """
        return name in self.viewpoints

    def get_offset(self):
        """
        Returns offset value of event
        """
        return self.offset_time

    def is_rest(self):
        """
        Returns value of 'rest' viewpoint for event
        """
        return self.viewpoints['rest']

    def weighted_comparison(self, other, weights=None):
        """
        Defines an equal function for Event with weighted attributes
        Return a float in interval [0, 1] in which 0 means that the
        two events are totally non-equal and 1, totally equal.
        """
        if weights is None:
            return float(self == other)

        score = 0
        for key, weight in weights.items():
            if self.get_viewpoint(key) == other.get_viewpoint(key):
                score += weight

        return score/sum(weights.values())

    def to_feature_list(self, features=None):
        """
        Transforms event in a list of features
        """
        if features is None:
            features = list(self.viewpoints)

        features_list = [self.viewpoints[feat]
                         if feat in self.viewpoints else None for feat in features]

        return [self.offset_time] + features_list, features

    def from_feature_list(self, from_list, features, nan_value=1000):
        """
        Transforms list of features in an event
        """
        for i, feat in enumerate(features):
            if feat == 'offset':
                self.offset_time = from_list[i]
            elif from_list[i] == nan_value:
                self.viewpoints[feat] = None
            else:
                self.viewpoints[feat] = from_list[i]

    def to_feature_dict(self, features=None):
        """
        Transforms event in a dict of features
        """
        if features is None:
            features = list(self.viewpoints)

        features_dict = {}
        features_dict['offset'] = self.offset_time
        for feat in features:
            features_dict[feat] = self.get_viewpoint(feat)
        return features_dict

    def from_feature_dict(self, from_dict, features):
        """
        Transforms dict of features in an event
        """
        if features is None:
            features = list(from_dict)

        for feat in features:
            if feat == 'offset':
                self.offset_time = from_dict[feat]
            else:
                self.viewpoints[feat] = from_dict[feat]

    def __str__(self):
        """
        Overrides str function for Event
        """
        to_return = 'Event at offset {}: \n'.format(self.offset_time)
        to_return += ''.join([str(key) + ': ' + str(viewpoint) + '; '
                              for key, viewpoint in self.viewpoints.items()])
        return to_return

    def __iter__(self):
        yield('offset', self.offset_time)
        for key in self.viewpoints:
            if key == 'posinbar':
                yield(key, str(self.viewpoints[key]))
            else:    
                yield(key, self.viewpoints[key])

    def __eq__(self, other):
        """
        Overrides equal function for Event
        """
        for key, viewpoint in self.viewpoints.items():
            other_view = other.get_viewpoint(key)
            if other_view is None or viewpoint != other_view:
                return False
        return True

    def __ne__(self, other):
        """
        Overrides non-equal function for Event
        """
        return not self == other
