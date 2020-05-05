#!/usr/bin/env python3.7
"""
This script presents the class ScoreConverter that converts the events
Generated by the System to a score
"""

import os

import music21

import representation.utils as utils

#from representation.conversor.score_attributes import ARTICULATIONS


class ScoreConversor:
    """
    A class used to parse a musical file.

    Attributes
    ----------
    """

    def __init__(self):
        self.stream = music21.stream.Stream()

    def parse_events(self, events, new_part=True):
        """
        """
        stream = self.stream
        if new_part:
            stream = music21.stream.Part()

        #measures = []
        slurs = []

        last_key_signature = 0
        last_time_signature = ''
        last_metro_value = ''
        for event in events:

            if event.get_viewpoint('timesig') != last_time_signature:
                stream.append(music21.meter.TimeSignature(
                    event.get_viewpoint('timesig')))
                last_time_signature = event.get_viewpoint('timesig')

            if event.get_viewpoint('metro.value') != last_metro_value:
                stream.append(music21.tempo.MetronomeMark(text=event.get_viewpoint('metro.text'),
                                                                number=event.get_viewpoint('metro.value'), referent=music21.note.Note(type=event.get_viewpoint('ref.type'))))
                last_metro_value = event.get_viewpoint('metro.value')

            if event.get_viewpoint('keysig') != last_key_signature:
                stream.append(music21.key.KeySignature(
                    sharps=int(event.get_viewpoint('keysig'))))
                last_key_signature = event.get_viewpoint('keysig')

            note = None
            if event.is_rest():
                note = music21.note.Rest(
                    quarterLength=event.get_viewpoint('duration.length'),
                    type=event.get_viewpoint('duration.type'),
                    dots=event.get_viewpoint('duration.dots'))
            else:
                note = self.convert_note_event(event)

            if event.get_viewpoint('slur.begin'):
                slurs.append(music21.spanner.Slur())
                pass

            stream.append(note)

        
        music21.stream.makeNotation.makeMeasures(stream, inPlace=True)

        if new_part:
            self.stream.append(stream)

        return self.stream

    def convert_note_event(self, event):
        """
        """
        pitch = music21.pitch.Pitch(event.get_viewpoint(
            'dnote') + str(int(event.get_viewpoint('octave'))))

        if event.get_viewpoint('accidental') is not music21.pitch.Accidental('natural').modifier:
            acc = music21.pitch.Accidental('natural')
            acc.modifier = event.get_viewpoint('accidental')
            pitch.accidental = acc

        if pitch.ps != event.get_viewpoint('cpitch'):
            pitch.ps = event.get_viewpoint('cpitch')

        note = music21.note.Note(
            pitch, quarterLength=event.get_viewpoint('duration.length'),
            type=event.get_viewpoint('duration.type'),
            dots=event.get_viewpoint('duration.dots'))

        for articulation in event.get_viewpoint('articulation'):
            note.articulations.append(
                getattr(music21.articulations, articulation.capitalize())())

        if event.get_viewpoint('breath mark'):
            note.articulations.append(music21.articulations.BreathMark())

        for exp in event.get_viewpoint('expression') + event.get_viewpoint('ornamentation'):
            note.expressions.append(
                getattr(music21.expressions, exp.capitalize())())

        if event.get_viewpoint('fermata'):
            note.expressions.append(music21.expressions.Fermata())

        if event.get_viewpoint('rehearsal'):
            note.expressions.append(music21.expressions.RehearsalMark())

        if event.is_grace_note():
            note.getGrace(appogiatura=True, inPlace=True)

        return note
