"""
Normalization And Arrays
"""
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.impute import SimpleImputer


def flatten(newlist):
    """
    flatten a list with strings
    """
    ret = []
    for item in newlist:
        if isinstance(item, list):
            ret.extend(flatten(item))
        else:
            ret.append(item)
    return ret


def normalize_column(col, x_min, x_max):
    """
    Normalize a column of a matrix
    """
    if max(col) == min(col) and max(col) != 0:
        return [1. for item in col]

    nom = (col - min(col))*(x_max-x_min)
    denom = max(col) - min(col)
    if denom == 0:
        denom = 1
    return (nom/denom) + x_min


def normalize_dictionary(d, x_min, x_max):
    """
    Normalize a Dictionary
    """
    max_l = max(d.values())
    min_l = min(d.values())

    denom = max_l - min_l
    if denom == 0:
        denom = 1

    return {key: (value - min_l)*(x_max-x_min)/denom for key, value in d.items()}


def normalize(feat_list, x_min, x_max):
    """
    Get Normalization for a matrix between [x_min, x_max]
    """
    normalized_columns = []
    for col in list(zip(*feat_list)):
        normalized_columns.append(normalize_column(list(col), x_min, x_max))
    return [list(line) for line in list(zip(*normalized_columns))]


def normalize_weights(weights):
    """
    Normalize weight list
    """
    if len(weights) < 1:
        return weights

    if any(w < 0 for w in weights):
        weights = [float(w) + abs(min(weights)) for w in weights]
    return [float(w)/sum(weights) for w in weights]


def create_feat_array(events, weights=None, offset=True):
    """
    Create a feature Array from Events and clean values.
    Can use weights for which features to extract and offset
    if offset can be counted as a feature
    """
    events_dict = [event.to_feature_dict(weights, offset) for event in events]

    vec = DictVectorizer()
    features = vec.fit_transform(events_dict).toarray()
    features_names = vec.get_feature_names()

    imp = SimpleImputer(missing_values=np.nan,
                        strategy='constant', fill_value=10000)
    return imp.fit_transform(features), features_names


def events_to_features(events, weights=None,
                       normalization='st1-mt0', offset=True, flatten_feat=True):
    """
    Creating Feature Array and Weights for Oracle
    """
    features, features_names = create_feat_array(events, weights, offset)

    norm_features = []
    if normalization == 'st1-mt0':
        norm_features = normalize(features, -1, 1)
    else:
        norm_features = normalize(features, 0, 1)

    if len(features_names) == 1 and flatten_feat:
        features = [x for [x] in features]
        norm_features = [x for [x] in norm_features]

    weighted_fit = None
    if weights is not None:
        weighted_fit = np.zeros(len(features_names))
        for i, feat in enumerate(features_names):
            w_feat = [key for key in weights if feat.find(key) != -1]
            if len(w_feat) == 0:
                weighted_fit[i] = 0
            else:
                weighted_fit[i] = weights[w_feat[0]]

    return norm_features, features, features_names, weighted_fit


def get_columns_from_weights(weights, fixed_weights, features_names):
    """
    Get Columns and Weights (non-normalized)
    per weighted_viewpoints and features_names
    """
    columns_to_retain = []
    weights_per_column = []
    fixed_per_column = []
    feature_names_per_column = []
    for i, key in enumerate(features_names):
        new_key = key
        if '=' in key:
            new_key = key.split('=')[0]
        elif any(s in key for s in ['articulation', 'expressions.expression', 'ornamentation',
                                    'dynamic', 'chordPitches', 'pitches', 'pitchClass',
                                    'primeForm', 'pcOrdered']):
            new_key = key.split('_')[0]

        if (new_key in weights and weights[new_key] != 0
                or new_key in fixed_weights and fixed_weights[new_key]):
            columns_to_retain.append(i)

            is_fixed = False
            if new_key in fixed_weights:
                is_fixed = fixed_weights[new_key]
            fixed_per_column.append(is_fixed)

            weight = weights[new_key]
            if is_fixed:
                weight = max(weights.values()) + 1
            weights_per_column.append(weight)

            feature_names_per_column.append(key)

    return columns_to_retain, weights_per_column, fixed_per_column, feature_names_per_column
