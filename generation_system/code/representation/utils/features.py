"""
Normalization And Arrays
"""
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.impute import SimpleImputer


def normalize_column(col, x_min, x_max):

    if max(col) == min(col) and max(col) != 0:
        return [1. for item in col]

    nom = (col - min(col))*(x_max-x_min)
    denom = max(col) - min(col)
    if denom == 0:
        denom = 1
    return (nom/denom) + x_min


def normalize(feat_list, x_min, x_max):
    """
    Get Normalization for
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


def create_feature_array_events(events, weights=None, normalization='st1-mt0', offset=True, flatten=True):
    """
    Creating Feature Array and Weights for Oracle
    """
    features, features_names = create_feat_array(events, weights, offset)

    norm_features = []
    if normalization == 'st1-mt0':
        norm_features = normalize(features, -1, 1)
    else:
        norm_features = normalize(features, 0, 1)

    if len(features_names) == 1 and flatten:
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


def create_feat_array(events, weights=None, offset=True):
    events_dict = [event.to_feature_dict(weights, offset) for event in events]

    vec = DictVectorizer()
    features = vec.fit_transform(events_dict).toarray()
    features_names = vec.get_feature_names()

    imp = SimpleImputer(missing_values=np.nan,
                        strategy='constant', fill_value=10000)
    return imp.fit_transform(features), features_names
