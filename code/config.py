"""Configuration settings

"""

import os

BASE_DIR = '/Users/Shared/data/xdd/doc2vec'

TEXT_103K = os.path.join(BASE_DIR, 'xdd-covid-19-8Dec-doc2vec_text')
TEXT_BIO = os.path.join(BASE_DIR, 'topic_doc2vecs/biomedical/text')
TEXT_GEO = os.path.join(BASE_DIR, 'topic_doc2vecs/geoarchive/text')
TEXT_MOL = os.path.join(BASE_DIR, 'topic_doc2vecs/molecular_physics/text')

SCPA_103K = os.path.join(BASE_DIR, 'xdd-covid-19-8Dec-scienceparse/scienceparse')
SCPA_BIO = os.path.join(BASE_DIR, 'topic_doc2vecs/biomedical/scienceparse')
SCPA_GEO = os.path.join(BASE_DIR, 'topic_doc2vecs/geoarchive/scienceparse')
SCPA_MOL = os.path.join(BASE_DIR, 'topic_doc2vecs/molecular_physics/scienceparse')

TEXT_DIRS = [TEXT_103K, TEXT_BIO, TEXT_GEO, TEXT_MOL]
SCPA_DIRS = [SCPA_103K, SCPA_BIO, SCPA_GEO, SCPA_MOL]

TEXT_DIRS_IDX = { '103k': TEXT_103K, 'bio': TEXT_BIO, 'geo': TEXT_GEO, 'mol': TEXT_MOL, }
SCPA_DIRS_IDX = { '103k': SCPA_103K, 'bio': SCPA_BIO, 'geo': SCPA_GEO, 'mol': SCPA_MOL, }
