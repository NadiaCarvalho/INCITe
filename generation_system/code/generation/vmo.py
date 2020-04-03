#!/usr/bin/env python3.7
"""
This script defines the VMO oracle class
based on the code in https://github.com/wangsix/vmo/blob/master/vmo/VMO/oracle.py
"""

import numpy as np
import scipy.spatial.distance as dist
import vmo.VMO.utility.misc as utl

from generation.factororacle import FactorOracle

class MO(FactorOracle):
    def __init__(self, **kwargs):
        super(MO, self).__init__(**kwargs)
        self.kind = 'a'
        self.f_array = feature_array(self.params['dim'])
        self.f_array.add(np.zeros(self.params['dim'], ))
        self.data[0] = None
        self.latent = []

    def reset(self, **kwargs):
        super(MO, self).reset(**kwargs)

        self.kind = 'a'
        # self.f_array = [0]
        self.f_array = feature_array(self.params['dim'])
        self.f_array.add(np.zeros(self.params['dim'], ))
        self.data[0] = None
        self.latent = []

    def add_state(self, new_data, method='inc'):
        """Create new state and update related links and compressed state"""
        self.sfx.append(0)
        self.rsfx.append([])
        self.trn.append([])
        self.lrs.append(0)

        # Experiment with pointer-based
        self.f_array.add(new_data)

        self.n_states += 1
        i = self.n_states - 1

        # assign new transition from state i-1 to i
        self.trn[i - 1].append(i)
        k = self.sfx[i - 1]
        pi_1 = i - 1

        # iteratively backtrack suffixes from state i-1
        if method == 'inc':
            suffix_candidate = 0
        elif method == 'complete':
            suffix_candidate = []
        else:
            suffix_candidate = 0

        while k is not None:

            if self.params['dfunc'] == 'other':
                # dvec = self.dfunc_handle([new_data],
                #                          self.f_array[self.trn[k]])[0]
                dvec = dist.cdist([new_data],
                                  self.f_array[self.trn[k]],
                                  metric=self.params['dfunc_handle'])[0]
            else:
                dvec = dist.cdist([new_data],
                                  self.f_array[self.trn[k]],
                                  metric=self.params['dfunc'])[0]

            I = np.where(dvec < self.params['threshold'])[0]
            if len(I) == 0:  # if no transition from suffix
                self.trn[k].append(i)  # Add new forward link to unvisited state
                pi_1 = k
                if method != 'complete':
                    k = self.sfx[k]
            else:
                if method == 'inc':
                    if I.shape[0] == 1:
                        suffix_candidate = self.trn[k][I[0]]
                    else:
                        suffix_candidate = self.trn[k][I[np.argmin(dvec[I])]]
                    break
                elif method == 'complete':
                    suffix_candidate.append((self.trn[k][I[np.argmin(dvec[I])]],
                                             np.min(dvec)))
                else:
                    suffix_candidate = self.trn[k][I[np.argmin(dvec[I])]]
                    break

            if method == 'complete':
                k = self.sfx[k]

        if method == 'complete':
            if not suffix_candidate:
                self.sfx[i] = 0
                self.lrs[i] = 0
                self.latent.append([i])
                self.data.append(len(self.latent) - 1)
            else:
                sorted_suffix_candidates = sorted(suffix_candidate,
                                                  key=lambda suffix: suffix[1])
                self.sfx[i] = sorted_suffix_candidates[0][0]
                self.lrs[i] = self._len_common_suffix(pi_1, self.sfx[i] - 1) + 1
                self.latent[self.data[self.sfx[i]]].append(i)
                self.data.append(self.data[self.sfx[i]])
        else:
            if k is None:
                self.sfx[i] = 0
                self.lrs[i] = 0
                self.latent.append([i])
                self.data.append(len(self.latent) - 1)
            else:
                self.sfx[i] = suffix_candidate
                self.lrs[i] = self._len_common_suffix(pi_1, self.sfx[i] - 1) + 1
                self.latent[self.data[self.sfx[i]]].append(i)
                self.data.append(self.data[self.sfx[i]])

        # Temporary adjustment
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