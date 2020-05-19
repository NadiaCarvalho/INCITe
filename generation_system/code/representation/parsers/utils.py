#!/usr/bin/env python3.7
"""
This script presents utility functions for dealing with representations
"""
import music21

#
# Basic/Maths Functions
#


def sign(number):
    """
    Returns the sign of a number
    """
    return number and (1, -1)[number < 0]


def seq_int(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns the difference between two midi values
    """
    return midi_viewpoint_1 - midi_viewpoint_2


def contour(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns the signal between two midi values
    """
    return sign(midi_viewpoint_1 - midi_viewpoint_2)


def contour_hd(midi_viewpoint_1, midi_viewpoint_2):
    """
    Returns a quantized difference between two midi values
    Defined in (Mullensiefen and Frieler, 2004a)
    """
    result = midi_viewpoint_1 - midi_viewpoint_2
    values = [1, 3, 5, 8]
    for count, ele in enumerate(values):
        if result < ele:
            return sign(result)*count
    return int(0)


def is_intervalic_difference(seq_int_1, sign_1, seq_int_2, sign_2):
    """
    Is Intervalic Difference (Defined in IDYOM)
    """
    if abs(seq_int_2) >= 7:
        if sign_1 != sign_2 and abs(seq_int_1) < abs(seq_int_2) - 3:
            return True
        if sign_1 == sign_2 and abs(seq_int_1) < abs(seq_int_2) - 2:
            return True
    if abs(seq_int_2) < 6 and seq_int_1 == seq_int_2:
        return True
    return False

#
# Offset Related
#


def get_last_x_events_that_are_notes_before_index(events, number=1, actual_index=None):
    """
    Returns the first event that is a note but not a rest before an event
    """
    if len(events) < 2:
        return None
    if len(events) < number + 1:
        number = len(events)-1
    if actual_index is None:
        actual_index = len(events) - 1

    count = 0
    events_to_return = []
    events_process = events[:actual_index]
    for i in range(len(events_process)):
        index = len(events_process) - (i + 1)
        if not events_process[index].is_rest():
            if number == 1:
                return index
            if count < number:
                events_to_return.append(index)
                count += 1
            else:
                return events_to_return
    return None


def get_events_at_offset(events, offset):
    """
    Returns all events that happen at a specified offset
    """
    return [event for event in events if event.get_offset() == offset]


def get_evs_bet_offs_inc(events, offset1, offset2=None):
    """
    Returns all events that happen between (and including) two specified offsets
    """
    if len(events) < 1:
        return events

    if offset2 is None:
        offset2 = events[-1].get_offset()

    return [event for event in events if offset1 <= event.get_offset() <= offset2]


#
# Parsing Utilities
#
def get_rests(events):
    """
    Returns all events that are rests
    """
    return [event for event in events if event.is_rest()]


def get_grace_notes(events):
    """
    Returns all events that are grace notes
    """
    return [event for event in events if event.is_grace_note()]


def harmonic_functions_key(chord, key):
    """
    Parses the harmonic key signatures information for a key
    """
    return music21.roman.romanNumeralFromChord(chord, key)


def part_name_parser(music_to_parse):
    """
    Return the name and voice of the part
    """
    part_name_voice = [music_to_parse.partName, 'v0']
    if music_to_parse.partName is None and isinstance(music_to_parse.id, str):
        part_name_voice = music_to_parse.id.split('-')
    return part_name_voice


def get_analysis_keys_stream_bet_offsets(music_to_parse, off1, off2):
    """
    Gets an analysis of key for a stream
    """
    k = music_to_parse.getElementsByOffset(
        off1, off2).stream().analyze('key')
    return (off1, k)


def has_value_viewpoint_events(events, viewpoint):
    """
    For a sequence of events, evaluate
    if all None (False) or not (True)
    """
    for event in events:
        view = event.get_viewpoint(viewpoint)
        if view is not None:
            return True
    return False


def instrument_for_voices(instrument):
    """
    Recover Instrument for voice dealing
    """
    real_in = music21.instrument.Instrument()
    try:
        if instrument is not None:
            if instrument in ['Brass', 'Woodwind', 'Keyboard', 'String']:
                instrument += 'Instrument'
            inst_name = ''.join(instrument.split(' '))
            real_in = getattr(music21.instrument, inst_name)()
    except AttributeError:
        print('Wrong Instrument: ' + instrument)
        try:
            real_in = music21.instrument.fromString(instrument)
        except music21.exceptions21.InstrumentException:
            print("Can't convert from this instrument: " + instrument)

    return real_in
