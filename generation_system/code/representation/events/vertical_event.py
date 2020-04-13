#!/usr/bin/env python3.7
"""
This script presents the class VerticalEvent that represents a vertical (harmonic) event in a piece of music
"""
from representation.events.event import Event

class VerticalEvent(Event):
    """
    Class VerticalEvent
    """
    def __init__(self, offset=None, from_dict=None, from_list=None, features=None):
        super().__init__(offset, from_dict, from_list, features)

        if len(list(self.viewpoints)) == 0:
            self.viewpoints = {
                
            }