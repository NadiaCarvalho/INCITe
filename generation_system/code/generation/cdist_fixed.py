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

def distance_between_windowed_features(XA, XB):
    """
    Windowed Distance between two matrixes using Euclidean Distance
    """
    if len(XB) == len(XA):
        return np.linalg.norm(np.array(XA), np.array(XB), ord='fro')

    max_matrix = XB
    min_matrix = XA
    if len(XB) < len(XA):
        max_matrix = XA
        min_matrix = XB

    window = len(max_matrix) - len(min_matrix)

    distances = []
    for i in range(window):
        distances.append(np.linalg.norm(np.array(min_matrix) - np.array(max_matrix[i : len(min_matrix) + i]), ord='fro'))

    if len(XB) < len(XA):
        return sum(distances)/len(distances)
    else:
        return min(distances)

