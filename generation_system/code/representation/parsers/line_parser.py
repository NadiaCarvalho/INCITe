#!/usr/bin/env python3.7
"""
This script presents the class LineParser that processes the events of a single line
"""

from fractions import Fraction

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

    def __init__(self, music_to_parse):
        """
        Parameters
        ----------
        music_to_parse: music21 stream
            line of music to parse
        """
        self.music_to_parse = music_to_parse

        part_name_voice = utils.part_name_parser(music_to_parse)
        self.part_name = part_name_voice[0]
        self.voice = part_name_voice[1]

        ka = music21.analysis.floatingKey.KeyAnalyzer(music_to_parse)

        # Get offsets of beginnings of measures
        measures = self.music_to_parse.recurse(classFilter='Measure')
        self.measure_offsets = [measure.offset for measure in measures]
        self.measure_keys = ka.getRawKeyByMeasure()

        self.events = []

    def parse_line(self):
        """
        Returns the events from a line with viewpoints
        """
        self.note_and_rests_parsing()
        self.intfib_grace_notes_parsing()
        self.dynamics_parsing()
        self.key_signatures_parsing()
        self.time_signatures_parsing()
        self.metro_marks_parsing()
        self.double_barline_parsing()
        self.repeat_barline_parsing()

        segmentation(self.events)
        # self.phrase_related_info()

        return self.events

    def note_and_rests_parsing(self):
        """
        Parses the note/rest events
        """
        # Get Notes and Rests only
        stream_notes_rests = self.music_to_parse.flat.notesAndRests.stream()

        for i, note_or_rest in enumerate(stream_notes_rests.elements):

            self.events.append(LinearEvent(offset=note_or_rest.offset))

            # Basic Part/Voice Names
            self.events[i].add_viewpoint('part', self.part_name)
            self.events[i].add_viewpoint('voice', self.voice)

            # Basic Rest/Grace Notes Information
            self.events[i].add_viewpoint('rest', note_or_rest.isRest)
            self.events[i].add_viewpoint(
                'grace', note_or_rest.duration.isGrace)

            # If note is not a rest, parse pitch information
            if not note_or_rest.isRest:
                self.note_basic_info_parsing(i, note_or_rest)
                self.contours_parsing(i)

            # Duration Parsing
            self.duration_info_parsing(i, note_or_rest)

            # Expression Parsing
            self.expression_parsing(i, note_or_rest.expressions)

            # Measure Related Information Parsing
            self.measure_info_parsing(i, note_or_rest)

    def note_basic_info_parsing(self, index, note_or_rest):
        """
        Parses the basic info for a note (not rest) event
        """
        self.events[index].add_viewpoint('pitch', note_or_rest.pitch.ps)
        self.events[index].add_viewpoint('dnote', note_or_rest.step)
        self.events[index].add_viewpoint('octave', note_or_rest.octave)

        if note_or_rest.pitch.accidental is not None:
            self.events[index].add_viewpoint(
                'accidental', note_or_rest.pitch.accidental.modifier)

        self.events[index].add_viewpoint(
            'microtonal', note_or_rest.pitch.microtone.cents)
        self.events[index].add_viewpoint(
            'pitch_class', note_or_rest.pitch.pitchClass)

        self.events[index].add_viewpoint('notehead', note_or_rest.notehead)

        if note_or_rest.noteheadFill is not None:
            self.events[index].add_viewpoint(
                'noteheadfill', note_or_rest.noteheadFill)

        if note_or_rest.noteheadParenthesis is not None:
            self.events[index].add_viewpoint(
                'noteheadparenthesis', note_or_rest.noteheadParenthesis)

        for art in note_or_rest.articulations:
            self.events[index].add_viewpoint('articulation', art.name)

        self.events[index].add_viewpoint(
            'volume', note_or_rest.volume.getRealized())

        if note_or_rest.tie is not None:
            self.events[index].add_viewpoint('tie_type', note_or_rest.tie.type)
            self.events[index].add_viewpoint(
                'tie_style', note_or_rest.tie.style)

    def duration_info_parsing(self, index, note_or_rest):
        """
        Parses the duration info for an event
        """
        self.events[index].add_viewpoint(
            'dur_length', note_or_rest.duration.quarterLength)
        self.events[index].add_viewpoint(
            'dur_type', note_or_rest.duration.type)
        self.events[index].add_viewpoint(
            'dots', note_or_rest.duration.dots)

    def contours_parsing(self, index):
        """
        Parses the contours for an event
        """
        # get index of last event that is a note and not a rest
        last_note_index = utils.get_first_event_that_is_note_before_index(
            self.events)
        if last_note_index is not None:
            pitch_note = self.events[index].get_viewpoint('pitch')
            pitch_last_note = self.events[last_note_index].get_viewpoint(
                'pitch')
            self.events[index].add_viewpoint(
                'seq_int', utils.seq_int(pitch_note, pitch_last_note))
            self.events[index].add_viewpoint(
                'contour', utils.contour(pitch_note, pitch_last_note))
            self.events[index].add_viewpoint(
                'contour_hd', utils.contour_hd(pitch_note, pitch_last_note))

    def expression_parsing(self, index, expressions):
        """
        Parses the existence of a fermata in an event
        """
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
            cur_fib_midi = self.events[index].get_viewpoint('pitch')
            last_fib_midi = last_fib.get_viewpoint('pitch')
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
                cur_midi = self.events[index].get_viewpoint('pitch')
                last_fib_midi = last_fib.get_viewpoint('pitch')
                self.events[index].add_viewpoint('intfib', utils.seq_int(
                    cur_midi, last_fib_midi))

    def measure_info_parsing(self, index, note_or_rest):
        """
        Parses the information relating to order in a measure
        and melodic sequences with other elements of a measure
        for an event
        """

        key_anal = self.measure_keys[note_or_rest.measureNumber - 1]
        self.events[index].add_viewpoint(
            'key_ms', str(key_anal))

        if not note_or_rest.isRest and key_anal is not None:
            sc_deg = key_anal.getScaleDegreeFromPitch(note_or_rest.pitch.name)
            self.events[index].add_viewpoint(
                'scale_degree_ms', sc_deg)

        if not note_or_rest.duration.isGrace:
            components = note_or_rest.beatStr.split(' ')
            posinbar = int(
                components[0]) + (Fraction(components[1]) if len(components) > 1 else 0) - 1
            self.events[index].add_viewpoint('posinbar', posinbar)
            self.events[index].add_viewpoint(
                'beat_strength', note_or_rest.beatStrength)

        if note_or_rest.offset in self.measure_offsets and not note_or_rest.duration.isGrace:
            self.parsing_fib_element(index, note_or_rest)
        else:
            self.parsing_non_fib_element(index, note_or_rest)

    def dynamics_parsing(self):
        """
        Parses the existent dynamics information
        """
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
        for grace_note in utils.get_grace_notes(self.events):
            fib_midi = self.events[self.events.index(
                grace_note) + 1].get_viewpoint('pitch')
            grace_note.add_viewpoint('intfib', utils.seq_int(
                fib_midi, grace_note.get_viewpoint('pitch')))

    def key_signatures_parsing(self):
        """
        Parses the existent key signatures information
        """
        keys = list(self.music_to_parse.flat.getElementsByClass(
            music21.key.KeySignature))

        for i, key in enumerate(keys):
            next_key_offset = (self.music_to_parse.highestTime if i == (len(keys)-1)
                               else keys[i+1].offset)
            key_anal = utils.get_analysis_keys_stream_bet_offsets(
                self.music_to_parse, key.offset, next_key_offset)[1]

            for event in utils.get_evs_bet_offs_inc(self.events, key.offset, next_key_offset):
                event.add_viewpoint('keysig', key.sharps)
                event.add_viewpoint('key_ks', str(key_anal))
                if not event.is_rest():
                    sc_deg = key_anal.getScaleDegreeFromPitch(
                        event.get_viewpoint('dnote') +
                        event.get_viewpoint('accidental'))
                    event.add_viewpoint('scale_degree_ks', sc_deg)

    def time_signatures_parsing(self):
        """
        Parses the existent key signatures information
        """
        time_sigs = list(self.music_to_parse.flat.getElementsByClass(
            music21.meter.TimeSignature))
        for i, sig in enumerate(time_sigs):
            offset = (None if i == (len(time_sigs)-1)
                      else time_sigs[i+1].offset)
            for event in utils.get_evs_bet_offs_inc(self.events, sig.offset, offset):
                event.add_viewpoint(
                    'timesig', sig.ratioString)

    def metronome_marks_parsing(self, part=None, events=None):
        """
        Parses the existent Metronome Markings of a line part to a set of events
        """
        if part is None:
            part = self.music_to_parse
        if events is None:
            events = self.events

        metro_marks = list(part.flat.getElementsByClass(
            music21.tempo.MetronomeMark))
        for i, metro in enumerate(metro_marks):
            offset = (None if i == (len(metro_marks)-1)
                      else metro_marks[i+1].offset)
            for event in utils.get_evs_bet_offs_inc(events, metro.offset, offset):
                event.add_viewpoint(
                    'metronome', metro.number)
                event.add_viewpoint(
                    'metro_sound', metro.numberSounding)
                event.add_viewpoint(
                    'metro_ref_value', metro.referent.quarterLength)
                event.add_viewpoint(
                    'metro_ref_type', metro.referent.type)

    def metro_marks_parsing(self):
        """
        Parses the existent Metronome Markings
        """
        self.metronome_marks_parsing()

    def double_barline_parsing(self):
        """
        Parses the existent double barlines (because they can be important if delimiting phrases)
        """
        for d_bar_off in [barline.offset for barline in self.music_to_parse.flat.getElementsByClass(
                music21.bar.Barline) if barline.type == 'double']:
            utils.get_events_at_offset(self.events, d_bar_off)[
                0].add_viewpoint('double_bar', True)

    def repeat_barline_parsing(self):
        """
        Parses the existent repeat barlines (because they can be important if delimiting phrases)
        and the direction for repeating
        """
        for repeat in self.music_to_parse.flat.getElementsByClass(music21.bar.Repeat):
            events_repeats = utils.get_events_at_offset(
                self.events, repeat.offset)
            if len(events_repeats) == 0:
                self.events[-1].add_viewpoint('end_repeat', True)
                self.events[-1].add_viewpoint('repeat_direction',
                                              repeat.direction)
            else:
                events_repeats[0].add_viewpoint(
                    'repeat_before', True)
                events_repeats[0].add_viewpoint(
                    'repeat_direction', repeat.direction)
