#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with events
"""

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


def get_all_inner_keys(dictionary, keys=[]):
    """
    Get all inner keys of dict
    """
    for key, value in dictionary.items():
        if not isinstance(value, dict):
            if key not in keys:
                keys.append(key)
        else:
            get_all_inner_keys(value)

    return utils.flatten([retrieve_path_to_key(dictionary, key) for key in keys])


def retrieve_path_to_key(dictionary, key_to_search):
    dict_copy = dict(copy.deepcopy(dictionary))
    keys = dictionary.keys()
    paths = []

    for key in keys:
        while dict_copy[key] != {}:
            path = retrieve_paths(dict_copy[key], key_to_search)
            if path is not None:
                proc_path = key + '.' + path
                if proc_path not in paths:
                    paths.append(proc_path)

                path_val = path.split('.')
                to_del = path_val[0]
                view_cat = dict_copy[key]

                if len(path_val) > 2:
                    for val in path_val[:-2]:
                        view_cat = view_cat[val]
                    to_del = path_val[-2]

                view_cat.pop(to_del, None)
                dict_copy[key] = view_cat

            if path is None or not any(isinstance(i, dict) for i in dict_copy[key].values()):
                dict_copy[key] = {}

        if key in dict_copy:
            del dict_copy[key]

    return paths


def retrieve_paths(dictionary, key_to_search):
    """
    Retrieve a path of key for nested dicts
    """
    if not isinstance(dictionary, dict):
        return None

    if key_to_search in dictionary:
        return key_to_search

    path = None
    for key, value in dictionary.items():
        res = retrieve_paths(value, key_to_search)
        if res is not None:
            path = "{}.{}".format(key, res)
    return path
