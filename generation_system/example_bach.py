import music21
from music21 import *
from music21 import corpus, converter

from representation.event import Event

bwv295 = corpus.parse('bach/bwv295')
#bwv295.show()

part_viewpoints = []

for part in bwv295.parts: # for each line
    #part.sorted.show() # sorted by offset
    pass

'''
For Conjoined Events
'''
events = []
number_events = len(bwv295.asTimespans(flatten=True).allTimePoints())

for i in range(number_events):
    events.append(Event(i, bwv295.asTimespans(flatten=True).allTimePoints()[i]))

for event in events:
    print(event.toString() + '\n')


