import music21
from music21 import *

import representation.utils as utils
from representation.event import Event
from representation.viewpoint import Viewpoint

class LineParser:
    def __init__(self, music_to_parse):
        self.music_to_parse = music_to_parse
        self.events = []
    
    def parseLine(self):
        self.noteAndRestsParsing()
        self.intfibGraceNotesParsing()
        self.dynamicsParsing()
        self.keySignsParsing()
        self.timeSignsParsing()
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
                self.events[i].addViewpoint(Viewpoint('pitch_name', note_or_rest.name))
                self.events[i].addViewpoint(Viewpoint('midi_pitch', note_or_rest.pitch.ps))
                self.events[i].addViewpoint(Viewpoint('octave', note_or_rest.octave))
                self.events[i].addViewpoint(Viewpoint('microtonal', note_or_rest.pitch.microtone.cents))
                self.events[i].addViewpoint(Viewpoint('notehead', note_or_rest.notehead))
                self.events[i].addViewpoint(Viewpoint('noteheadfill', note_or_rest.noteheadFill))
                self.events[i].addViewpoint(Viewpoint('articulation', note_or_rest.articulations))
                self.events[i].addViewpoint(Viewpoint('is_rest', False))
                self.contoursParsing(i)
            else:
                self.events[i].addViewpoint(Viewpoint('is_rest', True))
            
            self.events[i].addViewpoint(Viewpoint('duration_length', note_or_rest.duration.quarterLength))
            self.events[i].addViewpoint(Viewpoint('duration_type', note_or_rest.duration.type))
            self.events[i].addViewpoint(Viewpoint('dots', note_or_rest.duration.dots))

            if note_or_rest.duration.isGrace:
                self.events[i].addViewpoint(Viewpoint('is_grace', True))
            else:
                self.events[i].addViewpoint(Viewpoint('is_grace', False))

            self.events[i].addViewpoint(Viewpoint('expression', note_or_rest.expressions))
            self.fermataParsing(i)

            self.fibRelatedInformationParsing(i, note_or_rest)

    def contoursParsing(self, index):
        # get index of last event that is a note and not a rest
        last_note_index = utils.getLastEventThatIsNoteBeforeIndex(self.events)
        if last_note_index is not None:
            self.events[index].addViewpoint(Viewpoint('seqInt', utils.seqInt(self.events[index].getViewpoint('midi_pitch'), self.events[last_note_index].getViewpoint('midi_pitch'))))
            self.events[index].addViewpoint(Viewpoint('contour', utils.contour(self.events[index].getViewpoint('midi_pitch'), self.events[last_note_index].getViewpoint('midi_pitch'))))
            self.events[index].addViewpoint(Viewpoint('HD_contour', utils.contourHD(self.events[index].getViewpoint('midi_pitch'), self.events[last_note_index].getViewpoint('midi_pitch'))))

    def fermataParsing(self, index):
        if any(isinstance(note, music21.expressions.Fermata) for note in self.events[index].getViewpoint('expression').getInfo()):
            self.events[index].addViewpoint(Viewpoint('fermata', True)) 
        else:
            self.events[index].addViewpoint(Viewpoint('fermata', False)) 

    def fibRelatedInformationParsing(self, index, note_or_rest):
        # Get offsets of beginnings of measures
        measure_offsets = [measure.offset for measure in self.music_to_parse.recurse(classFilter='Measure')]

        if note_or_rest.offset in measure_offsets:
            if not note_or_rest.duration.isGrace:
                self.events[index].addViewpoint(Viewpoint('fib', True))
                self.events[index].addViewpoint(Viewpoint('intfib', 0.0))
                
                last_fib_index = measure_offsets.index(note_or_rest.offset) - 1
                if last_fib_index == -1:
                    last_fib_index = 0

                last_fibs = [event for event in utils.getEventsAtOffset(self.events, measure_offsets[last_fib_index]) if not (event.isGraceNote() or event.isRest())]
                self.events[index].addViewpoint(Viewpoint('thrbar', utils.seqInt(self.events[index].getViewpoint('midi_pitch'), last_fibs[0].getViewpoint('midi_pitch'))))
        else:
            self.events[index].addViewpoint(Viewpoint('fib', False))
            if not note_or_rest.isRest and not note_or_rest.duration.isGrace:      
                closest_offset_index = measure_offsets.index(min(measure_offsets, key=lambda x:abs(x - note_or_rest.offset)))
                if note_or_rest.offset < measure_offsets[closest_offset_index]:
                    closest_offset_index = closest_offset_index - 1
                
                closest_fibs = [event for event in utils.getEventsAtOffset(self.events, measure_offsets[closest_offset_index]) if not (event.isGraceNote() or event.isRest())]
                if len(closest_fibs) == 1:
                    self.events[index].addViewpoint(Viewpoint('intfib', utils.seqInt(self.events[index].getViewpoint('midi_pitch'), closest_fibs[0].getViewpoint('midi_pitch'))))

    def dynamicsParsing(self):
        for dynamic in self.music_to_parse.flat.getElementsByClass(dynamics.Dynamic):
            for event in utils.getEventsAtOffset(self.events, dynamic.offset):
                event.addViewpoint(Viewpoint('dynamic', dynamic.value))
    
    def intfibGraceNotesParsing(self):
        for grace_note in utils.getGraceNotes(self.events):
            index = self.events.index(grace_note)
            grace_note.addViewpoint(Viewpoint('intfib', utils.seqInt(self.events[index + 1].getViewpoint('midi_pitch'), grace_note.getViewpoint('midi_pitch'))))

    def keySignsParsing(self):
        keys = [keySignature for keySignature in self.music_to_parse.flat.getElementsByClass(key.KeySignature)]
        for i in range(len(keys)):
            next_key_offset = None
            if i != len(keys) - 1:
                next_key_offset = keys[i+1].offset
            for event in utils.getEventBetweenOffsetsIncluding(self.events, keys[i].offset, next_key_offset):
                event.addViewpoint(Viewpoint('keysig', keys[i].sharps))

    def timeSignsParsing(self):
        time_sigs = [timeSignature for timeSignature in self.music_to_parse.flat.getElementsByClass(meter.TimeSignature)]
        for i in range(len(time_sigs)):
            next_time_sig_offset = None
            if i != len(time_sigs) - 1:
                next_time_sig_offset = time_sigs[i+1].offset
            for event in utils.getEventBetweenOffsetsIncluding(self.events, time_sigs[i].offset, next_time_sig_offset):
                event.addViewpoint(Viewpoint('timesig', time_sigs[i].ratioString))

    def doubleBarlineParsing(self):
        double_barlines = [barline.offset for barline in self.music_to_parse.flat.getElementsByClass(bar.Barline) if barline.type == 'double']
        for d_bar in double_barlines:
            utils.getEventsAtOffset(self.events, d_bar.offset)[0].addViewpoint(Viewpoint('double_bar_before', True))

    def repeatBarlineParsing(self):
        repeats =  [repeat for repeat in self.music_to_parse.flat.getElementsByClass(bar.Repeat)]
        for repeat in repeats:
            events_repeats = utils.getEventsAtOffset(self.events, repeat.offset)
            if len(events_repeats) == 0: 
                events[-1].addViewpoint(Viewpoint('repeat_after', True))
                events[-1].addViewpoint(Viewpoint('repeat_direction', repeat.direction))
            else:
                events_repeats[0].addViewpoint(Viewpoint('repeat_before', True))
                events_repeats[0].addViewpoint(Viewpoint('repeat_direction', repeat.direction))








        
    
    


    #ka = analysis.floatingKey.KeyAnalyzer(to_parse)
    #ka.windowSize = 8 # int(len(measure_offsets)/100)
    #print(ka.run())
    #k = to_parse.analyze('key')
    #print(k.tonalCertainty())
    
   

    # Categorization of metrics in bar 
    # Ver artigos + código
    # Ver código para tonalCertainty
    # magnitude do 5º coeficiente (ver com value de tonalCertainty)
    # passar segmentos no espaço para um único ponto e calcular a magnitude