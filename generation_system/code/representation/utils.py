#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with representations
"""


def sign(_x):
    """
    Returns the sign of a number
    """
    return _x and (1, -1)[_x < 0]


def seq_int(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns the difference between two midi values
    """
    return midi_viewpoint_1.get_info() - midi_viewpoint_2.get_info()


def contour(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns the signal between two midi values
    """
    return sign(midi_viewpoint_1.get_info() - midi_viewpoint_2.get_info())


def contour_hd(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns a quantized difference between two midi values
    Defined in (Mullensiefen and Frieler, 2004a)
    """
    result = midi_viewpoint_1.get_info() - midi_viewpoint_2.get_info()
    values = [1, 3, 5, 8]
    for count, ele in enumerate(values):
        if result < ele:
            return sign(result)*count
    return int(0)


def get_first_event_that_is_note_before_index(events, actual_index=None):
    """
    Returns the first event that is a note but not a rest before an event
    """
    if len(events) < 2:
        return None
    if actual_index is None:
        actual_index = len(events) - 1
    events_process = events[:actual_index]
    for i in range(len(events_process)):
        index = len(events_process) - (i + 1)
        if not events_process[index].is_rest():
            return index
    return None


def offset_info(event, viewpoint):
    """
    Returns a string of offset : specific viewpoint for an event
    """
    to_print = 'Off ' + str(event.get_offset()) + ': '
    to_print += str(event.get_viewpoint(viewpoint).get_info()) + '; '
    return to_print


def show_sequence_of_viewpoint_with_offset(events, viewpoint):
    """
    Returns a string of a specific viewpoint for all events and offset of event
    """
    viewpoint_events = [offset_info(
        event, viewpoint) for event in events if event.check_viewpoint(viewpoint)]
    to_print = 'Viewpoint ' + viewpoint + ' : '
    to_print += ''.join(viewpoint_events)
    return to_print


def show_sequence_of_viewpoint_without_offset(events, viewpoint):
    """
    Returns a string of a specific viewpoint for all events with no offset
    """
    to_print = 'Viewpoint ' + viewpoint + ': '
    to_print += ''.join([(str(event.get_viewpoint(viewpoint).get_info()) + ' ')
                         if event.check_viewpoint(viewpoint) else 'None ' for event in events])
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
    if offset2 is None:
        offset2 = events[-1].get_offset()
    return [event for event in events if offset1 <= event.get_offset() <= offset2]

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
