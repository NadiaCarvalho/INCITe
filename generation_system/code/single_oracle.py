"""
"""
import os
import time

import generation.gen_algorithms.generation as gen
import generation.plot_fo as gen_plot
import generation.utils as gen_utils
from generation.cdist_fixed import distance_between_windowed_features
from representation.conversor.score_conversor import ScoreConversor
from representation.events.linear_event import LinearEvent


def get_single_part_features(application, information, line):
    """
    Get Part Features
    """
    normed_features = []
    original_features = []

    for music, _tuple in application.music.items():
        parser = _tuple[0]

        i = 0
        for key, events in parser.get_part_events().items():
            if len(events) > 0 and i == line:

                # Get Start and End Indexes
                start_index = application.indexes_first[music]['parts'][i]
                finish_index = start_index + len(events)

                normed_features.extend(
                    information['selected_normed'][start_index:finish_index])
                original_features.extend(
                    information['selected_original'][start_index:finish_index])
                break
            elif len(events) > 0:
                i += 1

    return normed_features, original_features


def construct_single_oracle(application, line):
    """
    Construct Oracle from Information
    """
    part_information = application.music_information['parts']
    features_names = part_information['selected_features_names']
    weights = part_information['normed_weights']
    fixed_weights = part_information['fixed_weights']

    # Get Normed and Original Features
    normed_features, original_features = get_single_part_features(application,
                                                                  part_information, line)

    thresh = gen_utils.find_threshold(
        normed_features, weights=weights,
        fixed_weights=fixed_weights,
        dim=len(features_names), entropy=True)

    oracle = gen_utils.build_oracle(
        normed_features, flag='a', features=features_names,
        weights=weights, fixed_weights=fixed_weights,
        dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])

    image = gen_plot.start_draw(oracle)
    name = r'data\myexamples\oracle' + '.PNG'
    image.save(name)

    application.oracles_information['single_oracle'] = {
        'oracle': oracle,
        'normed_features': normed_features,
        'original_features': original_features,
        'features_names': features_names
    }


def generate_sequences_single(information, num_seq):
    """
    Generate Sequences
    """
    ordered_sequences = []

    i = 0
    while i < num_seq:
        sequence, kend, ktrace = gen.generate(
            oracle=information['oracle'], seq_len=100, p=0.5, k=0, LRS=3)
        if len(sequence) > 0:
            dist = distance_between_windowed_features(
                [information['normed_features'][state-1]
                    for state in sequence],
                information['normed_features'])
            ordered_sequences.append((sequence, dist))
            i += 1

    ordered_sequences.sort(key=lambda tup: tup[1])
    return ordered_sequences


def generate_from_single(application, num_seq):
    """
    Generate Music From a Single Oracle
    """
    information = application.oracles_information['single_oracle']

    original_sequence = range(len(information['original_features']))
    linear_score_generator(original_sequence, information['original_features'],
                           information['features_names'], name='original', start=0)

    localtime = time.asctime(time.localtime(time.time()))
    localtime = '_'.join(localtime.split(' '))
    localtime = '-'.join(localtime.split(':'))

    ordered_sequences = generate_sequences_single(
        information, num_seq)
    # Generate Scores of Ordered Sequences
    for i, (sequence, dist) in enumerate(ordered_sequences):
        name = 'gen_' + localtime + '_' + \
            str(i) + '_distance_' + str(dist) + '.xml'
        linear_score_generator(
            sequence, information['original_features'],
            information['features_names'], name=name)


def linear_score_generator(sequence, o_information, feature_names, name='', start=-1):
    """
    Score Generator for Single Line
    """
    sequenced_events = [LinearEvent(
        from_list=o_information[state+start], features=feature_names) for state in sequence]
    if len(sequenced_events) > 0:
        score = ScoreConversor()
        score.parse_events(
            sequenced_events, new_part=True, new_voice=True)
        # score.stream.show()
        path = os.sep.join([os.getcwd(), 'data', 'generations', name])
        fp = score.stream.write(fp=path)
