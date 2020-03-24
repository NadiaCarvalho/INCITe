import music21

import representation.utils as utils
from representation.event import Event
from representation.viewpoint import Viewpoint


class LineParser:
    def __init__(self, music_to_parse):
        self.music_to_parse = music_to_parse
        self.events = []

    def parseLine(self):

        # Get offsets of beginnings of measures
        self.measure_offsets = [measure.offset for measure in self.music_to_parse.recurse(
            classFilter='Measure')]
        self.time_sigs = [timeSignature for timeSignature in self.music_to_parse.flat.getElementsByClass(
            music21.meter.TimeSignature)]

        self.noteAndRestsParsing()
        self.intfibGraceNotesParsing()
        self.dynamicsParsing()
        self.keySignsParsing()
        self.doubleBarlineParsing()
        self.repeatBarlineParsing()

        return self.events

    def noteAndRestsParsing(self):
        # Get Notes and Rests only
        stream_notes_rests = self.music_to_parse.flat.notesAndRests.stream()

        for i in range(len(stream_notes_rests.elements)):
            note_or_rest = stream_notes_rests.elements[i]
            self.events.append(Event(i, note_or_rest.offset))

            if not note_or_rest.isRest:
                # Basic Viewpoints
                self.events[i].addViewpoint(
                    Viewpoint('pitch_name', note_or_rest.name))
                self.events[i].addViewpoint(
                    Viewpoint('midi_pitch', note_or_rest.pitch.ps))
                self.events[i].addViewpoint(
                    Viewpoint('octave', note_or_rest.octave))
                self.events[i].addViewpoint(
                    Viewpoint('microtonal', note_or_rest.pitch.microtone.cents))
                self.events[i].addViewpoint(
                    Viewpoint('notehead', note_or_rest.notehead))
                self.events[i].addViewpoint(
                    Viewpoint('noteheadfill', note_or_rest.noteheadFill))
                self.events[i].addViewpoint(
                    Viewpoint('articulation', note_or_rest.articulations))
                self.events[i].addViewpoint(Viewpoint('is_rest', False))
                self.contoursParsing(i)
            else:
                self.events[i].addViewpoint(Viewpoint('is_rest', True))

            self.events[i].addViewpoint(
                Viewpoint('duration_length', note_or_rest.duration.quarterLength))
            self.events[i].addViewpoint(
                Viewpoint('duration_type', note_or_rest.duration.type))
            self.events[i].addViewpoint(
                Viewpoint('dots', note_or_rest.duration.dots))

            if note_or_rest.duration.isGrace:
                self.events[i].addViewpoint(Viewpoint('is_grace', True))
            else:
                self.events[i].addViewpoint(Viewpoint('is_grace', False))

            self.events[i].addViewpoint(
                Viewpoint('expression', note_or_rest.expressions))
            self.fermataParsing(i)

            self.barAndMeasureRelatedInformationParsing(i, note_or_rest)

    def contoursParsing(self, index):
        # get index of last event that is a note and not a rest
        last_note_index = utils.getLastEventThatIsNoteBeforeIndex(self.events)
        if last_note_index is not None:
            self.events[index].addViewpoint(Viewpoint('seqInt', utils.seqInt(self.events[index].getViewpoint(
                'midi_pitch'), self.events[last_note_index].getViewpoint('midi_pitch'))))
            self.events[index].addViewpoint(Viewpoint('contour', utils.contour(self.events[index].getViewpoint(
                'midi_pitch'), self.events[last_note_index].getViewpoint('midi_pitch'))))
            self.events[index].addViewpoint(Viewpoint('HD_contour', utils.contourHD(
                self.events[index].getViewpoint('midi_pitch'), self.events[last_note_index].getViewpoint('midi_pitch'))))

    def fermataParsing(self, index):
        if any(isinstance(note, music21.expressions.Fermata) for note in self.events[index].getViewpoint('expression').getInfo()):
            self.events[index].addViewpoint(Viewpoint('fermata', True))
        else:
            self.events[index].addViewpoint(Viewpoint('fermata', False))

    def timeSigParsing(self, index, note_or_rest):
        time_index = self.time_sigs.index(
            min(self.time_sigs, key=lambda x: abs(x.offset - note_or_rest.offset)))
        self.events[index].addViewpoint(
            Viewpoint('timesig', self.time_sigs[(time_index, time_index-1)[bool(note_or_rest.offset < self.time_sigs[time_index].offset)]].ratioString))

    def getLastFibBeforeFib(self, note_or_rest):
        index = self.measure_offsets.index(note_or_rest.offset)
        return [event for event in utils.getEventsAtOffset(
            self.events, self.measure_offsets[(index - 1, 0)[index == 0]]) if not (event.isGraceNote() or event.isRest())][0]

    def getLastFibBeforeNonFib(self, note_or_rest):
        index = self.measure_offsets.index(
            min(self.measure_offsets, key=lambda x: abs(x - note_or_rest.offset)))
        return[event for event in utils.getEventsAtOffset(
            self.events, self.measure_offsets[(index, index-1)[bool(note_or_rest.offset < self.measure_offsets[index])]]) if not event.isGraceNote()][0]

    def barAndMeasureRelatedInformationParsing(self, index, note_or_rest):
        self.timeSigParsing(index, note_or_rest)
        if note_or_rest.offset in self.measure_offsets:
            if not note_or_rest.duration.isGrace:
                self.events[index].addViewpoint(Viewpoint('fib', True))
                self.events[index].addViewpoint(Viewpoint('intfib', 0.0))
                self.events[index].addViewpoint(Viewpoint('posinbar', 0))
                self.events[index].addViewpoint(Viewpoint('thrbar', utils.seqInt(
                    self.events[index].getViewpoint('midi_pitch'), self.getLastFibBeforeFib(note_or_rest).getViewpoint('midi_pitch'))))
        else:
            self.events[index].addViewpoint(Viewpoint('fib', False))
            last_fib = self.getLastFibBeforeNonFib(note_or_rest)
            if not (note_or_rest.isRest or note_or_rest.duration.isGrace) and not last_fib.isRest():
                self.events[index].addViewpoint(Viewpoint('intfib', utils.seqInt(
                    self.events[index].getViewpoint('midi_pitch'), last_fib.getViewpoint('midi_pitch'))))

            print(self.events[index].getOffset() - last_fib.getOffset())

    def dynamicsParsing(self):
        for dynamic in self.music_to_parse.flat.getElementsByClass(music21.dynamics.Dynamic):
            for event in utils.getEventsAtOffset(self.events, dynamic.offset):
                event.addViewpoint(Viewpoint('dynamic', dynamic.value))

    def intfibGraceNotesParsing(self):
        for grace_note in utils.getGraceNotes(self.events):
            grace_note.addViewpoint(Viewpoint('intfib', utils.seqInt(
                self.events[self.events.index(grace_note) + 1].getViewpoint('midi_pitch'), grace_note.getViewpoint('midi_pitch'))))

    def keySignsParsing(self):
        keys = [keySignature for keySignature in self.music_to_parse.flat.getElementsByClass(
            music21.key.KeySignature)]
        for i in range(len(keys)):
            for event in utils.getEventBetweenOffsetsIncluding(self.events, keys[i].offset, (None, keys[i+1].offset)[i == len(keys)-1]):
                event.addViewpoint(Viewpoint('keysig', keys[i].sharps))

    def doubleBarlineParsing(self):
        double_barlines = [barline.offset for barline in self.music_to_parse.flat.getElementsByClass(
            music21.bar.Barline) if barline.type == 'double']
        for d_bar in double_barlines:
            utils.getEventsAtOffset(self.events, d_bar.offset)[
                0].addViewpoint(Viewpoint('double_bar_before', True))

    def repeatBarlineParsing(self):
        repeats = [
            repeat for repeat in self.music_to_parse.flat.getElementsByClass(music21.bar.Repeat)]
        for repeat in repeats:
            events_repeats = utils.getEventsAtOffset(
                self.events, repeat.offset)
            if len(events_repeats) == 0:
                self.events[-1].addViewpoint(Viewpoint('repeat_after', True))
                self.events[-1].addViewpoint(Viewpoint('repeat_direction',
                                                       repeat.direction))
            else:
                events_repeats[0].addViewpoint(
                    Viewpoint('repeat_before', True))
                events_repeats[0].addViewpoint(
                    Viewpoint('repeat_direction', repeat.direction))

    #ka = analysis.floatingKey.KeyAnalyzer(to_parse)
    # ka.windowSize = 8 # int(len(self.measure_offsets)/100)
    # print(ka.run())
    #k = to_parse.analyze('key')
    # print(k.tonalCertainty())

    # Categorization of metrics in bar
    # Ver artigos + código
    # Ver código para tonalCertainty
    # magnitude do 5º coeficiente (ver com value de tonalCertainty)
    # passar segmentos no espaço para um único ponto e calcular a magnitude
