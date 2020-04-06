#!/usr/bin/env python3.7
"""
This script is the main script of the generation system
"""

import os

import numpy as np
from music21 import converter
from vmo import VMO, plot

import generation.plot_fo as gen_plot
import generation.utils as gen_utils
import representation.utils as rep_utils
from representation.line_parser import LineParser
from representation.segmenter import segmenter
from representation.vertical_parser import VerticalParser


def main():
    """
    Main function for extracting the viewpoints for examples
    """
    name = 'bwv1.6.2.mxl'  # 'MicrotonsExample.mxl' #'VoiceExample.mxl'
    file_path = os.sep.join(['data', 'myexamples', name])
    if os.path.realpath('.').find('code') != -1:
        file_path.replace('code', '')
        file_path = os.sep.join(['..', file_path])

    bach = converter.parse(file_path)
    # bach.flat.show('text')

    # segmenter(bach.parts[0])

    part_events = {}

    for i, part in enumerate(bach.parts):
        if part.isSequence():
            print('Processing part {}'.format(str(i)))
            part_events[i] = LineParser(part).parse_line()
            print('End of Processing part {}'.format(str(i)))
        else:
            pass  # Process part with more than one voice

    #print(rep_utils.show_sequence_of_viewpoint_without_offset(part_events[0], 'intfib'))
    #[print(str(ev)) for ev in part_events[0]]

    """     
    if (len(bach.parts) > 1 or bach.parts[0].hasVoices() or len(bach.parts[0].getOverlaps()) > 0):
        print('Processing Vertical Events')
        vertical_events = VerticalParser(bach).parse_music()
        print('End of Processing {} Vertical Events'.format(len(vertical_events)))
        #[print(str(ev)) for ev in vertical_events]
        #print(utils.show_sequence_of_viewpoint_without_offset(vertical_events, '')) 
    """

    weights = {
        'midi_pitch': 0.5,
        'pitch_class': 0.5,
        'contour': 0.5,
        'intfib': 0.5,
        'thrbar': 0.5,
        'posinbar': 0.5,
        'beatstrength': 0.5,
        'duration_length': 0.5,
        'duration_type': 0.5
    }

    event_features, features_names, weighted_fit = rep_utils.create_feature_array_events(
        events=part_events[0], weights=weights)

    thresh = gen_utils.find_threshold(
        event_features[:15], weights=weighted_fit, dim=len(features_names), entropy=True)

    oracle = gen_utils.build_oracle(
        event_features[:15], flag='a', features=features_names, weights=weighted_fit, dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])
    gen_plot.start_draw(oracle).show()

    oracle2 = VMO.oracle.build_oracle(
        event_features[:15], flag='a', dim=len(features_names), dfunc='cosine', threshold=thresh[0][1])
    plot.start_draw(oracle2).show()


if __name__ == "__main__":
    main()

    # Fechar descritores + harmonic functions
    # VMO
    # ver o passível de implementar as redes bayesianas
    # segmentação de Pearce
