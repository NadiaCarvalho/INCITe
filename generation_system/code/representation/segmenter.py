#!/usr/bin/env python3.7
"""
This script presents a segmentation algorithm
"""

from fractions import Fraction

import music21

def segmenter(stream):
    """
    TODO: Segment using 
    """
    segments, measureLists = music21.search.segment.translateMonophonicPartToSegments(
        stream,
        algorithm=music21.search.translateDiatonicStreamToString)
    print(measureLists)
