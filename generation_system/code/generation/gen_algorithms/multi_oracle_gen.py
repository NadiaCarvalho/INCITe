#!/usr/bin/env python3.7
"""
This script defines the generation algorithm for synchronization of various Oracles
"""

import random

import numpy as np

from generation.oracles.factor_oracle import FactorOracle


def sync_generate(oracles, offsets, seq_len=10, p=0.5, k=1):
    """
    Generate synchronized lines from various oracles
    """
    len_events_by_part = [(key, len(part)) for key, part in offsets.items()]
    len_events_by_part.sort(key=lambda tup: tup[1], reverse=True)
    principal_key = len_events_by_part[0][0]
    max_size = len_events_by_part[0][1] + 1

    trns = {}
    sfxs = {}
    lrss = {}
    rsfxs = {}
    sequences = {}
    ktraces = {}

    for key, oracle in oracles.items():
        trns[key] = oracle.basic_attributes['trn'][:]
        sfxs[key] = oracle.basic_attributes['sfx'][:]
        lrss[key] = oracle.basic_attributes['lrs'][:]
        rsfxs[key] = oracle.basic_attributes['rsfx'][:]
        sequences[key] = []
        ktraces[key] = [k]

    for _i in range(seq_len):
        print(k)

        ks_at_k = _find_ks(offsets, principal_key, k)
        last_ktraces = dict([(key, ktr[-1]) for key, ktr in ktraces.items()])

        print('LK1: ' + str(ks_at_k))
        print('KTR: ' + str(dict([(key, ktr[-1]) for key, ktr in ktraces.items()])))

        sfxs_k = dict([(key, sfxs[key][ks_at_k[key]])
                       for key in ks_at_k.keys()])

        sym_1 = None
        # generate each state
        if any(list(sfxs_k.values())):
            if (random.random() < p):
                print('TRANSITIONS')
                key, sym = copy_transitions(
                    k, trns, sfxs, ks_at_k, ktraces, offsets, principal_key)
            else:
                print('SFXS BEST LRSS')
                key, sym = jump_best_lrss(
                    sfxs, rsfxs, lrss, max_size, ktraces, ks_at_k, offsets, principal_key)
                sym_1 = sym + 1
        else:
            if all(ks < len(sfxs[key]) - 1 for key, ks in ks_at_k.items()):
                print('STRAIGHT FORWARD')
                key = principal_key
                sym = k + 1
            else:
                print('SFXS RANDOM')
                key, sym = choose_from_sfxs_k(
                    k, sfxs, ks_at_k, offsets, principal_key)
                sym_1 = sym + 1

        next_keys = _find_ks(offsets, key, sym)
        keys_at_last_k = ks_at_k
        if sym_1 is not None:
            keys_at_last_k = next_keys
            next_keys = _find_ks(offsets, key, sym_1)

        print('OK: ' + str(dict([(key, len(part))
                                 for key, part in sfxs.items()])))
        print('LK2: ' + str(keys_at_last_k))
        print('NK: ' + str(next_keys))
        print('offsets: ' + str(dict([(key, offsets[key][k-1]) for key, k in next_keys.items()])))

        all_different = all(next_keys[key] > (keys_at_last_k[key] + 1) for key in next_keys.keys() if key in keys_at_last_k)

        for key in sfxs.keys():
            if key in next_keys:
                if not all_different and (key in keys_at_last_k and next_keys[key] > (keys_at_last_k[key] + 1)):
                    for i in range(next_keys[key] - keys_at_last_k[key]):
                        sequences[key].append(keys_at_last_k[key] + i + 1)
                        ktraces[key].append(keys_at_last_k[key] + i + 1)
                else:
                    sequences[key].append(next_keys[key])
                    ktraces[key].append(next_keys[key])
            elif key in keys_at_last_k:
                next_k_princ = keys_at_last_k[principal_key]
                next_k = _find_nearest_k(
                    offsets, key, offsets[principal_key][next_k_princ])
                for i in range(abs(next_k - keys_at_last_k[key])):
                    sequences[key].append(keys_at_last_k[key] + i + 1)
                    ktraces[key].append(keys_at_last_k[key] + i + 1)
        k = next_keys[principal_key]

        if any(ks > len(sfxs[key]) - 1 for key, ks in _find_ks(offsets, principal_key, k).items()):
            k = 0

        print()
    return sequences, ktraces


def choose_from_sfxs_k(k, sfxs, ks_at_k, offsets, principal_key):
    """
    Choose a random k from sfxs
    """
    sfxs_k = dict([(key, sfxs[key][ks_at_k[key]])
                   for key in ks_at_k.keys()])
    possible_moves = [(key, sfx) for key, sfx in sfxs_k.items() if len(
        _find_ks(offsets, key, sfx).values()) == len(offsets.keys())]

    pr_key = principal_key
    sym = sfxs_k[principal_key]
    if len(possible_moves) > 0:
        pr_key, sym = possible_moves[int(
            np.floor(random.random() * len(possible_moves)))]
    return pr_key, sym


def copy_transitions(k, trns, sfxs, ks_at_k, ktraces, offsets, principal_key, i=0):
    """
    Copy forward according to possible transitions for all oracles
    """
    I = get_f_transitions_by_oracle(
        trns, _find_ks(offsets, principal_key, k), offsets)

    if i > 5:
        return choose_from_sfxs_k(k, sfxs, ks_at_k, offsets, principal_key)

    if len(I) == 0:
        key_pr, sym = choose_from_sfxs_k(
            k, sfxs, ks_at_k, offsets, principal_key)
        new_ks = _find_ks(offsets, key_pr, sym)
        _ = [ktraces[key].append(value) for key, value in new_ks.items()]
        return copy_transitions(new_ks[principal_key], trns, sfxs, ks_at_k, ktraces, offsets, principal_key, i+1)

    return I[int(np.floor(random.random() * len(I)))]


def jump_best_lrss(sfxs, rsfxs, lrss, max_size, ktraces, ks_at_k, offsets, principal_key):
    """
    Get Best Suffix to Jump
    """
    _ = [ktraces[key].append(value) for key, value in ks_at_k.items()]
    key, sym = get_next_suffix(
        sfxs, rsfxs, lrss, max_size, ks_at_k, offsets)
    if key == '':
        key = principal_key
    return key, sym


def get_sim_trans(I, offsets, key):
    """
    Get Simultaneous Transitions by K
    """
    return [trans for trans in I if len(_find_ks(offsets, key, trans).values()) == len(offsets.keys())]


def get_f_transitions_by_oracle(trns, ks_at_k, offsets):
    """
    Get all Possible Transitions at offset k
    """
    trans = dict([(key, trns[key][ks_at_k[key]])
                  for key in ks_at_k.keys()])
    return [(key, tr) for key, I in trans.items() for tr in get_sim_trans(I, offsets, key)]


def get_next_suffix(sfxs, rsfxs, lrss, max_size, ks_at_k, offsets):
    """
    Try candidate suffix links for all oracles,
    find the one that gets the maximum lrs position
    and return
    """
    k_vecs = dict([(key, []) for key in sfxs.keys()])
    k_vecs = dict([(key, _find_links(k_vecs[key], sfxs[key], rsfxs[key],
                                     ks_at_k[key])) for key in ks_at_k.keys()])
    lrs_vecs = dict([(key, [lrss[key][_i] for _i in k_vec])
                     for key, k_vec in k_vecs.items()])

    k_vecs, lrs_vecs = filter_lrss(k_vecs, lrs_vecs, offsets)
    return get_max_lrs_position(k_vecs, lrs_vecs, max_size)


def filter_lrss(k_vecs, lrs_vecs, offsets):
    """
    Filter LRSs that go to a state that has
    a next state with events in all voices
    """
    k_vecs_filtered = {}
    lrs_vecs_filtered = {}
    for key, k_poss in lrs_vecs.items():
        k_vecs_filtered[key] = []
        lrs_vecs_filtered[key] = []

        for i, k in enumerate(k_poss):
            if len(_find_ks(offsets, key, k).values()) == len(offsets.keys()):
                k_vecs_filtered[key].append(k_vecs[key][i])
                lrs_vecs_filtered[key].append(k)

        if len(k_vecs_filtered[key]) == 0:
            k_vecs_filtered[key] = k_vecs[key]
            lrs_vecs_filtered[key] = lrs_vecs_filtered[key]

    return k_vecs_filtered, lrs_vecs_filtered


def get_max_lrs_position(k_vecs, lrs_vecs, length):
    """
    Find the position of the max lrs
    """
    key_lrss = [''] * length
    max_lrss = [0] * length

    for key, k_vec in k_vecs.items():
        for i, k in enumerate(k_vec):
            if lrs_vecs[key][i] >= max_lrss[k]:
                max_lrss[k] = lrs_vecs[key][i]
                key_lrss[k] = key

    max_lrs = max_lrss.index(max(max_lrss))
    return key_lrss[max_lrs], max_lrs


def _find_ks(offsets, principal_key, k):
    """
    Find k for parts at offset x
    """
    if k == 0:
        return dict([(key, 0) for key in offsets.keys()])

    print('FINDKS: ' + str(k))
    result = dict([(key, off.index(offsets[principal_key][k-1])+1)
                 for key, off in offsets.items() if offsets[principal_key][k-1] in off])
    print(result)
    print()
    return result


def _find_nearest_k(offsets, key, off):
    k = np.argmin(np.abs(np.array(offsets[key])-off))
    if offsets[key][k] < off:
        k += 1
    return k


def _find_links(k_vec, sfx, rsfx, k):
    """Find sfx/rsfx recursively."""
    k_vec.sort()
    if 0 in k_vec:
        return k_vec
    else:
        if sfx[k] not in k_vec:
            k_vec.append(sfx[k])
        for i in range(len(rsfx[k])):
            if rsfx[k][i] not in k_vec:
                k_vec.append(rsfx[k][i])
        for i in range(len(k_vec)):
            k_vec = _find_links(k_vec, sfx, rsfx, k_vec[i])
            if 0 in k_vec:
                break
        return k_vec
