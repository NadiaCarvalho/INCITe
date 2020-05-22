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
        ks_at_offset_k = _find_ks(offsets, principal_key, k)
        sfxs_k = dict([(key, sfxs[key][ks_at_offset_k[key]])
                       for key in ks_at_offset_k.keys()])

        print(ks_at_offset_k)
        print('SFXS : ' + str(sfxs_k))

        # generate each state
        # if any(list(sfxs_k.values())):
        if sfxs_k[principal_key] != 0 and sfxs_k[principal_key] is not None:
            if (random.random() < p):
                print('FORWARD')
                k = copy_forward(trns, sfxs, ktraces, sequences,
                                 offsets, principal_key, k)
            else:
                print('SFXS')
                _ = [ktraces[key].append(value)
                     for key, value in ks_at_offset_k.items()]
                sym, key_pr = get_next_suffix(
                    sfxs, rsfxs, lrss, max_size, ks_at_offset_k)
                k_symbols = _find_ks(offsets, key_pr, sym)

                if sym == len(sfxs[key_pr]) - 1:
                    sym = sfxs[key_pr][sym] + 1

                _ = [sequences[key].append(ks + 1)
                     for key, ks in k_symbols.items()]
                k = k_symbols[principal_key] + 1
                _ = [ktraces[key].append(ks + 1)
                     for key, ks in k_symbols.items()]
        else:
            if all(ks < len(sfxs[key]) - 1 for key, ks in ks_at_offset_k.items()):
                print('FORWARD OFF')
                next_keys = _find_ks(offsets, principal_key, k + 1)
                # copy forward
                for key in sfxs.keys():
                    if key in next_keys:
                        sequences[key].append(next_keys[key])
                        ktraces[key].append(next_keys[key])
                    elif key in ks_at_offset_k:
                        next_k = _find_nearest_k(
                            offsets, key, offsets[principal_key][k+1])
                        for i in range(next_k - ks_at_offset_k[key]):
                            sequences[key].append(ks_at_offset_k[key] + i + 1)
                            ktraces[key].append(ks_at_offset_k[key] + i + 1)
                k += 1
            else:
                print('SFXS OFF')
                possible_moves = [(key, sfx) for key, sfx in sfxs_k.items() if len(
                    _find_ks(offsets, key, sfx).values()) == len(offsets.keys())]

                pr_key = principal_key
                if len(possible_moves) > 0:
                    pr_key, sym = possible_moves[int(
                        np.floor(random.random() * len(possible_moves)))]
                else:
                    sym = sfxs[principal_key][k]

                new_keys = _find_ks(offsets, pr_key, sym + 1)
                # for key, ks in new_keys.items():
                #         sequences[key].append(ks + 1)
                #         ktraces[key].append(ks + 1)

                for key in sfxs.keys():
                    if key in next_keys:
                        sequences[key].append(next_keys[key])
                        ktraces[key].append(next_keys[key])
                    elif key in ks_at_offset_k:
                        next_k = _find_nearest_k(
                            offsets, key, offsets[principal_key][k+1])
                        for i in range(next_k - ks_at_offset_k[key]):
                            sequences[key].append(ks_at_offset_k[key] + i + 1)
                            ktraces[key].append(ks_at_offset_k[key] + i + 1)

                k = new_keys[principal_key]

        if any(ks > len(sfxs[key]) - 1 for key, ks in _find_ks(offsets, principal_key, k).items()):
            k = 0

        print()
        # print(sequences)

    return sequences, ktraces


def copy_forward(trns, sfxs, ktraces, sequences, offsets, principal_key, k):
    """
    Copy forward according to transitions for all oracles
    """
    I = get_f_transitions_by_oracle(
        trns, _find_ks(offsets, principal_key, k), offsets)

    if len(I) == 0:
        # if last state, choose a suffix
        k = sfxs[principal_key][k]
        ktraces[principal_key].append(k)
        return copy_forward(trns, sfxs, ktraces, sequences, offsets, principal_key, k)

    key, sym = I[int(np.floor(random.random() * len(I)))]
    new_ks = _find_ks(offsets, key, sym)

    _ = [sequences[key].append(value)
         for key, value in new_ks.items()]
    _ = [ktraces[key].append(value)
         for key, value in new_ks.items()]

    return new_ks[principal_key]


def get_sim_trans(I, offsets, key):
    """
    Get Simultaneous Transitions by K
    """
    return [trans for trans in I if len(_find_ks(offsets, key, trans).values()) == len(offsets.keys())]


def get_f_transitions_by_oracle(trns, ks_at_offset_k, offsets):
    """
    Get all Possible Transitions at offset k
    """
    trans = dict([(key, trns[key][ks_at_offset_k[key]])
                  for key in ks_at_offset_k.keys()])
    return [(key, tr) for key, I in trans.items() for tr in get_sim_trans(I, offsets, key)]


def get_next_suffix(sfxs, rsfxs, lrss, max_size, ks_at_offset_k):
    """
    Try candidate suffix links for all oracles,
    find the one that gets the maximum lrs position
    and return
    """
    k_vecs = dict([(key, []) for key in sfxs.keys()])
    k_vecs = dict([(key, _find_links(k_vecs[key], sfxs[key], rsfxs[key],
                                     ks_at_offset_k[key])) for key in ks_at_offset_k.keys()])
    lrs_vecs = dict([(key, [lrss[key][_i] for _i in k_vec])
                     for key, k_vec in k_vecs.items()])

    return get_max_lrs_position(k_vecs, lrs_vecs, max_size)


def get_max_lrs_position(k_vecs, lrs_vecs, length):
    """
    Find the position of the max lrs
    """
    key_lrss = [''] * length
    max_lrss = [0] * length
    for key, k_vec in k_vecs.items():
        for i, k in enumerate(k_vec):
            if lrs_vecs[key][i] > max_lrss[k]:
                max_lrss[k] = lrs_vecs[key][i]
                key_lrss[k] = key

    max_lrs = max_lrss.index(max(max_lrss))
    return max_lrs, key_lrss[max_lrs]


def _find_ks(offsets, principal_key, k):
    """
    Find k for parts at offset x
    """
    if k == 0:
        return dict([(key, 0) for key in offsets.keys()])

    # print('FIND KS')
    # print(offsets)
    # print(principal_key)
    # print(k)
    # print(offsets[principal_key])
    # print()

    return dict([(key, off.index(offsets[principal_key][k-1])+1)
                 for key, off in offsets.items() if offsets[principal_key][k-1] in off])


def _find_nearest_k(offsets, key, off):
    k = np.argmin(np.abs(np.array(offsets[key])-off))
    if offsets[key][k] > off:
        k -= 1
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
