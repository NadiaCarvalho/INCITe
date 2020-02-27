import music21
from music21 import *
from music21 import corpus, converter

from representation.event import Event

example = converter.parse('database\examples\VoiceExample.mxl')

print(example.elements)