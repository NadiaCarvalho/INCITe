"""
Statistics
"""
import numpy as np

import  application.representation.utils.features as utils


ARRAY_VALUES = ['expressions.articulation', 'expressions.expression',
                'expressions.ornamentation', 'expressions.dynamic', 'pitch.chordPitches', 'basic.pitches',
                'classes.pitchClass', 'basic.primeForm', 'classes.pcOrdered']

FIXED_FEATURES = ['posinbar', 'keysig']


def statistic_features(events):
    """
    Get Statistics from Features
    """
    features, features_names = utils.create_feat_array(events)
    columns_values = list(zip(*features))
    statistic_dict = {}
    for i, feat in enumerate(features_names):
        values = list(
            zip(*np.unique(list(columns_values[i]), return_counts=True)))

        if '=' in feat:
            info = feat.split('=')
            if not info[0] in statistic_dict:
                statistic_dict[info[0]] = []
            if len(values) == 1:
                statistic_dict[info[0]].append((info[1], values[0][1]))
            else:
                ret = [item for item in values if item[0] == 1.0]
                if len(ret) > 0:
                    statistic_dict[info[0]].append((info[1], ret[0][1]))
        elif any(s in feat for s in ARRAY_VALUES):
            cat = [s for s in ARRAY_VALUES if s in feat]
            if not cat[0] in statistic_dict:
                statistic_dict[cat[0]] = []
            value_1 = list(filter(lambda x: 1.0 in x, values))
            if value_1 != []:
                statistic_dict[cat[0]].append(
                    (feat.split('_')[-1], value_1[0][1]))
        elif feat != 'offset':
            statistic_dict[feat] = values

    return get_percentage_from_statistics(statistic_dict, len(events)), features, features_names


def get_percentage_from_statistics(statistic_dict, len_events):
    """
    Get Percentages as Specific Statistics from
    Viewpoint Statistics
    """
    new_stats_dict = {}
    for key, values in statistic_dict.items():
        unique_percentages = [
            round(float(x[1])/len_events * 100, 2) for x in values]
        new_stats_dict[key] = {
            'unique_values': values,
            'number_of_unique_values': len(values),
            'total_percentages': round(float(sum([x[1] for x in values]))/len_events * 100, 2),
            'unique_percentages': unique_percentages,
            'media_percentages': sum(unique_percentages)/len(unique_percentages),
            'median_percentages': np.median(unique_percentages),
            'variance': round(np.var(unique_percentages), 2),
            'standard_deviation': round(np.std(unique_percentages), 2),
        }
    return new_stats_dict


def calculate_part_weights(statistic_dict, key_stats='parts'):
    """
    To Reuse code
    """
    if key_stats in statistic_dict:
        std_parts = dict([(key, stats['standard_deviation'])
                                for key, stats in statistic_dict[key_stats].items()])
        std_parts_normed = utils.normalize_dictionary(
            std_parts, x_min=0, x_max=100)
        for key, stats in statistic_dict[key_stats].items():
            stats['weight'] = std_parts_normed[key]
            stats['fixed'] = False
            if 'posinbar' in key:
                stats['fixed'] = True


def calculate_automatic_viewpoints(statistic_dict):
    """
    Calculate Automatic Weights from Statistics
    """
    calculate_part_weights(statistic_dict)
    calculate_part_weights(statistic_dict, 'vertical')
