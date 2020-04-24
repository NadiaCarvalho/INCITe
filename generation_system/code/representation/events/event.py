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
        self.offset_time = offset
        self.viewpoints = {}

    def _init_from_list_or_dict(self, offset=None, from_dict=None, from_list=None, features=None):
        if from_dict is not None:
            self.from_feature_dict(from_dict, features)
        elif (from_list is not None) and (features is not None):
            self.from_feature_list(from_list, features)

    def get_view_aux(self, name, category, info=None, add=False):
        """
        Aux function for get/add viewpoint
        """
        paths = utils.retrieve_path_to_key(
            self.viewpoints, name)

        if add and len(paths) == 0:
            self.viewpoints[name] = info
        elif len(paths) > 0:
            viewpoint_path = paths[0].split('.')

            if category is not None:
                for path in paths:
                    list_paths = path.split('.')
                    if category in list_paths:
                        viewpoint_path = list_paths
                        break

            v_to_process = viewpoint_path
            if add:
                v_to_process = viewpoint_path[:-1]

            view_cat = self.viewpoints
            for viewpoint in v_to_process:
                view_cat = view_cat[viewpoint]
            return view_cat
        return None

    def add_viewpoint(self, name, info, category=None):
        """
        Adds a viewpoint to event
        """
        new_name = name
        new_category = category
        if '.' in name:
            splitted = name.split('.')
            new_name = splitted[1]
            new_category = splitted[0]

        view_cat = self.get_view_aux(new_name, info, new_category, add=True)
        if view_cat is not None:
            utils._add_viewpoint(view_cat, new_name, info)

    def get_viewpoint(self, name, category=None):
        """
        Returns a viewpoint of event
        """
        new_name = name
        new_category = category
        if '.' in name:
            splitted = name.split('.')
            new_name = splitted[1]
            new_category = splitted[0]

        return self.get_view_aux(new_name, new_category)

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

    def from_feature_list(self, from_list, features, nan_value=1000):
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
        if features is None:
            features = list(self.viewpoints)

        features_dict = {}

        if offset:
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
                self.add_viewpoint(feat, from_dict[feat])

    def __str__(self):
        """
        Overrides str function for Event
        """
        to_return = 'Event at offset {}: \n'.format(self.offset_time)
        viewpoints = ['.'.join(path.split('.')[-2:])
                      for path in utils.get_all_inner_keys(self.viewpoints)]

        to_return += ''.join([str(key) + ': ' + str(self.get_viewpoint(key)) + '; '
                              for key in viewpoints])
        return to_return

    def __iter__(self):
        viewpoints = ['.'.join(path.split('.')[-2:])
                      for path in utils.get_all_inner_keys(self.viewpoints)]
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
                      for path in utils.get_all_inner_keys(self.viewpoints)]
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
