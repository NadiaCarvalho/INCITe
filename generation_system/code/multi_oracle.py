"""
"""
import generation.gen_algorithms.multi_oracle_gen as multi_gen
import generation.plot_fo as gen_plot
import generation.utils as gen_utils
from generation.cdist_fixed import distance_between_windowed_features
from representation.conversor.score_conversor import ScoreConversor
from representation.events.linear_event import LinearEvent



def get_multiple_part_features(application, part_info, vert_info):
    """
    Get Multiple Part Features
    """
    ev_offsets = {}
    normed_features = {}
    original_features = {}

    for music, _tuple in application.music.items():
        parser = _tuple[0]
        last_offset = 0
        if ev_offsets != {}:
            last_offset = max([part_off[-1]
                               for part_off in ev_offsets.values()])

        i = 0
        for key, events in parser.get_part_events().items():
            if len(events) > 0:
                start_index = application.indexes_first[music]['parts'][i]
                finish_index = start_index + len(events)

                if i not in normed_features:
                    normed_features[i] = []
                    ev_offsets[i] = []
                    original_features[i] = []

                normed_features[i].extend(
                    part_info['selected_normed'][start_index:finish_index])
                original_features[i].extend(
                    part_info['selected_original'][start_index:finish_index])
                ev_offsets[i].extend(
                    [ev.get_offset() + last_offset for ev in events])

                i += 1

        vertical_events = parser.get_vertical_events()
        if len(vertical_events) > 0:
            start_index = application.indexes_first[music]['vertical']
            finish_index = start_index + len(vertical_events)

            if 'vertical' not in normed_features:
                normed_features['vertical'] = []
                ev_offsets['vertical'] = []

            normed_features['vertical'].extend(
                vert_info['selected_normed'][start_index:finish_index])
            ev_offsets['vertical'].extend(
                [ev.get_offset() + last_offset for ev in vertical_events])

    return normed_features, original_features, ev_offsets


def construct_multi_oracles(application):
    """
    Construct Multiple Oracles from Information
    """
    part_information = application.music_information['parts']
    vert_information = application.music_information['vertical']

    normed_features, original_features, ev_offsets = get_multiple_part_features(
        application, part_information, vert_information)

    oracles = {}

    for key, part in normed_features.items():
        features_names = part_information['selected_features_names']
        weights = part_information['normed_weights']
        fixed_weights = part_information['fixed_weights']
        if key == 'vertical':
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

    image = gen_plot.start_draw(oracles, ev_offsets)
    name = r'data\myexamples\oracle' + '.PNG'
    image.save(name)

    application.oracles_information['multiple_oracles'] = {
        'oracles': oracles,
        'normed_features': normed_features,
        'original_features': original_features,
        'features_names': part_information['selected_features_names'],
        'offsets': ev_offsets
    }


def generate_sequences_multiple(application, information, num_seq):
    """
    Generate Sequences
    """
    ordered_sequences = []

    i = 0
    while i < num_seq:
        sequences, ktraces = multi_gen.sync_generate(
            information['oracles'], information['offsets'], seq_len=50, p=0.5, k=0)

        if all(len(sequence) > 0 for sequence in sequences.values()):
            distances = []
            for key, sequence in sequences.items():
                distances.append(distance_between_windowed_features(
                    [information['normed_features'][key][state-1]
                        for state in sequence],
                    information['normed_features'][key]))

            ordered_sequences.append(
                (sequences, sum(distances)/len(distances)))
            i += 1

    ordered_sequences.sort(key=lambda tup: tup[1])
    return ordered_sequences


def generate_from_multiple(application, num_seq):
    """
    Generate Sequences From a Multiple Oracle
    """
    information = application.oracles_information['multiple_oracles']

    # Save original Score
    original_sequences = {}
    for key, part in information['original_features'].items():
        original_sequences[key] = range(len(part))
    multi_sequence_score_generator(
        original_sequences, information['original_features'],
        information['features_names'], name='original', start=0)

    localtime = time.asctime(time.localtime(time.time()))
    localtime = '_'.join(localtime.split(' '))
    localtime = '-'.join(localtime.split(':'))

    ordered_sequences = generate_sequences_multiple(
        information, num_seq)
    for i, (sequence, dist) in enumerate(ordered_sequences):
        name = 'gen_' + localtime + '_' + \
            str(i) + '_distance_' + str(dist) + '.xml'
        multi_sequence_score_generator(
            sequence, information['original_features'],
            information['features_names'],
            name=name)


def multi_sequence_score_generator(sequences, o_information, feature_names, name='', start=-1):
    """
    Generate Score
    """
    score = ScoreConversor()
    for key, sequence in sequences.items():
        if key != 'vertical':
            sequenced_events = [LinearEvent(
                from_list=o_information[key][state + start], features=feature_names)
                if (state + start) < len(o_information[key])
                else print('key: state ' + str(state + start))
                for state in sequence]
            if len(sequenced_events) > 0:
                score.parse_events(
                    sequenced_events, new_part=True, new_voice=True)
    # score.stream.show()

    path = os.sep.join([os.getcwd(), 'data', 'generations', name + '.xml'])
    fp = score.stream.write(fp=path)
