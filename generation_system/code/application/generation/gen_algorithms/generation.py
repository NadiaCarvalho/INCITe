#!/usr/bin/env python3.7
"""
This script defines the generation algorithm from an Oracle
based on the code in https://github.com/wangsix/vmo/blob/master/vmo/generate.py
"""
import random

import numpy as np

import logging

from application.generation.oracles.factor_oracle import FactorOracle


def generate(oracle, seq_len, p=0.5, k=1, LRS=0, weight=None):
    """
    Generate a sequence based on traversing an oracle.
    :param oracle: a indexed vmo object
    :param seq_len: the length of the returned improvisation sequence
    :param p: a float between (0,1) representing the probability using the forward links.
    :param k: the starting improvisation time step in oracle
    :param LRS: the length of minimum longest repeated suffixes allowed to jump
    :param weight:
            None: choose uniformly among all the possible sfx/rsfx given
                current state.
            "max": always choose the sfx/rsfx having the longest LRS.
            "weight": choose sfx/rsfx in a way that favors longer ones than
            shorter ones.
    :return:
            s: a list containing the sequence generated, each element represents a
            state.
            kend: the ending state.
            ktrace:
    """

    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.warning(str(oracle))
    logging.warning('PERC: ' + str(p))
    logging.warning('LRS: ' + str(LRS))

    trn = oracle.basic_attributes['trn'][:]
    sfx = oracle.basic_attributes['sfx'][:]
    lrs = oracle.basic_attributes['lrs'][:]
    rsfx = oracle.basic_attributes['rsfx'][:]

    s = []
    ktrace = [1]

    for _i in range(seq_len):
        logging.warning('i: ' + str(_i))
        logging.warning('i: ' + str(k))

        # generate each state
        if sfx[k] != 0 and sfx[k] is not None:
            if (random.random() < p):
                # copy forward according to transitions
                I = trn[k]
                if len(I) == 0:
                    # if last state, choose a suffix
                    k = sfx[k]
                    ktrace.append(k)
                    I = trn[k]
                sym = I[int(np.floor(random.random() * len(I)))]
                s.append(sym)  # Why (sym-1) before?
                k = sym
                ktrace.append(k)
            else:
                # copy any of the next symbols
                ktrace.append(k)
                _k = k
                k_vec = []
                k_vec = _find_links(k_vec, sfx, rsfx, _k)
                logging.warning('kvec: ' + str(k_vec))
                k_vec = [_i for _i in k_vec if lrs[_i] >= LRS]
                logging.warning('kvec > LRS: ' + str(k_vec))
                lrs_vec = [lrs[_i] for _i in k_vec]
                logging.warning('lrs_vec: ' + str(lrs_vec))
                if len(k_vec) > 0:  # if a possibility found, len(I)
                    if weight == 'weight':
                        max_lrs = np.amax(lrs_vec)
                        query_lrs = max_lrs - np.floor(random.expovariate(1))

                        if query_lrs in lrs_vec:
                            _tmp = np.where(lrs_vec == query_lrs)[0]
                            _tmp = _tmp[int(
                                np.floor(random.random() * len(_tmp)))]
                            sym = k_vec[_tmp]
                        else:
                            _tmp = np.argmin(abs(
                                np.subtract(lrs_vec, query_lrs)))
                            sym = k_vec[_tmp]

                    elif weight == 'max':
                        sym = k_vec[np.argmax([lrs[_i] for _i in k_vec])]
                    else:
                        sym = k_vec[int(
                            np.floor(random.random() * len(k_vec)))]

                    if sym == len(sfx) - 1:
                        sym = sfx[sym] + 1
                    else:
                        s.append(sym + 1)
                    k = sym + 1
                    ktrace.append(k)
                else:  # otherwise continue
                    if k < len(sfx) - 1:
                        sym = k + 1
                    else:
                        sym = sfx[k] + 1
                    s.append(sym)
                    k = sym
                    ktrace.append(k)
        else:
            if k < len(sfx) - 1:
                s.append(k + 1)
                k += 1
                ktrace.append(k)
            else:
                sym = sfx[k] + 1
                s.append(sym)
                k = sym
                ktrace.append(k)
        if k >= len(sfx) - 1:
            k = 0

    logging.warning('ktrace: ' + str(ktrace))
    logging.warning('seq: ' + str(s))
    kend = k
    return s, kend, ktrace


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
