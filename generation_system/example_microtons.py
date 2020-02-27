import os

import music21
from music21 import *
from music21 import converter, corpus

from representation.event import Event
from representation.viewpoint import Viewpoint

example = converter.parse(os.sep.join(['myexamples','MicrotonsExample.mxl']))

#example.flat.show('text')

stream_notes_rests = example.flat.notesAndRests.stream()

events = []

for i in range(len(stream_notes_rests.elements)):
    note_or_rest = stream_notes_rests.elements[i]
    print(note_or_rest)
    events.append(Event(i, note_or_rest.offset))
    
    if not note_or_rest.isRest:
        events[i].addViewpoint(Viewpoint('pitch', note_or_rest.pitch))
    else:
        events[i].addViewpoint(Viewpoint('pitch', 'rest'))
    
    events[i].addViewpoint(Viewpoint('duration', note_or_rest.duration.quarterLength))

    print(events[i].toString())
