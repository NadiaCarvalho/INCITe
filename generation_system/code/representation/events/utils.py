#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with events
"""

import collections
import copy
import representation.utils as utils


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
    if type(dnote) is type(''):
        return dnotes[dnote]

    note_number = int(list(dnotes.values()).index(dnote))
    return list(dnotes.keys())[note_number]


def _add_viewpoint(viewpoint, name, info):
    """
    Add viewpoint sub-routine
    """
    if isinstance(viewpoint[name], list):
        viewpoint[name].append(info)
        viewpoint[name] = utils.flatten(viewpoint[name])
    else:
        viewpoint[name] = info

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
