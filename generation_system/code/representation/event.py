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

    def __str__(self):
        """
        Overrides str function for Event
        """
        to_return = 'Event at offset {}: \n'.format(self.offset_time)
        to_return += ''.join([str(viewpoint)
                              for key, viewpoint in self.viewpoints.items()])
        return to_return
