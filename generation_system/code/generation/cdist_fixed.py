"""
Implementation of cdist with fixed weights
"""

import numpy as np
import scipy.spatial.distance as dist


def fixed_cdist(XA, XB, w, fw, metric='euclidean'):
    """
    Calculate distance between two feature arrays,
    in which some of the features have to be absolute
    and the others are weighted
    """
    cols = [col for col, value in enumerate(fw) if value]
    result = dist.cdist(XA, XB, metric=metric, w=w)
    if cols != []:
        distance_of_fixed = dist.cdist(
            np.array(XA)[:, cols], XB[:, cols], metric=metric)
        for i, res in enumerate(result):
            for j, _ in enumerate(res):
                if distance_of_fixed[i][j] != 0:
                    result[i][j] = 100000
    return result
