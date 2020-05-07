#!/usr/bin/env python3.7
"""
This script presents the class LineParser that processes the events of a single line
"""

import music21

import representation.utils as utils
from representation.events.linear_event import LinearEvent
from representation.parsers.segmentation import segmentation


class LineParser:
    """
    A class used to parse lines of music and translate them to viewpoint events.

    Attributes
    ----------
    music_to_parse: music21 stream
        line of music to parse
    events: list of objects of class Event
        events parsed from music
    part_name: str
        the name of the part being parsed
    voice: str
        the voice of the music the part being parsed corresponds
    measure_offsets: list of int
        offsets of measures in music
    measure_keys: list of music21 key elements
        analysis of key by measure in music
    """

    def __init__(self, music_to_parse, metadata=None):
        """
        Parameters
        ----------
        music_to_parse: music21 stream
            line of music to parse
        """
        self.music_to_parse = music_to_parse  # .toSoundingPitch()

        self.composer = metadata.composer
        self.title = metadata.title
        self.instrument = music_to_parse.getInstrument()

        part_name_voice = utils.part_name_parser(music_to_parse)
        self.part_name = part_name_voice[0]
        self.voice = part_name_voice[1]

        # Get offsets of beginnings of measures
        measures = self.music_to_parse.recurse(classFilter='Measure')
        self.measure_offsets = [measure.offset for measure in measures]

        ka = music21.analysis.floatingKey.KeyAnalyzer(music_to_parse)
        self.measure_keys = ka.getRawKeyByMeasure()

        self.events = []

    def parse_line(self):
        """
        Returns the events from a line with viewpoints
        """
        self.note_and_rests_parsing()
        # self.intfib_grace_notes_parsing()
        self.dynamics_parsing()
        self.key_signatures_parsing()
        self.time_signatures_parsing()
        self.metro_marks_parsing()
        self.double_barline_parsing()
        self.repeat_barline_parsing()

        segmentation(self.events)
        self.segmentation_info()

        return self.events

    def note_and_rests_parsing(self):
        """
        Parses the note/rest events
        """
        #print('Parse Notes')
        # Get Notes and Rests only
        stream_notes_rests = self.music_to_parse.flat.notesAndRests.stream()

        for i, note_or_rest in enumerate(stream_notes_rests.elements):

            self.events.append(LinearEvent(offset=note_or_rest.offset))

            # Basic Part/Voice Names
            self.events[i].add_viewpoint('piece_title', self.title)
            self.events[i].add_viewpoint('composer', self.composer)
            self.events[i].add_viewpoint('instrument', self.instrument)
            self.events[i].add_viewpoint('part', self.part_name)
            self.events[i].add_viewpoint('voice', self.voice)

            # # Basic Rest/Grace Notes Information
            self.events[i].add_viewpoint('rest', note_or_rest.isRest)
            self.events[i].add_viewpoint(
                'grace', note_or_rest.duration.isGrace)

            # Duration Parsing
            self.duration_info_parsing(i, note_or_rest)

            # Expression and Spanners Parsing
            self.expression_parsing(i, note_or_rest.expressions)
            self.spanner_parsing(
                i, note_or_rest, note_or_rest.getSpannerSites())

            # If note is not a rest, parse pitch information
            if not note_or_rest.isRest:
                self.note_basic_info_parsing(i, note_or_rest)
                self.contours_parsing(i)

            # Measure Related Information Parsing
            self.measure_info_parsing(i, note_or_rest)

    def note_basic_info_parsing(self, index, note_or_rest):
        """
        Parses the basic info for a note (not rest) event
        """
        #print('Parse Note Basic')
        self.events[index].add_viewpoint(
            'cpitch', note_or_rest.pitch.ps)
        self.events[index].add_viewpoint('dnote', note_or_rest.step)
        self.events[index].add_viewpoint('octave', note_or_rest.octave)

        if note_or_rest.pitch.accidental is not None:
            self.events[index].add_viewpoint(
                'accidental', note_or_rest.pitch.accidental.modifier)

        self.events[index].add_viewpoint(
            'microtonal', note_or_rest.pitch.microtone.cents)
        self.events[index].add_viewpoint(
            'pitch_class', note_or_rest.pitch.pitchClass)

        self.events[index].add_viewpoint(
            'notehead.type', note_or_rest.notehead)

        if note_or_rest.noteheadFill is not None:
            self.events[index].add_viewpoint(
                'fill', note_or_rest.noteheadFill)

        if note_or_rest.noteheadParenthesis is not None:
            self.events[index].add_viewpoint(
                'parenthesis', note_or_rest.noteheadParenthesis)

        for art in note_or_rest.articulations:
            if art.name == 'breath mark':
                self.events[index].add_viewpoint('breath_mark', True)
            else:
                self.events[index].add_viewpoint('articulation', art.name)

        self.events[index].add_viewpoint(
            'volume', note_or_rest.volume.getRealized())

        if note_or_rest.tie is not None:
            self.events[index].add_viewpoint(
                'type', note_or_rest.tie.type, 'tie')
            self.events[index].add_viewpoint(
                'style', note_or_rest.tie.style, 'tie')

    def duration_info_parsing(self, index, note_or_rest):
        """
        Parses the duration info for an event
        """
        #print('Parse Duration')
        self.events[index].add_viewpoint(
            'length', note_or_rest.duration.quarterLength, 'duration')
        self.events[index].add_viewpoint(
            'duration.type', note_or_rest.duration.type)
        self.events[index].add_viewpoint(
            'dots', note_or_rest.duration.dots, 'duration')

        if note_or_rest.duration.isGrace:
            self.events[index].add_viewpoint(
                'duration.type', note_or_rest.duration.components[0].type)
            self.events[index].add_viewpoint(
                'duration.slash', note_or_rest.duration.slash)

    def contours_parsing(self, index):
        """
        Parses the contours for an event
        """
        #print('Parse Contours')
        # get index of last event that is a note and not a rest
        last_note_index = utils.get_last_x_events_that_are_notes_before_index(
            self.events)

        if last_note_index is not None:
            pitch_note = self.events[index].get_viewpoint('cpitch')
            pitch_last_note = self.events[last_note_index].get_viewpoint(
                'cpitch')
            self.events[index].add_viewpoint(
                'seq_int', utils.seq_int(pitch_note, pitch_last_note))
            self.events[index].add_viewpoint(
                'contour', utils.contour(pitch_note, pitch_last_note))
            self.events[index].add_viewpoint(
                'contour_hd', utils.contour_hd(pitch_note, pitch_last_note))

        last_four_note_indexes = utils.get_last_x_events_that_are_notes_before_index(
            self.events, number=2)
        if last_four_note_indexes is not None:
            if not isinstance(last_four_note_indexes, list):
                last_four_note_indexes = [last_four_note_indexes]

            last_four_note_indexes.append(index)
            seq_ints = [self.events[i].get_viewpoint(
                'seq_int') for i in list(last_four_note_indexes[::-1])]
            signs = [utils.sign(seq_int) for seq_int in seq_ints]

            if ((seq_ints[-2] >= 7 and signs[-1] != signs[-2])
                    or (seq_ints[-2] < 6 and signs[-1] == signs[-2])):
                self.events[index].add_viewpoint('registral_direction', True)

            if ((abs(seq_ints[-2]) >= 7 and
                 ((abs(seq_ints[-1]) < abs(seq_ints[-2])-3 and signs[-1] != signs[-2])
                    or (abs(seq_ints[-1]) < abs(seq_ints[-2])-2 and signs[-1] == signs[-2])))
                    or (abs(seq_ints[-2]) < 6 and seq_ints[-1] == seq_ints[-2])):
                self.events[index].add_viewpoint(
                    'intervallic_difference', True)

            score = 0
            if all(i > 0 for i in signs):
                self.events[index].add_viewpoint('upwards', True)
            elif all(i < 0 for i in signs):
                self.events[index].add_viewpoint('downwards', True)
            elif all(i == 0 for i in signs):
                self.events[index].add_viewpoint('no_movement', True)
            else:
                score += 1

            if abs(seq_ints[-1]) < abs(seq_ints[-2])-2:
                score += 1
            self.events[index].add_viewpoint(
                'closure', score)

    def expression_parsing(self, index, expressions):
        """
        Parses the existence of a fermata in an event
        """
        #print('Parse Expression')
        for expression in expressions:
            if type(expression) is music21.expressions.Fermata:
                self.events[index].add_viewpoint('fermata', True)
            elif type(expression) is music21.expressions.RehearsalMark:
                self.events[index].add_viewpoint('rehearsal', True)
            elif type(expression) is music21.expressions.Turn:
                self.events[index].add_viewpoint(
                    'ornamentation', 'turn_' + expression.name)
            elif type(expression) is music21.expressions.Trill:
                self.events[index].add_viewpoint(
                    'ornamentation', 'trill_' + expression.placement + '_' + expression.size.name)
            elif type(expression) is music21.expressions.Tremolo:
                self.events[index].add_viewpoint(
                    'ornamentation', 'tremolo_' + str(expression.measured) + '_' + str(expression.numberOfMarks))
            elif type(expression) is music21.expressions.Schleifer:
                self.events[index].add_viewpoint('ornamentation', 'schleifer')
            elif 'GeneralMordent' in expression.classes:
                self.events[index].add_viewpoint(
                    'ornamentation', 'mordent_' + expression.direction + '_' + expression.size.name)
            elif 'GeneralAppoggiatura' in expression.classes:
                self.events[index].add_viewpoint(
                    'ornamentation', 'appogiatura_' + expression.name)
            else:
                self.events[index].add_viewpoint('expression', expression)

    def spanner_parsing(self, index, note_or_rest, spanners):
        """
        Parses the existence of a fermata in an event
        """
        #print('Parse spanners (slurs, cresc/etc)')
        for span in spanners:
            if 'Slur' in span.classes:
                self.events[index].add_viewpoint(
                    'slur.begin', span.isFirst(note_or_rest))
                self.events[index].add_viewpoint(
                    'slur.end', span.isLast(note_or_rest))
                self.events[index].add_viewpoint(
                    'slur.between', True)

    def get_first_fib_before_fib(self, offset):
        """
        Returns the first fib before an event that is a fib
        """
        index = self.measure_offsets.index(offset)
        if index == 0:
            return None
        fib_candidates = [event for event in utils.get_events_at_offset(
            self.events, self.measure_offsets[index - 1]) if utils.not_rest_or_grace(event)]
        if len(fib_candidates) > 0:
            return fib_candidates[0]
        return self.get_first_fib_before_fib(self.measure_offsets[index - 1])

    def get_first_fib_before_non_fib(self, note_or_rest):
        """
        Returns the first fib before an event that is not a fib
        """
        index = self.measure_offsets.index(
            min(self.measure_offsets, key=lambda x: abs(x - note_or_rest.offset)))
        fib_index = (
            index, index-1)[bool(note_or_rest.offset < self.measure_offsets[index])]
        return [event for event in utils.get_events_at_offset(
            self.events, self.measure_offsets[fib_index]) if not event.is_grace_note()]

    def parsing_fib_element(self, index, note_or_rest):
        """
        Parses the information for an event that is the first element in bar
        """
        self.events[index].add_viewpoint('fib', True)
        self.events[index].add_viewpoint('intfib', 0.0)
        last_fib = self.get_first_fib_before_fib(
            note_or_rest.offset)
        if last_fib is not None:
            cur_fib_midi = self.events[index].get_viewpoint('cpitch')
            last_fib_midi = last_fib.get_viewpoint('cpitch')
            self.events[index].add_viewpoint('thrbar', utils.seq_int(
                cur_fib_midi, last_fib_midi))

    def parsing_non_fib_element(self, index, note_or_rest):
        """
        Parses the information for an event that is not the first element in bar
        """
        self.events[index].add_viewpoint('fib', False)
        last_fib = self.get_first_fib_before_non_fib(note_or_rest)
        if len(last_fib) > 1:
            last_fib = last_fib[0]
            if not note_or_rest.isRest and utils.not_rest_or_grace(last_fib):
                cur_midi = self.events[index].get_viewpoint('cpitch')
                last_fib_midi = last_fib.get_viewpoint('cpitch')
                self.events[index].add_viewpoint('intfib', utils.seq_int(
                    cur_midi, last_fib_midi))

    def measure_info_parsing(self, index, note_or_rest):
        """
        Parses the information relating to order in a measure
        and melodic sequences with other elements of a measure
        for an event
        """
        #print('Parse Measure')

        key_anal = self.measure_keys[note_or_rest.measureNumber - 1]
        self.events[index].add_viewpoint(
            'key', str(key_anal), 'measure')

        if not note_or_rest.isRest and key_anal is not None:
            sc_deg = key_anal.getScaleDegreeFromPitch(note_or_rest.pitch.name)
            self.events[index].add_viewpoint(
                'scale_degree', sc_deg, 'measure')

        if not note_or_rest.duration.isGrace:
            try:
                posinbar = note_or_rest.beat - 1
                self.events[index].add_viewpoint('posinbar', posinbar)
                self.events[index].add_viewpoint(
                    'beat_strength', note_or_rest.beatStrength)

                if posinbar == 0 or posinbar % 1 == 0:
                    self.events[index].add_viewpoint(
                        'tactus', True)
            except music21.Music21Exception:
                print('this object does not have a TimeSignature in Sites')

        if note_or_rest.offset in self.measure_offsets and not note_or_rest.duration.isGrace:
            self.parsing_fib_element(index, note_or_rest)
        else:
            self.parsing_non_fib_element(index, note_or_rest)

    def dynamics_parsing(self):
        """
        Parses the existent dynamics information
        """
        #print('Parse Dynamics')
        dynamics = list(self.music_to_parse.flat.getElementsByClass(
            music21.dynamics.Dynamic))
        for i, dynamic in enumerate(dynamics):
            next_dyn_offset = (self.music_to_parse.highestTime if i == (len(dynamics)-1)
                               else dynamics[i+1].offset)
            for event in utils.get_evs_bet_offs_inc(self.events, dynamic.offset, next_dyn_offset):
                event.add_viewpoint('dynamic', dynamic.value)

    def intfib_grace_notes_parsing(self):
        """
        Parses the intfib information for fib grace_notes, as they are
        not really the fib even if they are the first element in a bar
        """
        #print('Parse Grace')
        for grace_note in utils.get_grace_notes(self.events):
            fib_midi = self.events[self.events.index(
                grace_note) + 1].get_viewpoint('cpitch')
            grace_note.add_viewpoint('intfib', utils.seq_int(
                fib_midi, grace_note.get_viewpoint('cpitch')))

    def key_signatures_parsing(self):
        """
        Parses the existent key signatures information
        """
        #print('Parse Keys')
        keys = list(self.music_to_parse.flat.getElementsByClass(
            music21.key.KeySignature))

        for i, key in enumerate(keys):
            next_key_offset = (self.music_to_parse.highestTime if i == (len(keys)-1)
                               else keys[i+1].offset)

            try:
                key_anal = utils.get_analysis_keys_stream_bet_offsets(
                    self.music_to_parse, key.offset, next_key_offset)[1]

                for event in utils.get_evs_bet_offs_inc(self.events, key.offset, next_key_offset):
                    event.add_viewpoint('keysig', key.sharps)
                    event.add_viewpoint('key', str(key_anal), 'signature')
                    if not event.is_rest():
                        sc_deg = key_anal.getScaleDegreeFromPitch(
                            event.get_viewpoint('dnote') +
                            event.get_viewpoint('accidental'))
                        event.add_viewpoint(
                            'scale_degree', sc_deg, 'signature')
            except music21.analysis.discrete.DiscreteAnalysisException:
                print('failed to get likely keys for Stream component')

    def time_signatures_parsing(self):
        """
        Parses the existent key signatures information
        """
        #print('Parse Time Sig')
        time_sigs = list(self.music_to_parse.flat.getElementsByClass(
            music21.meter.TimeSignature))
        for i, sig in enumerate(time_sigs):
            offset = (None if i == (len(time_sigs)-1)
                      else time_sigs[i+1].offset)
            for event in utils.get_evs_bet_offs_inc(self.events, sig.offset, offset):
                event.add_viewpoint(
                    'timesig', sig.ratioString)
                event.add_viewpoint(
                    'pulses', sig.numerator)
                event.add_viewpoint(
                    'barlength', sig.denominator)

    def metronome_marks_parsing(self, metro_marks, events=None):
        """
        Parses the existent Metronome Markings of a line part to a set of events
        """
        if events is None:
            events = self.events

        for i, metro in enumerate(metro_marks):
            for event in utils.get_evs_bet_offs_inc(events, metro[0], metro[1]):
                event.add_viewpoint(
                    'text', metro[2].text, 'metro')
                event.add_viewpoint(
                    'value', metro[2].number, 'metro')
                if metro[2].numberSounding is not None:
                    event.add_viewpoint(
                        'sound', metro[2].numberSounding)
                else:
                    event.add_viewpoint(
                        'sound', metro[2].number)
                event.add_viewpoint(
                    'value', metro[2].referent.quarterLength, 'ref')
                event.add_viewpoint(
                    'type', metro[2].referent.type, 'ref')

    def metro_marks_parsing(self):
        """
        Parses the existent Metronome Markings
        """
        #print('Parse Metro')
        self.metronome_marks_parsing(metro_marks=list(self.music_to_parse.flat.metronomeMarkBoundaries()))

    def double_barline_parsing(self):
        """
        Parses the existent double barlines (because they can be important if delimiting phrases)
        """
        #print('Parse Barline')
        for d_bar_off in [barline.offset for barline in self.music_to_parse.flat.getElementsByClass(
                music21.bar.Barline) if barline.type == 'double']:
            events_at_barline = utils.get_events_at_offset(
                self.events, d_bar_off)
            if len(events_at_barline) > 0:
                events_at_barline[0].add_viewpoint('double', True)

    def repeat_barline_parsing(self):
        """
        Parses the existent repeat barlines (because they can be important if delimiting phrases)
        and the direction for repeating
        """
        #print('Parse Repeat')
        for repeat in self.music_to_parse.flat.getElementsByClass(music21.bar.Repeat):
            events_repeats = utils.get_events_at_offset(
                self.events, repeat.offset)
            if len(events_repeats) == 0:
                self.events[-1].add_viewpoint('is_end', True)
                self.events[-1].add_viewpoint('direction',
                                              repeat.direction)
            else:
                events_repeats[0].add_viewpoint(
                    'exists_before', True)
                events_repeats[0].add_viewpoint(
                    'direction', repeat.direction)

    def segmentation_info(self):
        """
        """
        #print('Parse Segmentation')
        boundary_indexes = [
            i for i, event in enumerate(self.events) if event.get_viewpoint('pharse.boundary') == 1]

        for k, event in enumerate(self.events):
            if k != 0:
                index = boundary_indexes.index(
                    min(boundary_indexes, key=lambda x: abs(x - k)))
                last_index = (
                    index, index-1)[bool(k < boundary_indexes[index])]

                length = len(self.events) - boundary_indexes[last_index]
                if last_index < len(boundary_indexes)-1:
                    length = boundary_indexes[last_index +
                                              1] - boundary_indexes[last_index]

                if k in boundary_indexes:
                    last_index = boundary_indexes.index(k)-1
                    length = len(self.events) - k
                    if last_index < len(boundary_indexes)-2:
                        length = boundary_indexes[last_index+2] - k

                event.add_viewpoint('intphrase',  utils.seq_int(
                    event.get_viewpoint('pitch.cpitch'), self.events[last_index].get_viewpoint('pitch.cpitch')))
                event.add_viewpoint('phrase.length', length)
