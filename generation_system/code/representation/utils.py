#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with representations
"""


import music21
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.impute import SimpleImputer


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
    to_print += str(event.get_viewpoint(viewpoint)) + '; '
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
    to_print += ''.join([(str(event.get_viewpoint(viewpoint)) + ' ')
                         if event.check_viewpoint(viewpoint) else 'None ' for event in events])
    return to_print


def show_part_viewpoint(viewpoint, part, offset=False):
    """
    Shows only a viewpoint for a specific part
    """
    if offset:
        print(show_sequence_of_viewpoint_with_offset(part, viewpoint))
    else:
        print(show_sequence_of_viewpoint_without_offset(part, viewpoint))


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


def cond_sim(event, offset, threshold, offset_thresh):
    """
    cond func for get_all_events_similar_to_event
    """
    res = False
    if event[1] >= threshold:
        if offset_thresh is not None:
            if offset - offset_thresh <= event[0].get_offset() <= offset + offset_thresh:
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
    for event in events:
        matrix.append([event.weighted_comparison(ev, weights)
                       for ev in events])
    return np.array(matrix)


def normalize(feat_list, x_min, x_max):
    """
    Get Normalization for 
    """
    nom = (feat_list-feat_list.min(axis=0))*(x_max-x_min)
    denom = feat_list.max(axis=0) - feat_list.min(axis=0)
    denom[denom == 0] = 1
    return x_min + nom/denom


def normalize_weights(weights):
    """
    Normalize weight list
    """
    if any(w < 0 for w in weights):
        weights = [float(w) + abs(min(weights)) for w in weights]
    return [float(w)/sum(weights) for w in weights]


def create_feature_array_events(events, weights=None, normalization='st1-mt0', offset=True, flatten=True):
    """
    Creating Feature Array and Weights for Oracle
    """
    events_dict = [event.to_feature_dict(weights, offset) for event in events]
    vec = DictVectorizer()
    features = vec.fit_transform(events_dict).toarray()
    features_names = vec.get_feature_names()

    imp = SimpleImputer(missing_values=np.nan,
                        strategy='constant', fill_value=10000)
    features = imp.fit_transform(features)

    norm_features = []
    if normalization == 'st1-mt0':
        norm_features = normalize(features, -1, 1)
    else:
        norm_features = normalize(features, 0, 1)

    if len(features_names) == 1 and flatten:
        features = [x for [x] in features]
        norm_features = [x for [x] in norm_features]

    weighted_fit = None
    if weights is not None:
        weighted_fit = np.zeros(len(features_names))
        for i, feat in enumerate(features_names):
            w_feat = [key for key in weights if feat.find(key) != -1]
            if len(w_feat) == 0:
                weighted_fit[i] = 0
            else:
                weighted_fit[i] = weights[w_feat[0]]

    # dict_normalized = {}
    # for i, event in enumerate(norm_features):
    #     dict_normalized[str(event)] = features[i]
    return norm_features, features, features_names, weighted_fit


def part_name_parser(music_to_parse):
    """
    Return the name and voice of the part
    """
    part_name_voice = [music_to_parse.partName, 'v0']
    if music_to_parse.partName is None:
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
        if not (view is None or view is None):
            return True
    return False
