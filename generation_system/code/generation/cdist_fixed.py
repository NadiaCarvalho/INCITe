"""
Implementation of cdist with fixed weights
"""

import numpy as numpy
import scipy.spatial.distance as dist

def fixed_cdist(XA, XB, w, fw, metric='euclidean'):
    cols = [col for col, value in enumerate(fw) if value]



    return dist.cdist(XA, XB, metric=metric, w=w)
