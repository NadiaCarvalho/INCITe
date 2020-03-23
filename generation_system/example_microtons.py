import os

from music21 import converter, corpus

import representation.utils as utils
import representation.parser as parser


if __name__== "__main__":
    file_path = os.sep.join(['myexamples','MicrotonsExample.mxl'])
    if os.path.realpath('.').find('generation_system') == -1:
        file_path = os.sep.join(['generation_system', file_path]) 

    example = converter.parse(file_path)
    #example.flat.show('text')
    events = parser.parseLine(example)
    
    print(utils.showSequenceOfViewpointWithoutOffset(events, 'repeat_direction'))
