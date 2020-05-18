"""
Voice Utils
"""
import music21


def get_number_voices(stream):
    """
    """
    max_voice_count = 1
    # To deal with separation of chords
    chords = stream.recurse(classFilter='Chord')
    cardinalities = [len(chord.pitches) for chord in chords]
    for card in cardinalities:
        if card > max_voice_count:
            max_voice_count = card
    olDictN = stream.recurse(classFilter='Note')
    stream_not_hidden = music21.stream.Stream()
    _ = [stream_not_hidden.append(
        note) for note in olDictN if not note.style.hideObjectOnPrint]
    olDict = stream_not_hidden.getOverlaps()
    for group in olDict.values():
        if len(group) > max_voice_count:
            max_voice_count = len(group)
    return max_voice_count


def make_voices(stream, in_place=False, fill_gaps=True, number_voices=None, dist_name=0):
    """
    Make voices from a poliphonic stream, based on music21 
    """
    return_obj = stream
    if not in_place:  # make a copy
        return_obj = copy.deepcopy(stream)

    max_voice_count = get_number_voices(return_obj)
    if number_voices is not None:
        max_voice_count = max(number_voices, max_voice_count)

    if max_voice_count == 1:  # nothing to do here
        if not in_place:
            return return_obj
        return None

    # store all voices in a list
    voices = []
    for dummy in range(max_voice_count):
        # add voice classes
        voices.append(music21.stream.Voice(id=(dummy + dist_name)))

    # iterate through all elements; if not in an overlap, place in
    # voice 1, otherwise, distribute
    for e in return_obj.recurse():
        o = e.getOffsetBySite(return_obj.flat)

        # cannot match here by offset, as olDict keys are representative
        # of the first overlapped offset, not all contained offsets
        # if o not in olDict: # place in a first voices
        #    voices[0].insert(o, e)
        # find a voice to place in
        # as elements are sorted, can use the highest time
        # else:
        if type(e) is music21.chord.Chord:
            notes_to_insert = [music21.note.Note(
                pitch, duration=e.duration) for pitch in e.pitches]
            if notes_to_insert is not None:
                notes_to_insert.reverse()

            for i, note in enumerate(notes_to_insert):
                if note.style.hideObjectOnPrint:
                    continue

                if len(notes_to_insert) == max_voice_count:
                    voices[i].insert(o, note)
                else:
                    # distribute notes by voices, higher ones have always less examples
                    limits = [(n*max_voice_count - len(notes_to_insert)) /
                              len(notes_to_insert) for n in range(max_voice_count)]
                    powered_values = is_power(
                        len(notes_to_insert), max_voice_count)

                    start_voice = 0
                    if i > 0:
                        start_voice = math.ceil(limits[i])
                        if powered_values:
                            start_voice += 1

                    end_voice = max_voice_count
                    if i < len(notes_to_insert) - 1:
                        end_voice = math.floor(limits[i+1])
                        if powered_values:
                            end_voice += 1

                    for v in range(start_voice, end_voice):
                        voices[v].insert(o, note)
        else:
            for v in voices:
                if (type(e) is music21.note.Note or type(e) is music21.note.Rest) and e.style.hideObjectOnPrint:
                    break

                v.insert(o, e)

        # remove from source
        return_obj.remove(e)

    # remove any unused voices (possible if overlap group has sus)
    for v in voices:
        if v:  # skip empty voices
            if fill_gaps:
                v.makeRests(fillGaps=True, inPlace=True)
            return_obj.insert(0, v)

    # elements changed will already have been called
    if not in_place:
        return return_obj


def process_voiced_measure(measure, max_voice_count):
    """
    """
    new_voices = []
    old_measure = copy.deepcopy(measure)
    measure.removeByClass(classFilterList='Voice')

    for voice in old_measure.voices:
        if len(voice.recurse(classFilter='Chord')) > 0 or len(voice.recurse(classFilter='Note').getOverlaps()) > 0:
            new = make_voices(voice, in_place=False, number_voices=int(
                max_voice_count/len(old_measure.voices)), dist_name=len(new_voices))
            for v in new.voices:
                new_voices.append(v)
        else:
            new_voices.append(voice)

    for v in new_voices:
        measure.insert(0, v)
