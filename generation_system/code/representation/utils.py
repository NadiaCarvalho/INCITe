#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with representations
"""

import music21

import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.feature_extraction import DictVectorizer


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


def get_analysis_keys_measure(measure):
    """
    Gets an analysis of key for a measure
    """
    k = measure.analyze('key')
    return (measure.number, k)


def harmonic_functions_key(chord, key):
    """
    Parses the harmonic key signatures information for a key
    """
    return music21.roman.romanNumeralFromChord(chord, key)


def get_all_events_similar_to_event(events, event, weights=None, threshold=0.5, offset_thresh=None):
    """
    Get all events that are similar to an event in a certain threshold
    """
    res = [(ev, event.weighted_comparison(ev, weights)) for ev in events]
    return [ev for ev in res if cond_sim(ev, event.get_offset(), threshold, offset_thresh)]


def cond_sim(ev, offset, threshold, offset_thresh):
    """
    cond func for get_all_events_similar_to_event
    """
    res = False
    if ev[1] >= threshold:
        if offset_thresh is not None:
            if offset - offset_thresh <= ev[0].get_offset() <= offset + offset_thresh:
                res = True
        else:
            res = True

    return res


def create_similarity_matrix(events, weights=None):
    """
    Create Similarity Matrix for events with weights
    Usage:
    similar = rep_utils.get_all_events_similar_to_event(
        part_events[0], part_events[0][6], weights, 0.4, 1.5)
    similarity_matrix = rep_utils.create_similarity_matrix(
        part_events[0][:5], weights)
    print(similarity_matrix)
    [print(str(ev[0].get_offset()) + ' : ' + str(ev[1])) for ev in similar]
    """
    matrix = []
    for i, event in enumerate(events):
        matrix.append([event.weighted_comparison(ev, weights)
                       for ev in events])
    return np.array(matrix)


def create_feature_array_events(events, weights):
    """
    Creating Feature Array and Weights for Oracle
    """
    events_dict = [event.to_feature_dict(weights) for event in events]
    vec = DictVectorizer()
    features = vec.fit_transform(events_dict).toarray()
    features_names = vec.get_feature_names()

    if len(features_names) == 1:
        features = [x for [x] in features]

    weighted_fit = np.zeros(len(features_names))
    for i, feat in enumerate(features_names):
        w_feat = [key for key in weights if feat.find(key) != -1]
        if len(w_feat) == 0:
            weighted_fit[i] = 0
        else:
            weighted_fit[i] = weights[w_feat[0]]

    return features, features_names, weighted_fit
