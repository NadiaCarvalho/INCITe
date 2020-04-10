#!/usr/bin/env python3.7
"""
This script presents the class LineSegmenter that tries different approaches to segment a melodic line
"""

class LineSegmenter:
    """
    A class used to segment lines of music represented as events of viewpoints.

    Attributes
    ----------
    """
    
    def __init__(self, events_to_segment):
        self.events = events_to_segment