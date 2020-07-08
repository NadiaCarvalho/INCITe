"""
Voice Utils
"""
import copy
import math

import music21


def is_power(num_1, num_2):
    """
    Check if number is power of another
    """
    # The only power of 1 is 1 itself
    if num_1 == 1:
        return num_2 == 1
    # Repeatedly compute power of x
    _pow = 1
    while _pow < num_2:
        _pow = _pow * num_1
    # Check if power of x becomes y
    return _pow == num_2


def get_number_voices(stream):
    """
    Get Ideal Number of Voices from a Music21 Stream
    """
    voice_count = 1

    # To deal with separation of chords
    chords = stream.recurse(classFilter='Chord')
    cardinalities = [len(chord.pitches) for chord in chords]
    for card in cardinalities:
        if card > voice_count:
            voice_count = card

    old_dict_notes = stream.recurse(classFilter='Note')
    stream_not_hidden = music21.stream.Stream()
    _ = [stream_not_hidden.append(
        note) for note in old_dict_notes if not note.style.hideObjectOnPrint]
    old_dict_overlaps = stream_not_hidden.getOverlaps()
    for group in old_dict_overlaps.values():
        if len(group) > voice_count:
            voice_count = len(group)
    return voice_count


def distribute_notes(i, cardinality, voice_count):
    """
    Distribute notes by voices, higher ones have always less examples
    """
    limits = [(n*voice_count - cardinality) /
              cardinality for n in range(voice_count)]
    powered_values = is_power(cardinality, voice_count)

    start_voice = 0
    if i > 0:
        start_voice = math.ceil(limits[i])
        if powered_values:
            start_voice += 1

    end_voice = voice_count
    if i < cardinality - 1:
        end_voice = math.floor(limits[i+1])
        if powered_values:
            end_voice += 1

    return start_voice, end_voice


def process_chord(element, off, voices, voice_count):
    """
    Process notes of chord by voices
    """
    notes_to_insert = [music21.note.Note(
        pitch, duration=element.duration) for pitch in element.pitches]
    if notes_to_insert is not None:
        notes_to_insert.reverse()

    for i, note in enumerate(notes_to_insert):
        if note.style.hideObjectOnPrint:
            continue

        cardinality = len(notes_to_insert)
        if cardinality == voice_count:
            voices[i].insert(off, note)
            continue

        start_voice, end_voice = distribute_notes(i, cardinality, voice_count)
        for j in range(start_voice, end_voice):
            voices[j].insert(off, note)


def remove_unused_voices(voices, fill_gaps, return_obj):
    """
    remove any unused voices (possible if overlap group has sus)
    """
    for voice in voices:
        if voice:  # skip empty voices
            if fill_gaps:
                voice.makeRests(fillGaps=True, inPlace=True)
            return_obj.insert(0, voice)


def define_voices(voice_count, dist_name):
    """
    store all voices in a list
    """
    voices = []
    for dummy in range(voice_count):
        # add voice classes
        voices.append(music21.stream.Voice(id=(dummy + dist_name)))
    return voices


def make_voices(stream, in_place=False, fill_gaps=True, number_voices=None, dist_name=0):
    """
    Make voices from a poliphonic stream, based on music21
    """
    return_obj = stream
    if not in_place:  # make a copy
        return_obj = copy.deepcopy(stream)

    voice_count = get_number_voices(return_obj)
    if number_voices is not None:
        voice_count = max(number_voices, voice_count)

    if voice_count == 1:  # nothing to do here
        if not in_place:
            return return_obj
        return None

    voices = define_voices(voice_count, dist_name)

    for element in return_obj.recurse():
        off = element.getOffsetBySite(return_obj.flat)

        if isinstance(element, music21.chord.Chord):
            process_chord(element, off, voices, voice_count)
        else:
            for voice in voices:
                if (isinstance(element, (music21.note.Note, music21.note.Rest))
                        and element.style.hideObjectOnPrint):
                    break
                voice.insert(off, element)
        # remove from source
        return_obj.remove(element)

    remove_unused_voices(voices, fill_gaps, return_obj)

    # elements changed will already have been called
    return return_obj


def process_voiced_measure(measure, max_voice_count):
    """
    Process a measure that has voices
    """
    new_voices = []
    old_measure = copy.deepcopy(measure)
    measure.removeByClass(classFilterList='Voice')

    for voice in old_measure.voices:
        if (len(voice.recurse(classFilter='Chord')) > 0
                or len(voice.recurse(classFilter='Note').getOverlaps()) > 0):
            new = make_voices(voice, in_place=False, number_voices=int(
                max_voice_count/len(old_measure.voices)), dist_name=len(new_voices))
            for _voice in new.voices:
                new_voices.append(_voice)
        else:
            new_voices.append(voice)

    for voice in new_voices:
        measure.insert(0, voice)
