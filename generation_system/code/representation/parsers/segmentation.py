#!/usr/bin/env python3.7
"""
This script presents the necessary functions for dealing with segmentation of musical phrases
"""

import math

import numpy as np

import representation.utils as utils


def change_degree(event_1, event_2):
    """
    Returns degree of change between two events for each feature
    of event
    """
    return [abs(a - b)/(a + b) if a != b else 0 for a, b in zip(event_1, event_2)]


def strength(nf_im1, nf_i, nf_ip1):
    """
    Gets Strength for each feature of an event from the its 
    normalized feature list representation,
    and the normalized feature list 
    representations of the previous and posterious events
    """
    degree_1 = change_degree(nf_im1, nf_i)
    degree_2 = change_degree(nf_i, nf_ip1)
    sum_nf = [a+b for a, b in zip(degree_1, degree_2)]
    return [a*b for a, b in zip(nf_i, sum_nf)]


def threshold_peak_picking(i, window, k, boundary_strengths):
    """
    Calculates the threshold value, using standard deviation and mean 
    In a specific Window of Time
    """
    start = 0
    if (i-window) > start:
        start = (i-window)

    bs_window = boundary_strengths[start:i]
    xbar = [sum(bs)/len(bs_window) for bs in zip(*bs_window)]
    deviations = [[(a - b)**2 for a, b in zip(bs, xbar)]
                  for bs in boundary_strengths[:i]]

    sum_dev = [sum(dev) for dev in zip(*deviations)]
    sum_mean = [sum(bs) for bs in zip(*boundary_strengths[:i])]

    variances = [math.sqrt(dev/(i-1)) for dev in sum_dev]
    means = [(mean/(i-1)) for mean in sum_mean]

    return [(k*v + m) for v, m in zip(variances, means)]


def peak_picking(i, boundary_strengths, weights, window=None, k=1.28):
    """
    Peak Picking Boundary Location Witten and Pearce

    Principles:
    - Note following a boundary should have greater/equal strength than following note
    - Note following a boundary should have greater/equal strength than preciding note
    - Note following a boundary should have higher (> k) strength

    Returns 1 for existent boundary before note
    Returns 0 for not existent boundary before note
    """
    if i < 2:  # First note is always a note following a boundary
        return 1-i  # Second note is not a candidate
    if i == len(boundary_strengths)-1:  # Penultimate note is not candidate
        return 0

    if window is None:
        window = i

    w_bs_i = np.dot(boundary_strengths[i], weights)
    w_bs_ip1 = np.dot(boundary_strengths[i+1], weights)
    w_bs_im1 = np.dot(boundary_strengths[i-1], weights)
    w_value = np.dot(threshold_peak_picking(
        i, window, k, boundary_strengths), weights)

    if (w_bs_i >= w_bs_ip1 and w_bs_i >= w_bs_im1 and w_bs_i > w_value):
        return 1
    return 0


def segmentation(events):
    """
    Segmentation for a set of events, using 
    Peak Picking Boundary Location by Witten and Pearce
    """
    # all features are equally relevant for now
    #weights_dict = {i: 1 for i in list(events[0].viewpoints)}

    # with different weights
    weights_dict = {  # candidates for phrasing discovery (melodic)
        # 'pitch.value': 1,
        'rest': 1,
        # 'dur_length': 1,
        'fermata': 1,
        'breath_mark': 1,
        'closure': 1,

        # 'seq_int': 1,
        # 'contour': 1,
        # 'contour_hd': 1,
        # 'fib': 1,
        # 'posinbar': 1,
        # 'beat_strength': 1,
        # 'double': 1,
        # 'repeat.exists': 1,
        # 'signatures.scale_degree': 1,
        # 'scale_degree_ms': 1,
    }

    # Get all events as a set of normalized features
    norm_features, _, _, weights = utils.create_feature_array_events(
        events, weights=weights_dict, normalization='from_0',
        offset=False, flatten=False)

    # Calculate boundary strengths
    boundary_strengths = [strength(norm_features[i-1],
                                   norm_features[i], norm_features[i+1])
                          for i, _ in enumerate(events[1:-1])]
    boundary_strengths.insert(0, np.zeros(len(weights)))

    # Normalize strenghs and weights
    normalized_bss = utils.normalize(np.array(boundary_strengths), 0, 1)
    normalized_weights = utils.normalize_weights(weights)

    # Apply phrasing
    for i, event in enumerate(events):
        if i == len(events) - 1:
            events[-1].add_viewpoint('phrase.boundary', -1)
            break

        # Calculate presence of boundary
        boundary = peak_picking(i, normalized_bss, weights)
        event.add_viewpoint('phrase.boundary', boundary)
        if boundary == 1 and i != 0:
            events[i-1].add_viewpoint('phrase.boundary', -boundary)
