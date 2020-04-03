#!/usr/bin/env python3.7
"""
This script defines the Factor Oracle class
based on the code in https://github.com/wangsix/vmo/blob/master/vmo/VMO/oracle.py
"""

import numpy as np
import scipy.spatial.distance as dist
import vmo.VMO.utility.misc as utl

from generation.factororacle import FactorOracle

class FO(FactorOracle):
    """ An implementation of the factor oracle
    """

    def __init__(self, **kwargs):
        super(FO, self).__init__(**kwargs)
        self.kind = 'r'

    def add_state(self, new_symbol):
        """

        :type self: oracle
        """
        self.sfx.append(0)
        self.rsfx.append([])
        self.trn.append([])
        self.lrs.append(0)
        self.data.append(new_symbol)

        self.n_states += 1

        i = self.n_states - 1

        self.trn[i - 1].append(i)
        k = self.sfx[i - 1]
        pi_1 = i - 1

        # Adding forward links
        while k is not None:
            _symbols = [self.data[state] for state in self.trn[k]]
            if self.data[i] not in _symbols:
                self.trn[k].append(i)
                pi_1 = k
                k = self.sfx[k]
            else:
                break

        if k is None:
            self.sfx[i] = 0
            self.lrs[i] = 0
        else:
            _query = [[self.data[state], state] for state in
                      self.trn[k] if self.data[state] == self.data[i]]
            _query = sorted(_query, key=lambda _query: _query[1])
            _state = _query[0][1]
            self.sfx[i] = _state
            self.lrs[i] = self._len_common_suffix(pi_1, self.sfx[i] - 1) + 1

        k = self._find_better(i, self.data[i - self.lrs[i]])
        if k is not None:
            self.lrs[i] += 1
            self.sfx[i] = k
        self.rsfx[self.sfx[i]].append(i)

        if self.lrs[i] > self.max_lrs[i - 1]:
            self.max_lrs.append(self.lrs[i])
        else:
            self.max_lrs.append(self.max_lrs[i - 1])

        self.avg_lrs.append(self.avg_lrs[i - 1] * ((i - 1.0) / (self.n_states - 1.0)) +
                            self.lrs[i] * (1.0 / (self.n_states - 1.0)))

    def accept(self, context):
        """ Check if the context could be accepted by the oracle
        
        Args:
            context: s sequence same type as the oracle data
        
        Returns:
            bAccepted: whether the sequence is accepted or not
            _next: the state where the sequence is accepted
        """
        _next = 0
        for _s in context:
            _data = [self.data[j] for j in self.trn[_next]]
            if _s in _data:
                _next = self.trn[_next][_data.index(_s)]
            else:
                return 0, _next
        return 1, _next

    def get_alphabet(self):
        alphabet = [self.data[i] for i in self.trn[0]]
        dictionary = dict(zip(alphabet, range(len(alphabet))))
        return dictionary

    @property
    def latent(self):
        latent = []
        for s in self.trn[0]:
            indices = set([s])
            indices = utl.get_rsfx(self, indices, s)
            latent.append(list(indices))
        return latent
