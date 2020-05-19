#!/usr/bin/env python3.7
"""
This script presents the class Event that represents an event in a piece of music
"""

import fractions
import representation.events.utils as utils


class Event:
    """
    Class Event
    """

    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        # pylint: disable=unused-argument
        self.offset_time = offset
        self.viewpoints = {}

    def _init_from_list_or_dict(self, offset=None, from_dict=None, from_list=None, features=None):
        # pylint: disable=unused-argument
        if from_dict is not None:
            self.from_feature_dict(from_dict, features)
        elif (from_list is not None) and (features is not None):
            self.from_feature_list(from_list, features)

    def add_viewpoint(self, name, info, category=None):
        """
        Adds a viewpoint to event
        """
        new_name = name
        if '.' not in name and category is not None:
            new_name = category + '.' + name

        viewpoints_flat = utils.flatten_dict(self.viewpoints, sep='.')
        views = [v for v in viewpoints_flat if new_name in v]

        if views != []:
            path = views[0].split('.')
            view_cat = self.viewpoints
            for key in path[:-1]:
                view_cat = view_cat[key]
            utils.add_viewpoint(view_cat, path[-1], info)

    def get_viewpoint(self, name, category=None):
        """
        Returns a viewpoint of event
        """
        new_name = name
        if '.' not in name and category is not None:
            new_name = category + '.' + name

        viewpoints_flat = utils.flatten_dict(self.viewpoints, sep='.')
        views = [v for v in viewpoints_flat if new_name in v]
        if views != []:
            return viewpoints_flat[views[0]]
        return None

    def get_offset(self):
        """
        Returns offset value of event
        """
        return self.offset_time

    def is_rest(self):
        """
        Returns value of 'rest' viewpoint for event
        """
        return self.get_viewpoint('rest')

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

        features_list = [self.get_viewpoint(feat) for feat in features]

        return [self.offset_time] + features_list, features

    def from_feature_list(self, from_list, features, nan_value=10000):
        """
        Transforms list of features in an event
        """
        for i, feat in enumerate(features):
            if feat == 'offset':
                self.offset_time = from_list[i]
            elif from_list[i] == nan_value:
                self.add_viewpoint(feat, None)
            else:
                self.add_viewpoint(feat, from_list[i])

    def to_feature_dict(self, features=None, offset=True):
        """
        Transforms event in a dict of features
        """
        viewpoints_flat = utils.flatten_dict(self.viewpoints, sep='.')
        if features is None:
            features = viewpoints_flat.keys()

        features_dict = {}
        if offset:
            features_dict['offset'] = self.offset_time

        for feat in features:
            views = [v for v in viewpoints_flat if feat in v]
            if views != []:
                features_dict[feat] = viewpoints_flat[views[0]]
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
                self.add_viewpoint(feat, from_dict[feat])

    def __str__(self):
        """
        Overrides str function for Event
        """
        to_return = 'Event at offset {}: \n'.format(self.offset_time)
        viewpoints = ['.'.join(path.split('.')[-2:])
                      for path in utils.flatten_dict(self.viewpoints, sep='.')]

        to_return += ''.join([str(key) + ': ' + str(self.get_viewpoint(key)) + '; '
                              for key in viewpoints])
        return to_return

    def __iter__(self):
        viewpoints = ['.'.join(path.split('.')[-2:])
                      for path in utils.flatten_dict(self.viewpoints, sep='.')]
        yield('offset', self.offset_time)
        for key in viewpoints:
            view = self.get_viewpoint(key)
            if isinstance(view, fractions.Fraction):
                yield(key, str(view))
            else:
                yield(key, view)

    def __eq__(self, other):
        """
        Overrides equal function for Event
        """
        viewpoints = ['.'.join(path.split('.')[-2:])
                      for path in utils.flatten_dict(self.viewpoints, sep='.')]
        for viewpoint in viewpoints:
            self_view = self.get_viewpoint(viewpoint)
            other_view = other.get_viewpoint(viewpoint)
            if other_view is None or self_view != other_view:
                return False
        return True

    def __ne__(self, other):
        """
        Overrides non-equal function for Event
        """
        return not self == other
