#!/usr/bin/env python3.7
"""
This script defines the generation algorithm for synchronization of various Oracles
"""

import random

import numpy as np

from generation.factor_oracle import FactorOracle

def sync_generate(oracles, offsets, seq_len=10, p=0.5, k=1, LRS=0, weight=None):
    """
    Generate synchronized lines from various oracles
    """
    sync_lrs_oracle = oracles.values()
    print([(key, len(part)) for key, part in offsets.items()])



    #trn = oracle.basic_attributes['trn'][:]
    #sfx = oracle.basic_attributes['sfx'][:]
    #lrs = oracle.basic_attributes['lrs'][:]
    #rsfx = oracle.basic_attributes['rsfx'][:]

