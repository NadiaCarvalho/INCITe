#!/usr/bin/env python3.7
"""
This script is the main script of the generation system
"""

import os

from music21 import converter

import representation.utils as utils
from representation.parser import LineParser

if __name__ == "__main__":
    FILE_PATH = os.sep.join(['data', 'myexamples', 'bwv1.6.mxl'])
    if os.path.realpath('.').find('code') != -1:
        FILE_PATH.replace('code', '')
        FILE_PATH = os.sep.join(['..', FILE_PATH])

    EXAMPLE = converter.parse(FILE_PATH)
    # example.flat.show('text')
    EVENTS = LineParser(EXAMPLE.parts[0]).parse_line()

    print(utils.show_sequence_of_viewpoint_without_offset(EVENTS, 'intfib'))

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
