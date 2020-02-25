import music21
from music21 import *
from music21 import corpus, converter

from generation_system.representation.event import Event

bwv295 = corpus.parse('bach/bwv295')
#bwv295.show()

number_events = len(bwv295.asTimespans(flatten=True).allTimePoints())

'''
for part in bwv295.parts: # for each line
    #part.sorted.show() # sorted by offset
    pass
'''

events = []

for i in range(number_events):
    events.append(Event(i, bwv295.asTimespans(flatten=True).allTimePoints()[i]))

for event in events:
    print(event.toString() + '\n')


