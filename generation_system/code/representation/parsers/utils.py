#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with representations
"""

import copy
import math

import music21
import numpy as np


"""
Basic/Maths Functions
"""


def flatten(newlist):
    """
    flatten a list with strings
    """
    rt = []
    for item in newlist:
        if isinstance(item, list):
            rt.extend(flatten(item))
        else:
            rt.append(item)
    return rt


def is_power(x, y):
    """
    Check if number is power of another
    """

    # The only power of 1
    # is 1 itself
    if (x == 1):
        return (y == 1)

    # Repeatedly compute
    # power of x
    _pow = 1
    while (_pow < y):
        _pow = _pow * x

    # Check if power of x
    # becomes y
    return (_pow == y)


def sign(x): return x and (1, -1)[x < 0]


def seq_int(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns the difference between two midi values
    """
    return midi_viewpoint_1 - midi_viewpoint_2


def contour(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns the signal between two midi values
    """
    return sign(midi_viewpoint_1 - midi_viewpoint_2)


def contour_hd(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns a quantized difference between two midi values
    Defined in (Mullensiefen and Frieler, 2004a)
    """
    result = midi_viewpoint_1 - midi_viewpoint_2
    values = [1, 3, 5, 8]
    for count, ele in enumerate(values):
        if result < ele:
            return sign(result)*count
    return int(0)


"""
Offset Related
"""


def get_last_x_events_that_are_notes_before_index(events, number=1, actual_index=None):
    """
    Returns the first event that is a note but not a rest before an event
    """
    if len(events) < 2:
        return None
    elif len(events) < number+1:
        number = len(events)-1

    if actual_index is None:
        actual_index = len(events) - 1

    count = 0
    events_to_return = []
    events_process = events[:actual_index]
    for i in range(len(events_process)):
        index = len(events_process) - (i + 1)
        if not events_process[index].is_rest():
            if number == 1:
                return index
            if count < number:
                events_to_return.append(index)
                count += 1
            else:
                return events_to_return
    return None


def offset_info(event, viewpoint):
    """
    Returns a string of offset : specific viewpoint for an event
    """
    to_print = 'Off ' + str(event.get_offset()) + ': '
    to_print += str(event.get_viewpoint(viewpoint)) + '; '
    return to_print


def get_events_at_offset(events, offset):
    """
    Returns all events that happen at a specified offset
    """
    return [event for event in events if event.get_offset() == offset]


def get_evs_bet_offs_inc(events, offset1, offset2=None):
    """
    Returns all events that happen between (and including) two specified offsets
    """
    if len(events) < 1:
        return events

    if offset2 is None:
        offset2 = events[-1].get_offset()

    return [event for event in events if offset1 <= event.get_offset() <= offset2]


"""
Parsing Utilities
"""


def not_rest_or_grace(event):
    """
    Returns True/False if event is not rest or grace note
    """
    return not (event.is_grace_note() or event.is_rest())


def get_rests(events):
    """
    Returns all events that are rests
    """
    return [event for event in events if event.is_rest()]


def get_grace_notes(events):
    """
    Returns all events that are grace notes
    """
    return [event for event in events if event.is_grace_note()]


def harmonic_functions_key(chord, key):
    """
    Parses the harmonic key signatures information for a key
    """
    return music21.roman.romanNumeralFromChord(chord, key)


def part_name_parser(music_to_parse):
    """
    Return the name and voice of the part
    """
    part_name_voice = [music_to_parse.partName, 'v0']
    if music_to_parse.partName is None and type(music_to_parse.id) == str:
        part_name_voice = music_to_parse.id.split('-')
    return part_name_voice


def get_analysis_keys_stream_bet_offsets(music_to_parse, off1, off2):
    """
    Gets an analysis of key for a stream
    """
    k = music_to_parse.getElementsByOffset(
        off1, off2).stream().analyze('key')
    return (off1, k)


def has_value_viewpoint_events(events, viewpoint):
    """
    For a sequence of events, evaluate
    if all None (False) or not (True)
    """
    for event in events:
        view = event.get_viewpoint(viewpoint)
        if not view is None:
            return True
    return False
