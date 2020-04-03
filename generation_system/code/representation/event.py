#!/usr/bin/env python3.7
"""
This script presents the class Event that represents an event in a piece of music
"""


class Event:
    """
    Class Event
    """

    def __init__(self, offset):
        self.offset_time = offset
        self.viewpoints = {}

    def add_viewpoint(self, viewpoint):
        """
        Adds a viewpoint to event
        """
        self.viewpoints[viewpoint.get_name()] = viewpoint

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
        Returns value of 'is_rest' viewpoint for event
        """
        return self.viewpoints['is_rest'].get_info()

    def is_grace_note(self):
        """
        Returns value of 'is_grace' viewpoint for event
        """
        return self.viewpoints['is_grace'].get_info()

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
            #viewpoint = self.viewpoints[key]
            #other_view = other.get_viewpoint(key)
            if self.get_viewpoint(key) == other.get_viewpoint(key):
                score += weight
    
        return (score/sum(weights.values()))

    def __str__(self):
        """
        Overrides str function for Event
        """
        to_return = 'Event at offset {}: \n'.format(self.offset_time)
        to_return += ''.join([str(viewpoint)
                              for key, viewpoint in self.viewpoints.items()])
        return to_return

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
