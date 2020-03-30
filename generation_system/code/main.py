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
    name = 'bwv1.6.2.mxl' #'MicrotonsExample.mxl' 
    file_path = os.sep.join(['data', 'myexamples', name])
    if os.path.realpath('.').find('code') != -1:
        file_path.replace('code', '')
        file_path = os.sep.join(['..', file_path])

    bach = converter.parse(file_path)
    # bach.flat.show('text')

    part_events = {}

    for i, part in enumerate(bach.parts):
        if part.isSequence():
            print('Processing part {}'.format(str(i)))
            part_events[i] = LineParser(part).parse_line()
        else:
            pass # Process part with more

    #print(utils.show_sequence_of_viewpoint_without_offset(part_events[4], 'intfib'))

    if (len(bach.parts) > 1 or bach.parts[0].hasVoices() or len(bach.parts[0].getOverlaps()) > 0):
        print('Processing Vertical Events')
        vertical_events = VerticalParser(bach).parse_music()
        print(utils.show_sequence_of_viewpoint_without_offset(vertical_events, 'harmfuncKS'))
        print(utils.show_sequence_of_viewpoint_without_offset(vertical_events, 'harmfuncMS'))
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

    # Fechar descritores + harmonic functions
    # VMO
    # ver o passível de implementar as redes bayesianas
    # segmentação de Pearce