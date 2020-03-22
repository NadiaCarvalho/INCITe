import os

import numpy as np

import music21
from music21 import *
from music21 import converter, corpus

import representation.utils as utils
from representation.event import Event
from representation.viewpoint import Viewpoint

if __name__== "__main__":
    file_path = os.sep.join(['myexamples','MicrotonsExample.mxl'])
    if os.path.realpath('.').find('generation_system') == -1:
        file_path = os.sep.join(['generation_system', file_path]) 

    example = converter.parse(file_path)

    example.flat.show('text')

    stream_notes_rests = example.flat.notesAndRests.stream()
    measure_offsets = [measure.offset for measure in example.recurse(classFilter='Measure')]

    events = []

    for i in range(len(stream_notes_rests.elements)):
        note_or_rest = stream_notes_rests.elements[i]
        events.append(Event(i, note_or_rest.offset))
        
        # Basic Viewpoints
        if not note_or_rest.isRest:
            events[i].addViewpoint(Viewpoint('pitch_name', note_or_rest.name))
            events[i].addViewpoint(Viewpoint('midi_pitch', note_or_rest.pitch.ps))
            events[i].addViewpoint(Viewpoint('octave', note_or_rest.octave))

            events[i].addViewpoint(Viewpoint('microtonal', note_or_rest.pitch.microtone.cents))

            events[i].addViewpoint(Viewpoint('notehead', note_or_rest.notehead))
            events[i].addViewpoint(Viewpoint('noteheadfill', note_or_rest.noteheadFill))
            events[i].addViewpoint(Viewpoint('articulation', note_or_rest.articulations))
            events[i].addViewpoint(Viewpoint('is_rest', False))
       
            # get index of last event that is a note and not a rest
            last_note_index = utils.getLastEventThatIsNoteBeforeIndex(events)
            if last_note_index is not None:
                events[i].addViewpoint(Viewpoint('seqInt', utils.seqInt(events[i].getViewpoint('midi_pitch'), events[last_note_index].getViewpoint('midi_pitch'))))
                events[i].addViewpoint(Viewpoint('contour', utils.contour(events[i].getViewpoint('midi_pitch'), events[last_note_index].getViewpoint('midi_pitch'))))
                events[i].addViewpoint(Viewpoint('HD_contour', utils.contourHD(events[i].getViewpoint('midi_pitch'), events[last_note_index].getViewpoint('midi_pitch'))))
        else:
            events[i].addViewpoint(Viewpoint('is_rest', True))

        events[i].addViewpoint(Viewpoint('duration_length', note_or_rest.duration.quarterLength))
        events[i].addViewpoint(Viewpoint('duration_type', note_or_rest.duration.type))
        if note_or_rest.duration.isGrace:
            events[i].addViewpoint(Viewpoint('is_grace', True))
        else:
            events[i].addViewpoint(Viewpoint('is_grace', False))

        events[i].addViewpoint(Viewpoint('dots', note_or_rest.duration.dots))
        events[i].addViewpoint(Viewpoint('expression', note_or_rest.expressions))

        if any(isinstance(note, music21.expressions.Fermata) for note in note_or_rest.expressions):
            events[i].addViewpoint(Viewpoint('fermata', True)) 
        else:
            events[i].addViewpoint(Viewpoint('fermata', False)) 

        if note_or_rest.offset in measure_offsets:
            if not note_or_rest.duration.isGrace:
                events[i].addViewpoint(Viewpoint('fib', True))
                events[i].addViewpoint(Viewpoint('intfib', 0.0))
                
                last_fib_index = measure_offsets.index(note_or_rest.offset) - 1
                if last_fib_index == -1:
                    last_fib_index = 0
                last_fibs = [event for event in utils.getEventsAtOffset(events, measure_offsets[last_fib_index]) if (not event.isGraceNote() and not event.isRest())]
                events[i].addViewpoint(Viewpoint('thrbar', utils.seqInt(events[i].getViewpoint('midi_pitch'), last_fibs[0].getViewpoint('midi_pitch'))))
        else:
            events[i].addViewpoint(Viewpoint('fib', False))
            if not note_or_rest.isRest and not note_or_rest.duration.isGrace:      
                closest_offset_index = measure_offsets.index(min(measure_offsets, key=lambda x:abs(x - note_or_rest.offset)))
                if note_or_rest.offset < measure_offsets[closest_offset_index]:
                    closest_offset_index = closest_offset_index - 1
                closest_fibs = [event for event in utils.getEventsAtOffset(events, measure_offsets[closest_offset_index]) if (not event.isGraceNote() and not event.isRest())]
                if len(closest_fibs) == 1:
                    events[i].addViewpoint(Viewpoint('intfib', utils.seqInt(events[i].getViewpoint('midi_pitch'), closest_fibs[0].getViewpoint('midi_pitch'))))

    for dynamic in example.flat.getElementsByClass(dynamics.Dynamic):
        for event in utils.getEventsAtOffset(events, dynamic.offset):
            event.addViewpoint(Viewpoint('dynamic', dynamic.value))
    
    for grace_note in utils.getGraceNotes(events):
        index = events.index(grace_note)
        grace_note.addViewpoint(Viewpoint('intfib', utils.seqInt(events[index + 1].getViewpoint('midi_pitch'), grace_note.getViewpoint('midi_pitch'))))

    keys = [keySignature for keySignature in example.flat.getElementsByClass(key.KeySignature)]
    for i in range(len(keys)):
        next_key_offset = None
        if i != len(keys) - 1:
            next_key_offset = keys[i+1].offset
        for event in utils.getEventBetweenOffsetsIncluding(events, keys[i].offset, next_key_offset):
            event.addViewpoint(Viewpoint('keysig', keys[i].sharps))

    time_sigs = [timeSignature for timeSignature in example.flat.getElementsByClass(meter.TimeSignature)]
    for i in range(len(time_sigs)):
        next_time_sig_offset = None
        if i != len(time_sigs) - 1:
            next_time_sig_offset = time_sigs[i+1].offset
        for event in utils.getEventBetweenOffsetsIncluding(events, time_sigs[i].offset, next_time_sig_offset):
            event.addViewpoint(Viewpoint('timesig', time_sigs[i].ratioString))


    double_barlines = [barline.offset for barline in example.flat.getElementsByClass(bar.Barline) if barline.type == 'double']
    for d_bar in double_barlines:
        utils.getEventsAtOffset(events, d_bar.offset)[0].addViewpoint(Viewpoint('double_bar_before', True))

    repeats =  [repeat for repeat in example.flat.getElementsByClass(bar.Repeat)]
    for repeat in repeats:
        events_repeats = utils.getEventsAtOffset(events, repeat.offset)
        if len(events_repeats) == 0: 
            events[-1].addViewpoint(Viewpoint('repeat_after', True))
            events[-1].addViewpoint(Viewpoint('repeat_direction', repeat.direction))
        else:
            events_repeats[0].addViewpoint(Viewpoint('repeat_before', True))
            events_repeats[0].addViewpoint(Viewpoint('repeat_direction', repeat.direction))

    #ka = analysis.floatingKey.KeyAnalyzer(example)
    #ka.windowSize = 8 # int(len(measure_offsets)/100)
    #print(ka.run())
    #events[i].addViewpoint(Viewpoint('keysig', note_or_rest.)) # Key Signature
    #k = example.analyze('key')
    #print(k.tonalCertainty())
    
    print(utils.showSequenceOfViewpointWithoutOffset(events, 'timesig'))
