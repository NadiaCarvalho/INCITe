#!/usr/bin/env python3.7
"""
This script defines the utils for the FO family algorithms
based on the code in https://github.com/wangsix/vmo/blob/master/vmo/VMO/oracle.py
"""

from generation.factororacle import FactorOracle
from generation.fo import FO
from generation.vmo import MO


class feature_array:
    def __init__(self, dim):
        self.data = np.zeros((100, dim))
        self.dim = dim
        self.capacity = 100
        self.size = 0

    def __getitem__(self, item):
        return self.data[item, :]

    def add(self, x):
        if self.size == self.capacity:
            self.capacity *= 4
            newdata = np.zeros((self.capacity, self.dim))
            newdata[:self.size, :] = self.data
            self.data = newdata

        self.data[self.size, :] = x
        self.size += 1

    def finalize(self):
        self.data = self.data[:self.size, :]


def _create_oracle(oracle_type, **kwargs):
    """A routine for creating a factor oracle."""
    if oracle_type == 'f':
        return FO(**kwargs)
    elif oracle_type == 'a':
        return MO(**kwargs)
    else:
        return MO(**kwargs)


def create_oracle(flag, threshold=0, dfunc='euclidean',
                  dfunc_handle=None, dim=1):
    return _create_oracle(flag, threshold=threshold, dfunc=dfunc,
                          dfunc_handle=dfunc_handle, dim=dim)


def _build_oracle(flag, oracle, input_data, suffix_method='inc'):
    if type(input_data) != np.ndarray or type(input_data[0]) != np.ndarray:
        input_data = np.array(input_data)

    if input_data.ndim != 2:
        input_data = np.expand_dims(input_data, axis=1)

    if flag == 'a':
        [oracle.add_state(obs, suffix_method) for obs in input_data]
        oracle.f_array.finalize()
    else:
        [oracle.add_state(obs) for obs in input_data]
    return oracle


def build_oracle(input_data, flag,
                 threshold=0, suffix_method='inc',
                 feature=None, weights=None, dfunc='cosine',
                 dfunc_handle=None, dim=1):
    # initialize weights if needed
    if weights is None:
        weights = {}
        weights.setdefault(feature, 1.0)

    if flag == 'a':
        oracle = _create_oracle(flag, threshold=threshold, dfunc=dfunc,
                                dfunc_handle=dfunc_handle, dim=dim)
        oracle = _build_oracle(flag, oracle, input_data, suffix_method)
    elif flag == 'f' or flag == 'v':
        oracle = _create_oracle(flag, threshold=threshold, dfunc=dfunc,
                                dfunc_handle=dfunc_handle, dim=dim)
        oracle = _build_oracle(flag, oracle, input_data)
    else:
        oracle = _create_oracle('a', threshold=threshold, dfunc=dfunc,
                                dfunc_handle=dfunc_handle, dim=dim)
        oracle = _build_oracle(flag, oracle, input_data, suffix_method)

    return oracle


def find_threshold(input_data, r=(0, 1, 0.1), method='ir', flag='a',
                   suffix_method='inc', alpha=1.0, feature=None, ir_type='cum',
                   dfunc='cosine', dfunc_handle=None, dim=1,
                   verbose=False, entropy=False):
    if method == 'ir':
        return find_threshold_ir(input_data, r, flag, suffix_method, alpha,
                                 feature, ir_type, dfunc, dfunc_handle, dim,
                                 verbose, entropy)


def find_threshold_ir(input_data, r=(0, 1, 0.1), flag='a', suffix_method='inc',
                      alpha=1.0, feature=None, ir_type='cum',
                      dfunc='cosine', dfunc_handle=None, dim=1,
                      verbose=False, entropy=False):
    thresholds = np.arange(r[0], r[1], r[2])
    irs = []
    if entropy:
        h0_vec = []
        h1_vec = []
    for t in thresholds:
        if verbose:
            print('Testing threshold:', t)
        tmp_oracle = build_oracle(input_data, flag=flag, threshold=t,
                                  suffix_method=suffix_method, feature=feature,
                                  dfunc=dfunc, dfunc_handle=dfunc_handle, dim=dim)
        tmp_ir, h0, h1 = tmp_oracle.IR(ir_type=ir_type, alpha=alpha)
        irs.append(tmp_ir.sum())
        if entropy:
            h0_vec.append(h0.sum())
            h1_vec.append(h1.sum())
    # now pair irs and thresholds in a vector, and sort by ir
    ir_thresh_pairs = [(a, b) for a, b in zip(irs, thresholds)]
    pairs_return = ir_thresh_pairs
    ir_thresh_pairs = sorted(ir_thresh_pairs, key=lambda x: x[0],
                             reverse=True)
    if entropy:
        return ir_thresh_pairs[0], pairs_return, h0_vec, h1_vec
    else:
        return ir_thresh_pairs[0], pairs_return
