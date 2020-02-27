import os

import music21
from music21 import *
from music21 import converter, corpus

from representation.event import Event

example = converter.parse(os.sep.join(['myexamples','VoiceExample.mxl']))

print(example.elements)
