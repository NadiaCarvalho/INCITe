"""
Text Wrapper
"""
import os


def wrap_text(text, max_char):
    """
    Wrap Text by x chars if text has separators
    """
    text_to_split = ''.join([str.strip() for str in text.splitlines(True)])
    path = text_to_split.split(os.sep)
    if len(path) == 1:
        path = text_to_split.split('/')
    text_to_wrap = []
    for p in path:
        if len(text_to_wrap) > 0 and (len(text_to_wrap[-1] + (p + os.sep)) < max_char):
            text_to_wrap[-1] += (p + os.sep)
        else:
            text_to_wrap.append((p + os.sep))
    text_to_wrap[-1] = text_to_wrap[-1][:-1]
    return '\n'.join(text_to_wrap)
