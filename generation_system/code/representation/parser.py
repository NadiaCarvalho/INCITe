#!/usr/bin/env python3.7
"""
This script presents the class Event that represents an event in a piece of music
"""

from fractions import Fraction

import music21

import representation.utils as utils
from representation.event import Event
from representation.viewpoint import Viewpoint


class LineParser:
    """
    Class LineParser
    """

    def __init__(self, music_to_parse):
        self.music_to_parse = music_to_parse
        self.events = []

        # Get offsets of beginnings of measures
        self.measure_offsets = [measure.offset for measure in self.music_to_parse.recurse(
            classFilter='Measure')]

    def parse_line(self):
        """
        Returns the events from a line with viewpoints
        """
        self.note_and_rests_parsing()
        self.intfib_grace_notes_parsing()
        self.dynamics_parsing()
        self.key_signatures_parsing()
        self.time_signatures_parsing()
        self.double_barline_parsing()
        self.repeat_barline_parsing()

        return self.events

    def note_and_rests_parsing(self):
        """
        Parses the note/rest events
        """
        # Get Notes and Rests only
        stream_notes_rests = self.music_to_parse.flat.notesAndRests.stream()

        for i, note_or_rest in enumerate(stream_notes_rests.elements):
            self.events.append(Event(note_or_rest.offset))

            if not note_or_rest.isRest:
                # Basic Viewpoints
                self.events[i].add_viewpoint(
                    Viewpoint('pitch_name', note_or_rest.name))
                self.events[i].add_viewpoint(
                    Viewpoint('midi_pitch', note_or_rest.pitch.ps))
                self.events[i].add_viewpoint(
                    Viewpoint('octave', note_or_rest.octave))
                self.events[i].add_viewpoint(
                    Viewpoint('microtonal', note_or_rest.pitch.microtone.cents))
                self.events[i].add_viewpoint(
                    Viewpoint('notehead', note_or_rest.notehead))
                self.events[i].add_viewpoint(
                    Viewpoint('noteheadfill', note_or_rest.noteheadFill))
                self.events[i].add_viewpoint(
                    Viewpoint('articulation', note_or_rest.articulations))
                self.events[i].add_viewpoint(Viewpoint('is_rest', False))
                self.contours_parsing(i)
            else:
                self.events[i].add_viewpoint(Viewpoint('is_rest', True))

            self.events[i].add_viewpoint(
                Viewpoint('duration_length', note_or_rest.duration.quarterLength))
            self.events[i].add_viewpoint(
                Viewpoint('duration_type', note_or_rest.duration.type))
            self.events[i].add_viewpoint(
                Viewpoint('dots', note_or_rest.duration.dots))

            if note_or_rest.duration.isGrace:
                self.events[i].add_viewpoint(Viewpoint('is_grace', True))
            else:
                self.events[i].add_viewpoint(Viewpoint('is_grace', False))

            self.events[i].add_viewpoint(
                Viewpoint('expression', note_or_rest.expressions))
            self.fermata_parsing(i)

            self.measure_info_parsing(i, note_or_rest)

    def contours_parsing(self, index):
        """
        Parses the contours for an event
        """
        # get index of last event that is a note and not a rest
        last_note_index = utils.get_first_event_that_is_note_before_index(
            self.events)
        if last_note_index is not None:
            midi_pitch_note = self.events[index].get_viewpoint(
                'midi_pitch')
            midi_pitch_last_note = self.events[last_note_index].get_viewpoint(
                'midi_pitch')
            self.events[index].add_viewpoint(
                Viewpoint('seqInt', utils.seq_int(midi_pitch_note, midi_pitch_last_note)))
            self.events[index].add_viewpoint(
                Viewpoint('contour', utils.contour(midi_pitch_note, midi_pitch_last_note)))
            self.events[index].add_viewpoint(Viewpoint(
                'HD_contour', utils.contour_hd(midi_pitch_note, midi_pitch_last_note)))

    def fermata_parsing(self, index):
        """
        Parses the existence of a fermata in an event
        """
        expressions = self.events[index].get_viewpoint('expression').get_info()
        if any(isinstance(note, music21.expressions.Fermata) for note in expressions):
            self.events[index].add_viewpoint(Viewpoint('fermata', True))
        else:
            self.events[index].add_viewpoint(Viewpoint('fermata', False))

    def get_first_fib_before_fib(self, note_or_rest):
        """
        Returns the first fib before an event that is a fib
        """
        index = self.measure_offsets.index(note_or_rest.offset)
        fib_index = index - (1, 0)[index == 0]
        return [event for event in utils.get_events_at_offset(
            self.events, self.measure_offsets[fib_index]) if utils.not_rest_or_grace(event)][0]

    def get_first_fib_before_non_fib(self, note_or_rest):
        """
        Returns the first fib before an event that is not a fib
        """
        index = self.measure_offsets.index(
            min(self.measure_offsets, key=lambda x: abs(x - note_or_rest.offset)))
        fib_index = (
            index, index-1)[bool(note_or_rest.offset < self.measure_offsets[index])]
        return[event for event in utils.get_events_at_offset(
            self.events, self.measure_offsets[fib_index]) if not event.is_grace_note()][0]

    def parsing_fib_element(self, index, note_or_rest):
        """
        Parses the information for an event that is the first element in bar
        """
        self.events[index].add_viewpoint(Viewpoint('fib', True))
        self.events[index].add_viewpoint(Viewpoint('intfib', 0.0))
        cur_fib_midi = self.events[index].get_viewpoint('midi_pitch')
        last_fib_midi = self.get_first_fib_before_fib(
            note_or_rest).get_viewpoint('midi_pitch')
        self.events[index].add_viewpoint(Viewpoint('thrbar', utils.seq_int(
            cur_fib_midi, last_fib_midi)))

    def parsing_non_fib_element(self, index, note_or_rest):
        """
        Parses the information for an event that is not the first element in bar
        """
        self.events[index].add_viewpoint(Viewpoint('fib', False))
        last_fib = self.get_first_fib_before_non_fib(note_or_rest)
        if not note_or_rest.isRest and utils.not_rest_or_grace(last_fib):
            cur_midi = self.events[index].get_viewpoint('midi_pitch')
            last_fib_midi = last_fib.get_viewpoint('midi_pitch')
            self.events[index].add_viewpoint(Viewpoint('intfib', utils.seq_int(
                cur_midi, last_fib_midi)))

    def measure_info_parsing(self, index, note_or_rest):
        """
        Parses the information relating to order in a measure
        and melodic sequences with other elements of a measure
        for an event
        """
        if not note_or_rest.duration.isGrace:
            components = note_or_rest.beatStr.split(' ')
            posinbar = int(
                components[0]) + (Fraction(components[1]) if len(components) > 1 else 0) - 1
            self.events[index].add_viewpoint(Viewpoint('posinbar', posinbar))

        if note_or_rest.offset in self.measure_offsets and not note_or_rest.duration.isGrace:
            self.parsing_fib_element(index, note_or_rest)
        else:
            self.parsing_non_fib_element(index, note_or_rest)

    def dynamics_parsing(self):
        """
        Parses the existent dynamics information
        """
        for dynamic in self.music_to_parse.flat.getElementsByClass(music21.dynamics.Dynamic):
            for event in utils.get_events_at_offset(self.events, dynamic.offset):
                event.add_viewpoint(Viewpoint('dynamic', dynamic.value))

    def intfib_grace_notes_parsing(self):
        """
        Parses the intfib information for fib grace_notes, as they are
        not really the fib even if they are the first element in a bar
        """
        for grace_note in utils.get_grace_notes(self.events):
            fib_midi = self.events[self.events.index(
                grace_note) + 1].get_viewpoint('midi_pitch')
            grace_note.add_viewpoint(Viewpoint('intfib', utils.seq_int(
                fib_midi, grace_note.get_viewpoint('midi_pitch'))))

    def key_signatures_parsing(self):
        """
        Parses the existent key signatures information
        """
        keys = list(self.music_to_parse.flat.getElementsByClass(
            music21.key.KeySignature))
        for i, _ in enumerate(keys):
            offset = (None if i == (len(keys)-1) else keys[i+1].offset)
            for event in utils.get_evs_bet_offs_inc(self.events, keys[i].offset, offset):
                event.add_viewpoint(Viewpoint('keysig', keys[i].sharps))

    def time_signatures_parsing(self):
        """
        Parses the existent key signatures information
        """
        time_sigs = list(self.music_to_parse.flat.getElementsByClass(
            music21.meter.TimeSignature))
        for i, _ in enumerate(time_sigs):
            offset = (None if i == (len(time_sigs)-1)
                      else time_sigs[i+1].offset)
            for event in utils.get_evs_bet_offs_inc(self.events, time_sigs[i].offset, offset):
                event.add_viewpoint(
                    Viewpoint('timesig', time_sigs[i].ratioString))

    def double_barline_parsing(self):
        """
        Parses the existent double barlines (because they can be important if delimiting phrases)
        """
        for d_bar_off in [barline.offset for barline in self.music_to_parse.flat.getElementsByClass(
                music21.bar.Barline) if barline.type == 'double']:
            utils.get_events_at_offset(self.events, d_bar_off)[
                0].add_viewpoint(Viewpoint('double_bar_before', True))

    def repeat_barline_parsing(self):
        """
        Parses the existent repeat barlines (because they can be important if delimiting phrases)
        and the direction for repeating
        """
        for repeat in self.music_to_parse.flat.getElementsByClass(music21.bar.Repeat):
            events_repeats = utils.get_events_at_offset(
                self.events, repeat.offset)
            if len(events_repeats) == 0:
                self.events[-1].add_viewpoint(Viewpoint('repeat_after', True))
                self.events[-1].add_viewpoint(Viewpoint('repeat_direction',
                                                        repeat.direction))
            else:
                events_repeats[0].add_viewpoint(
                    Viewpoint('repeat_before', True))
                events_repeats[0].add_viewpoint(
                    Viewpoint('repeat_direction', repeat.direction))
