#!/usr/bin/env python3.7
"""
This script defines ploting routines for ploting oracles,
based on the code in https://github.com/wangsix/vmo/b_lob/master/vmo/plot.py
"""

import numpy as np
# import music21 #@UnusedImport
# import pretty_midi #@UnusedImport


try:
    # , ImageFilter  # @UnresolvedImport @UnusedImport
    from PIL import Image, ImageDraw
except Exception:
    print('pil not loaded - hopefully running in max')


WIDTH = 900 * 4
HEIGHT = 400 * 4
LRS_THRESH = 0


def start_draw(_oracle, size=(900*4, 400*4)):
    """

    :param _oracle: input vmo object
    :param size: the size of the output image
    :return: an update call the draw()
    """

    width = size[0]
    height = size[1]
    current_state = 0
    image = Image.new('RGB', (width, height))
    oracle = _oracle
    return draw(oracle, current_state, image, width, height)


def draw(oracle, current_state, image, width=WIDTH, height=HEIGHT):
    """

    :param oracle: input vmo object
    :param current_state:
    :param image: an PIL image object
    :param width: width of the image
    :param height: height of the image
    :return: the updated PIL image object
    """

    trn = oracle.basic_attributes['trn']
    sfx = oracle.basic_attributes['sfx']
    lrs = oracle.basic_attributes['lrs']

    # handle to Draw object - PIL
    n_states = len(sfx)
    drawer = ImageDraw.Draw(image)

    for i in range(n_states):
        # draw circle for each state
        x_pos = (float(i) / n_states * width) + 0.5 * 1.0 / n_states * width
        # iterate over forward transitions
        for tran in trn[i]:
            # if forward transition to next state
            if tran == i + 1:
                # draw forward transitions
                next_x = (float(i + 1) / n_states * width) + \
                    0.5 * 1.0 / n_states * width
                current_x = x_pos + (0.25 / n_states * width)
                drawer.line((current_x, height/2, next_x, height/2),
                            width=1, fill='white')
            else:
                if lrs[tran] >= LRS_THRESH:
                    # forward transition to another state
                    current_x = x_pos
                    next_x = (float(tran) / n_states * width) + \
                        (0.5 / n_states * width)
                    arc_height = (height / 2) + (tran - i) * 0.125
                    drawer.arc((int(current_x), int(height/2 - arc_height/2),
                                int(next_x), int(height/2 + arc_height / 2)), 180, 0,
                               fill='White')
        if sfx[i] is not None and sfx[i] != 0 and lrs[sfx[i]] >= LRS_THRESH:
            current_x = x_pos
            next_x = (float(sfx[i]) / n_states * width) + \
                (0.5 / n_states * width)
            # draw arc
            arc_height = (height / 2) - (sfx[i] - i) * 0.125
            drawer.arc((int(next_x),
                        int(height/2 - arc_height/2),
                        int(current_x),
                        int(height/2 + arc_height/2)),
                       0,
                       180,
                       fill='White')

    image.resize((900, 400), (Image.BILINEAR))
    return image


def draw_compror():
    """Compror drawing: under construction"""
    raise NotImplementedError(
        "Compror drawing is under construction, coming soon!")


def get_pattern_mat(oracle, pattern):
    """Output a matrix containing patterns in rows from a vmo.

    :param oracle: input vmo object
    :param pattern: pattern extracted from oracle
    :return: a numpy matrix that could be used to visualize the pattern extracted.
    """

    pattern_mat = np.zeros((len(pattern), oracle.statistics['n_states']-1))
    for i, pat in enumerate(pattern):
        length = pat[1]
        for _s in pat[0]:
            pattern_mat[i][_s-length:_s-1] = 1

    return pattern_mat
