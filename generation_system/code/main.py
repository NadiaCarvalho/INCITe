import os

from music21 import converter, corpus

import representation.utils as utils
from representation.parser import LineParser

if __name__ == "__main__":
    file_path = os.sep.join(['data', 'myexamples', 'MicrotonsExample.mxl'])
    if os.path.realpath('.').find('code') != -1:
        file_path.replace('code', '')
        file_path = os.sep.join(['..', file_path])

    example = converter.parse(file_path)
    # example.flat.show('text')
    events = LineParser(example.parts[0]).parseLine()

    print(utils.showSequenceOfViewpointWithoutOffset(events, 'posinbar'))
