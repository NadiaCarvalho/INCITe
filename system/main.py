import os
import pathlib

import matplotlib as plot
import numpy as np
import scipy as sp

import music21
from music21 import *
from music21 import corpus



'''
core_corpus = corpus.corpora.CoreCorpus() 
core_corpus.manualCoreCorpusPath = os.sep.join([os.sep.join(['database','music21']),''])
core_corpus.rebuildMetadataCache(useMultiprocessing=True, verbose=True)
print(core_corpus.metadataBundle)
'''

'''
if os.name == 'nt':
    posix_paths = []
    for path in core_corpus.getPaths():
        posix_paths.append(path.as_posix())
    #corpus_paths = posix_paths

#print(corpus_paths[0])
'''
