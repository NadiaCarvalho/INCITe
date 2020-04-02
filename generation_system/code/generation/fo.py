#!/usr/bin/env python3.7
"""
This script defines the Factor Oracle (FO) class
based on the code in https://github.com/wangsix/vmo/blob/master/vmo/VMO/oracle.py
"""

class FactorOracle:
    def __init__(self):
        self.sfx = []
        self.trn = []
        self.rsfx = []
        self.lrs = []
        self.data = []