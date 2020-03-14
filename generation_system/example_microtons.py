import os

import music21
from music21 import *
from music21 import converter, corpus

from representation.event import Event
from representation.viewpoint import Viewpoint

file_path = os.sep.join(['myexamples','MicrotonsExample.mxl'])
if os.path.realpath('.').find('generation_system') == -1:
    file_path = os.sep.join(['generation_system', file_path]) 

example = converter.parse(file_path)

#example.flat.show('text')

stream_notes_rests = example.flat.notesAndRests.stream()

events = []

for i in range(len(stream_notes_rests.elements)):
    note_or_rest = stream_notes_rests.elements[i]
    #print(note_or_rest)
    events.append(Event(i, note_or_rest.offset))
    
    if not note_or_rest.isRest:
        events[i].addViewpoint(Viewpoint('pitch', note_or_rest.name))
        events[i].addViewpoint(Viewpoint('octave', note_or_rest.octave))
        #events[i].addViewpoint(Viewpoint('microtonal', note_or_rest.pitch.microtone))
        events[i].addViewpoint(Viewpoint('notehead', note_or_rest.notehead))
        #events[i].addViewpoint(Viewpoint('noteheadfill', note_or_rest.noteheadFill))
        events[i].addViewpoint(Viewpoint('articulation', note_or_rest.articulations))
        events[i].addViewpoint(Viewpoint('expression', note_or_rest.expressions))
        events[i].addViewpoint(Viewpoint('rest', False))
    else:
        events[i].addViewpoint(Viewpoint('rest', True))
    
    events[i].addViewpoint(Viewpoint('duration', note_or_rest.duration.quarterLength))

    #events[i].addViewpoint(Viewpoint('keysig', note_or_rest.)) # Key Signature

    print(events[i].toString())
