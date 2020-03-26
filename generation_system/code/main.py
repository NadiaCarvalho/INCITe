#!/usr/bin/env python3.7
"""
This script is the main script of the generation system
"""

import os

from music21 import converter

import representation.utils as utils
from representation.line_parser import LineParser
from representation.vertical_parser import VerticalParser

def main():
    """
    Main function for extracting the viewpoints for examples
    """
    file_path = os.sep.join(['data', 'myexamples', 'bwv1.6.mxl'])
    if os.path.realpath('.').find('code') != -1:
        file_path.replace('code', '')
        file_path = os.sep.join(['..', file_path])

    bach = converter.parse(file_path)
    # bach.flat.show('text')

    voice_events = {}

    for i, part in enumerate(bach.parts):
        voice_events[i] = LineParser(part).parse_line()

    #print(utils.show_sequence_of_viewpoint_without_offset(voice_events[4], 'intfib'))

    vertical_events = VerticalParser(bach).parse_music()
    #[print(str(ev)) for ev in vertical_events]


if __name__ == "__main__":
    main()

    #ka = analysis.floatingKey.KeyAnalyzer(to_parse)
    # ka.windowSize = 8 # int(len(self.measure_offsets)/100)
    # print(ka.run())
    #k = to_parse.analyze('key')
    # print(k.tonalCertainty())

    # Categorization of metrics in bar
    # Ver artigos + código
    # Ver código para tonalCertainty
    # magnitude do 5º coeficiente (ver com value de tonalCertainty)
    # passar segmentos no espaço para um único ponto e calcular a magnitude
