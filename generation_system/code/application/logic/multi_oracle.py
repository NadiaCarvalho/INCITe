"""
Multiple part Oracle and Sequence Generator
"""
import collections
import os
import time
import random

import numpy as np

import application.logic.generation.gen_algorithms.multi_oracle_gen as multi_gen
import application.logic.generation.plot_fo as gen_plot
import application.logic.generation.utils as gen_utils
from application.logic.generation.cdist_fixed import distance_between_windowed_features
from application.logic.representation.conversor.score_conversor import parse_multiple
from application.logic.representation.events.linear_event import PartEvent
from application.logic.representation.parsers.utils import get_last_x_events_that_are_notes_before_index


def get_multiple_part_features(application, part_info, vert_info):
    """
    Get Multiple Part Features
    """
    ev_offsets = collections.OrderedDict()
    normed_features = collections.OrderedDict()
    original_features = collections.OrderedDict()

    keys_for_parts = application.principal_music[0].get_part_events().keys()

    for music, _tuple in application.music.items():
        parser = _tuple[0]
        last_offset = 0
        if ev_offsets != {}:
            last_offset = max([part_off[-1]
                               for part_off in ev_offsets.values()])

        i = 0
        for key, events in parser.get_part_events().items():
            if len(events) > 0:
                if key in keys_for_parts:
                    start_index = application.indexes_first[music]['parts'][i]
                    finish_index = start_index + len(events)

                    if key not in normed_features:
                        normed_features[key] = []
                        ev_offsets[key] = []
                        original_features[key] = []

                    normed_features[key].extend(
                        part_info['selected_normed'][start_index:finish_index])
                    original_features[key].extend(
                        part_info['selected_original'][start_index:finish_index])
                    ev_offsets[key].extend(
                        [ev.get_offset() + last_offset for ev in events])
                i += 1

        interpart_events = parser.get_interpart_events()
        if len(interpart_events) > 0:
            start_index = application.indexes_first[music]['inter-part']
            finish_index = start_index + len(interpart_events)

            if 'inter-part' not in normed_features:
                normed_features['inter-part'] = []
                ev_offsets['inter-part'] = []

            normed_features['inter-part'].extend(
                vert_info['selected_normed'][start_index:finish_index])
            ev_offsets['inter-part'].extend(
                [ev.get_offset() + last_offset for ev in interpart_events])

    return normed_features, original_features, ev_offsets


def construct_multi_oracles(application):
    """
    Construct Multiple Oracles from Information
    """
    part_information = application.music_information['parts']
    vert_information = application.music_information['inter-part']

    normed_features, original_features, ev_offsets = get_multiple_part_features(
        application, part_information, vert_information)

    oracles = collections.OrderedDict()

    for key, part in normed_features.items():
        features_names = part_information['selected_features_names']
        weights = part_information['normed_weights']
        fixed_weights = part_information['fixed_weights']
        if key == 'inter-part':
            features_names = vert_information['selected_features_names']
            weights = vert_information['normed_weights']
            fixed_weights = vert_information['fixed_weights']

        thresh = gen_utils.find_threshold(
            part, weights=weights, fixed_weights=fixed_weights,
            dim=len(features_names), entropy=True)
        oracles[key] = gen_utils.build_oracle(
            part, flag='a', features=features_names,
            weights=weights, fixed_weights=fixed_weights,
            dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])

    # oracles.move_to_end('inter-part', last=True)
    # image = gen_plot.start_draw(oracles, ev_offsets)
    # name = r'data\oracles\oracle' + '.PNG'
    # image.save(name)

    application.oracles_information['multiple_oracles'] = {
        'oracles': oracles,
        'normed_features': normed_features,
        'original_features': original_features,
        'features_names': part_information['selected_features_names'],
        'offsets': ev_offsets
    }


def generate_sequences_multiple(information, num_seq, seq_len=10, start=-1):
    """
    Generate Sequences
    """
    ordered_sequences = []

    i = 0
    while i < num_seq:
        sequences, ktraces = multi_gen.sync_generate(
            information['oracles'], information['offsets'], seq_len=seq_len, p=random.uniform(0.3, 0.5), k=-1)

        flag = all(len(sequence) > 0 for sequence in sequences.values())
        if flag:
            distances = []
            distances_2 = []
            for key, sequence in sequences.items():
                normed_feats = information['normed_features'][key]
                if key != 'inter-part':
                    orig_feats = information['original_features'][key]

                seq = list(
                    map(lambda x: x + start if not isinstance(x, str) else x, sequence))
                filter_strings = [s for s in seq if not isinstance(s, str)]

                if (any(s >= len(normed_feats) for s in filter_strings) or
                          (len(seq) - len(filter_strings)) > (seq_len / 5.0)):
                    flag = False
                    print('FALSE')
                    break

                sequence_in_feat = [normed_feats[k]
                                    for k in filter_strings]
                if key != 'inter-part':
                    sequences[key] = [orig_feats[k] if not isinstance(
                        k, str) else k for k in seq]

                    distances.append(distance_between_windowed_features(
                        sequence_in_feat,
                        normed_feats))

                    # calculate ktrace distance as
                    # (#non-consecutive / #total-recuperaded-states)
                    print(filter_strings)
                    distances_2.append(
                        (sum(np.diff(filter_strings) != 1) +  (len(seq) - len(filter_strings)))/len(seq))

            if flag:
                ordered_sequences.append(
                    (sequences,
                     sum(distances)/len(distances),
                     sum(distances_2)/len(distances_2)))
                i += 1

    ordered_sequences.sort(key=lambda tup: tup[2])
    return ordered_sequences


def generate_from_multiple(application, num_seq):
    """
    Generate Sequences From a Multiple Oracle
    """
    information = application.oracles_information['multiple_oracles']

    localtime = time.asctime(time.localtime(time.time()))
    localtime = '_'.join(localtime.split(' '))
    localtime = '-'.join(localtime.split(':'))

    # Save original Score
    multi_sequence_score_generator(
        information['original_features'], information['features_names'],
        application=application, name='original',
        time='generations_' + localtime, actual_index=0)

    ordered_sequences = generate_sequences_multiple(
        information, num_seq)
    for i, (sequence, dist_1, dist_2) in enumerate(ordered_sequences):
        name = 'gen_' + str(i) + '_distF_' + str(round(dist_1)) + \
            '_distC_' + str(round(dist_2, 2))
        multi_sequence_score_generator(
            sequence,
            information['features_names'],
            application=application,
            name=name,
            time='generations_' + localtime)


def multi_sequence_score_generator(sequences, feature_names, application, name='', time='', actual_index=-1):
    """
    Generate Score
    """
    start_pitches = {}
    sequenced_events = {}
    for key, sequence in sequences.items():
        if key != 'inter-part':
            sequenced_events[key] = [PartEvent(
                from_list=state, features=feature_names)
                if not isinstance(state, str)
                else state
                for state in sequence]

            start_pitches[key] = application.principal_music[0].get_part_events()[
                key][0].get_viewpoint('pitch')

            if actual_index == -1:
                last_pitch_index = get_last_x_events_that_are_notes_before_index(
                    application.principal_music[0].get_part_events()[key],
                    number=1, actual_index=actual_index)
                start_pitches[key] = 0
                if last_pitch_index is not None:
                    last_pitch = application.principal_music[0].get_part_events()[
                        key][last_pitch_index].get_viewpoint('pitch')
                    start_pitches[key] = last_pitch

    duration = False
    if any('duration' in feat for feat in feature_names):
        duration = True

    score = parse_multiple(sequenced_events, start_pitches, duration)

    splitted_db = application.database_path.split(os.sep)
    if len(splitted_db) == 1:
        splitted_db = application.database_path.split('/')

    db_path = os.sep.join(splitted_db[:-1])
    gen_folder = os.sep.join([db_path, 'generations', time])
    if not os.path.exists(gen_folder):
        try:
            os.makedirs(gen_folder, exist_ok=True)
        except OSError:
            print("Creation of the directory %s failed" % gen_folder)
        else:
            print("Successfully created the directory %s " % gen_folder)
            path = os.sep.join([gen_folder, name + '.xml'])
            fp = score.write(fp=path)
    else:
        print(os.sep.join([gen_folder, name + '.xml']))
        fp = score.write(fp=os.sep.join([gen_folder, name + '.xml']))
