#!/usr/bin/env python3.7
"""
This script is the main script of the generation system
"""

import os

from music21 import converter

import generation.utils as gen_utils
import generation.plot_fo as gen_plot
import representation.utils as rep_utils
from representation.line_parser import LineParser
from representation.vertical_parser import VerticalParser

import numpy as np
from vmo import VMO, plot

def main():
    """
    Main function for extracting the viewpoints for examples
    """
    name = 'bwv1.6.2.mxl'  # 'MicrotonsExample.mxl'
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
            print('End of Processing part {}'.format(str(i)))
        else:
            pass  # Process part with more

    #print(utils.show_sequence_of_viewpoint_without_offset(part_events[4], 'intfib'))

    """     
    if (len(bach.parts) > 1 or bach.parts[0].hasVoices() or len(bach.parts[0].getOverlaps()) > 0):
        print('Processing Vertical Events')
        vertical_events = VerticalParser(bach).parse_music()
        print('End of Processing {} Vertical Events'.format(len(vertical_events)))
        #[print(str(ev)) for ev in vertical_events]
        #print(utils.show_sequence_of_viewpoint_without_offset(vertical_events, '')) 
    """

    weights = {
        'midi_pitch': 1,
        'pitch_class': 0.15,
        'contour': 0.4,
        'intfib': 0.2,
        'thrbar': 0.1,
        'posinbar': 0.5,
        'beatstrength': 0.5,
        'duration_length': 0.6,
        'duration_type': 0.4
    }

    event_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        part_events[0], weights)

    euc_handle = lambda u, v, w: np.sqrt(((w*(u-v))**2).sum())

    oracle = gen_utils.build_oracle(
        event_features[:5], flag='a', features=features_names, weights=weighted_fit, dim=len(features_names), dfunc='other', dfunc_handle=euc_handle, threshold=2)
    gen_plot.start_draw(oracle).show()

    oracle2 = VMO.oracle.build_oracle(
        event_features[:5], flag='a', feature=features_names, weights=weighted_fit, dim=len(features_names), threshold=2)
    plot.start_draw(oracle2).show()

if __name__ == "__main__":
    main()

    # Fechar descritores + harmonic functions
    # VMO
    # ver o passível de implementar as redes bayesianas
    # segmentação de Pearce
