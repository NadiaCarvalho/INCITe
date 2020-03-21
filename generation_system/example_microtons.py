import os

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

    #example.flat.show('text')

    stream_notes_rests = example.flat.notesAndRests.stream()
    dynamics = example.flat.getElementsByClass(dynamics.Dynamic)

    events = []

    for i in range(len(stream_notes_rests.elements)):
        note_or_rest = stream_notes_rests.elements[i]
        events.append(Event(i, note_or_rest.offset))
        #print(example.containerInHierarchy(note_or_rest).id)
        
        # Basic Viewpoints
        if not note_or_rest.isRest:
            events[i].addViewpoint(Viewpoint('pitch_name', note_or_rest.name))
            events[i].addViewpoint(Viewpoint('midi_pitch', note_or_rest.pitch.ps))
            events[i].addViewpoint(Viewpoint('octave', note_or_rest.octave))

            events[i].addViewpoint(Viewpoint('microtonal', note_or_rest.pitch.microtone.cents))

            events[i].addViewpoint(Viewpoint('notehead', note_or_rest.notehead))
            #events[i].addViewpoint(Viewpoint('noteheadfill', note_or_rest.noteheadFill))
            events[i].addViewpoint(Viewpoint('articulation', note_or_rest.articulations))
            events[i].addViewpoint(Viewpoint('is_rest', False))
       
            # get index of last event that is a note and not a rest
            last_note_index = utils.getLastEventThatIsNoteBeforeIndex(events)
            if last_note_index is not None:
                events[i].addViewpoint(Viewpoint('contour', utils.contour(events[i].getViewpoint('midi_pitch'), events[last_note_index].getViewpoint('midi_pitch'))))
                events[i].addViewpoint(Viewpoint('HD_contour', utils.contourHD(events[i].getViewpoint('midi_pitch'), events[last_note_index].getViewpoint('midi_pitch'))))
        else:
            events[i].addViewpoint(Viewpoint('is_rest', True))
        
        events[i].addViewpoint(Viewpoint('duration', note_or_rest.duration.quarterLength))
        if note_or_rest.duration.isGrace:
            events[i].addViewpoint(Viewpoint('is_grace', True))
        else:
            events[i].addViewpoint(Viewpoint('is_grace', False))

        events[i].addViewpoint(Viewpoint('dots', note_or_rest.duration.dots))
        events[i].addViewpoint(Viewpoint('expression', note_or_rest.expressions))


        


        #events[i].addViewpoint(Viewpoint('keysig', note_or_rest.)) # Key Signature
    
    for event in events:
        event_offset = event.getOffset()

        for dynamic in dynamics:
            if dynamic.offset == event_offset:
                event.addViewpoint(Viewpoint('dynamic', dynamic.value))
        
        #for element in example.flat.getElementsByOffset(event_offset):

        print(event.toString())
