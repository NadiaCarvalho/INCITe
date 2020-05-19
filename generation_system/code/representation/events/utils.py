#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with events
"""

import collections

import music21

import representation.utils.features as utils


def convert_note_name(dnote):
    """
    Converts note names to integers and backwards
    """
    dnotes = {
        'C': 0,
        'D': 1,
        'E': 2,
        'F': 3,
        'G': 4,
        'A': 5,
        'B': 6
    }
    if isinstance(dnote, str):
        return dnotes[dnote]

    note_number = int(list(dnotes.values()).index(dnote))
    return list(dnotes.keys())[note_number]


def add_viewpoint(viewpoint, name, info):
    """
    Add viewpoint sub-routine
    """
    if isinstance(viewpoint[name], list):
        viewpoint[name].append(info)
        viewpoint[name] = utils.flatten(viewpoint[name])
    else:
        viewpoint[name] = info


def flatten_dict(dictionary, parent_key='', sep='_'):
    """
    Flatten a dictionary using
    sep as separator for nested keys
    """
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def instrument_converter(instrument):
    """
    Convert Instrument String to Instrument
    """
    if 'Instrument' in instrument:
        instrument = 'Instrument'
    elif instrument in ['Brass', 'Woodwind', 'Keyboard', 'String']:
        instrument += 'Instrument'

    try:
        instrument = getattr(music21.instrument, instrument)()
    except AttributeError:
        print('Wrong Instrument: ' + instrument)
        try:
            instrument = music21.instrument.fromString(
                instrument)
        except music21.exceptions21.InstrumentException:
            print(
                "Can't convert from this instrument: " + instrument)
            instrument = music21.instrument.Instrument()
    return instrument
