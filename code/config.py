"""Configuration settings

This is all about access to data locations.

"""

import os

DATA_DIR = 'data'
DOMAINS = ['103k', 'bio', 'geo', 'mol']
DATA_TYPES = ['text', 'scpa', 'proc']

DATA = {
    '103k': { 'text': 'xdd-covid-19-8Dec-doc2vec_text',
              'scpa': 'xdd-covid-19-8Dec-scienceparse/scienceparse',
              'proc': 'xdd-covid-19-8Dec-processed' },
    'bio': { 'text': 'topic_doc2vecs/biomedical/text',
             'scpa': 'topic_doc2vecs/biomedical/scienceparse',
             'proc': 'topic_doc2vecs/biomedical/processed' },
    'geo': { 'text': 'topic_doc2vecs/geoarchive/text',
             'scpa': 'topic_doc2vecs/geoarchive/scienceparse',
             'proc': 'topic_doc2vecs/geoarchive/processed' },
    'mol': { 'text': 'topic_doc2vecs/molecular_physics/text',
             'scpa': 'topic_doc2vecs/molecular_physics/scienceparse',
             'proc': 'topic_doc2vecs/molecular_physics/processed' }}


def location(domain, data_type):
    return os.path.join(DATA_DIR, DATA[domain][data_type])


def text_directories():
    return [location(domain, 'text') for domain in DOMAINS]


def scpa_directories():
    return [location(domain, 'scpa') for domain in DOMAINS]


def text_directories_idx():
    return { domain: location(domain, 'text') for domain in DOMAINS }


def scpa_directories_idx():
    return { domain: location(domain, 'scpa') for domain in DOMAINS }


def proc_directories_idx():
    return { domain: location(domain, 'proc') for domain in DOMAINS }
