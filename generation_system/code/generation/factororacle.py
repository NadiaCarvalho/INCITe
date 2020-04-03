#!/usr/bin/env python3.7
"""
This script defines the Factor Oracle class
based on the code in https://github.com/wangsix/vmo/blob/master/vmo/VMO/oracle.py
"""

import numpy as np
import scipy.spatial.distance as dist
import vmo.VMO.utility.misc as utl

class FactorOracle(object):
    """ The base class for the FO(factor oracle) and MO(variable markov oracle)
    
    Attributes:
        sfx: a list containing the suffix link of each state.
        trn: a list containing the forward links of each state as a list.
        rsfx: a list containing the reverse suffix links of each state 
            as a list.
        lrs: the value of longest repeated suffix of each state.
        data: the symobols associated with the direct link 
            connected to each state.
        compror: a list of tuples (i, i-j), i is the current coded position,
            i-j is the length of the corresponding coded words.
        code: a list of tuples (len, pos), len is the length of the 
            corresponding coded words, pos is the position where the coded
            words starts.
        seg: same as code but non-overlapping.
        f_array: (For kind 'a' and 'v'): a list containing the feature array
        latent: (For kind 'a' and 'v'): a list of lists with each sub-list
            containing the indexes for each symbol.
        kind: 
            'a': Variable Markov oracle
            'f': repeat oracle
            'v': Centroid-based oracle (under test)
        n_states: number of total states, also is length of the input 
            sequence plus 1.
        max_lrs: the longest lrs so far.
        avg_lrs: the average lrs so far.
        name: the name of the oracle.
        params: a python dictionary for different feature and distance settings.
            keys:
                'thresholds': the minimum value for separating two values as 
                    different symbols.
                'weights': a dictionary containing different weights for features
                    used.
                'dfunc': the distance function.
    """

    def __init__(self, **kwargs):
        # Basic attributes
        self.sfx = []
        self.trn = []
        self.rsfx = []
        self.lrs = []
        self.data = []

        # Compression attributes
        self.compror = []
        self.code = []
        self.seg = []

        # Object attributes
        self.kind = 'f'
        self.name = ''

        # Oracle statistics
        self.n_states = 1
        self.max_lrs = []
        self.max_lrs.append(0)
        self.avg_lrs = []
        self.avg_lrs.append(0.0)

        # Oracle parameters
        self.params = {
            'threshold': 0,
            'dfunc': 'cosine',
            'dfunc_handle': None,
            'dim': 1
        }
        self.update_params(**kwargs)

        # Adding zero state
        self.sfx.append(None)
        self.rsfx.append([])
        self.trn.append([])
        self.lrs.append(0)
        self.data.append(0)

    def reset(self, **kwargs):
        self.update_params(**kwargs)
        # Basic attributes
        self.sfx = []
        self.trn = []
        self.rsfx = []
        self.lrs = []
        self.data = []

        # Compression attributes
        self.compror = []
        self.code = []
        self.seg = []

        # Object attributes
        self.kind = 'f'
        self.name = ''

        # Oracle statistics
        self.n_states = 1
        self.max_lrs = []
        self.max_lrs.append(0)
        self.avg_lrs = []
        self.avg_lrs.append(0.0)

        # Adding zero state
        self.sfx.append(None)
        self.rsfx.append([])
        self.trn.append([])
        self.lrs.append(0)
        self.data.append(0)

    def update_params(self, **kwargs):
        """Subclass this"""
        self.params.update(kwargs)

    def add_state(self, new_data):
        """Subclass this"""
        pass

    def _encode(self):
        _code = []
        _compror = []
        if not self.compror:
            j = 0
        else:
            j = self.compror[-1][0]

        i = j
        while j < self.n_states - 1:
            while i < self.n_states - 1 and self.lrs[i + 1] >= i - j + 1:
                i += 1
            if i == j:
                i += 1
                _code.append([0, i])
                _compror.append([i, 0])
            else:
                _code.append([i - j, self.sfx[i] - i + j + 1])
                _compror.append([i, i - j])
            j = i
        return _code, _compror

    def encode(self):
        _c, _cmpr = self._encode()
        self.code.extend(_c)
        self.compror.extend(_cmpr)

        return self.code, self.compror

    def segment(self):
        """An non-overlap version Compror"""

        if not self.seg:
            j = 0
        else:
            j = self.seg[-1][1]
            last_len = self.seg[-1][0]
            if last_len + j > self.n_states:
                return

        i = j
        while j < self.n_states - 1:
            while not (not (i < self.n_states - 1) or not (self.lrs[i + 1] >= i - j + 1)):
                i += 1
            if i == j:
                i += 1
                self.seg.append((0, i))
            else:
                if (self.sfx[i] + self.lrs[i]) <= i:
                    self.seg.append((i - j, self.sfx[i] - i + j + 1))

                else:
                    _i = j + i - self.sfx[i]
                    self.seg.append((_i - j, self.sfx[i] - i + j + 1))
                    _j = _i
                    while not (not (_i < i) or not (self.lrs[_i + 1] - self.lrs[_j] >= _i - _j + 1)):
                        _i += 1
                    if _i == _j:
                        _i += 1
                        self.seg.append((0, _i))
                    else:
                        self.seg.append((_i - _j, self.sfx[_i] - _i + _j + 1))
            j = i
        return self.seg

    def _ir(self, alpha=1.0):
        code, _ = self.encode()
        cw = np.zeros(len(code))  # Number of code words
        for i, c in enumerate(code):
            cw[i] = c[0] + 1

        c0 = [1 if x[0] == 0 else 0 for x in self.code]
        h0 = np.log2(np.cumsum(c0))

        h1 = np.zeros(len(cw))

        for i in range(1, len(cw)):
            h1[i] = utl.entropy(cw[0:i + 1])

        ir = alpha * h0 - h1

        return ir, h0, h1

    def _ir_fixed(self, alpha=1.0):
        code, _ = self.encode()

        h0 = np.log2(self.num_clusters())

        if self.max_lrs[-1] == 0:
            h1 = np.log2(self.n_states - 1)
        else:
            h1 = np.log2(self.n_states - 1) + np.log2(self.max_lrs[-1])

        BL = np.zeros(self.n_states - 1)
        j = 0
        for i in range(len(code)):
            if self.code[i][0] == 0:
                BL[j] = 1
                j += 1
            else:
                L = code[i][0]
                BL[j:j + L] = L  # range(1,L+1)
                j = j + L
        ir = alpha * h0 - h1 / BL
        ir[ir < 0] = 0
        return ir, h0, h1

    def _ir_cum(self, alpha=1.0):
        code, _ = self.encode()

        N = self.n_states

        cw0 = np.zeros(N - 1)  # cw0 counts the appearance of new states only
        cw1 = np.zeros(N - 1)  # cw1 counts the appearance of all compror states
        BL = np.zeros(N - 1)  # BL is the block length of compror codewords

        j = 0
        for i in range(len(code)):
            if self.code[i][0] == 0:
                cw0[j] = 1
                cw1[j] = 1
                BL[j] = 1
                j += 1
            else:
                L = code[i][0]
                cw1[j] = 1
                BL[j:j + L] = L  # range(1,L+1)
                j = j + L

        h0 = np.log2(np.cumsum(cw0))
        h1 = np.log2(np.cumsum(cw1))
        h1 = h1 / BL
        ir = alpha * h0 - h1
        ir[ir < 0] = 0

        return ir, h0, h1

    def _ir_cum2(self, alpha=1.0):
        code, _ = self.encode()

        N = self.n_states
        BL = np.zeros(N - 1)  # BL is the block length of compror codewords

        h0 = np.log2(np.cumsum(
            [1.0 if sfx == 0 else 0.0 for sfx in self.sfx[1:]])
        )
        """
        h1 = np.array([h if m == 0 else h+np.log2(m) 
                       for h,m in zip(h0,self.lrs[1:])])
        h1 = np.array([h if m == 0 else h+np.log2(m) 
                       for h,m in zip(h0,self.max_lrs[1:])])
        h1 = np.array([h if m == 0 else h+np.log2(m) 
                       for h,m in zip(h0,self.avg_lrs[1:])])
        """
        h1 = np.array([np.log2(i + 1) if m == 0 else np.log2(i + 1) + np.log2(m)
                       for i, m in enumerate(self.max_lrs[1:])])

        j = 0
        for i in range(len(code)):
            if self.code[i][0] == 0:
                BL[j] = 1
                j += 1
            else:
                L = code[i][0]
                BL[j:j + L] = L  # range(1,L+1)
                j = j + L

        h1 = h1 / BL
        ir = alpha * h0 - h1
        ir[ir < 0] = 0  # Really a HACK here!!!!!
        return ir, h0, h1

    def _ir_cum3(self, alpha=1.0):

        h0 = np.log2(np.cumsum(
            [1.0 if sfx == 0 else 0.0 for sfx in self.sfx[1:]])
        )
        h1 = np.array([h if m == 0 else (h + np.log2(m)) / m
                       for h, m in zip(h0, self.lrs[1:])])

        ir = alpha * h0 - h1
        ir[ir < 0] = 0  # Really a HACK here!!!!!
        return ir, h0, h1

    def IR(self, alpha=1.0, ir_type='cum'):
        if ir_type == 'cum':
            return self._ir_cum(alpha)
        elif ir_type == 'all':
            return self._ir(alpha)
        elif ir_type == 'fixed':
            return self._ir_fixed(alpha)
        elif ir_type == 'cum2':
            return self._ir_cum2(alpha)
        elif ir_type == 'cum3':
            return self._ir_cum3(alpha)

    def num_clusters(self):
        return len(self.rsfx[0])

    def threshold(self):
        if self.params.get('threshold'):
            return int(self.params.get('threshold'))
        else:
            raise ValueError("Threshold is not set!")

    def dfunc(self):
        if self.params.get('dfunc'):
            return self.params.get('dfunc')
        else:
            raise ValueError("dfunc is not set!")

    def dfunc_handle(self, a, b_vec):
        fun = self.params['dfunc_handle']
        return fun(a, b_vec)

    def _len_common_suffix(self, p1, p2):
        if p2 == self.sfx[p1]:
            return self.lrs[p1]
        else:
            while self.sfx[p2] != self.sfx[p1] and p2 != 0:
                p2 = self.sfx[p2]
        return min(self.lrs[p1], self.lrs[p2])

    def _find_better(self, i, symbol):
        self.rsfx[self.sfx[i]].sort()
        for j in self.rsfx[self.sfx[i]]:
            if (self.lrs[j] == self.lrs[i] and
                        self.data[j - self.lrs[i]] == symbol):
                return j
        return None


class FactorOracle:
    def __init__(self):
        self.sfx = []
        self.trn = []
        self.rsfx = []
        self.lrs = []
        self.data = []