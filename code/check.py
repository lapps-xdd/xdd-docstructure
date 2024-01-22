"""Data set checks

Usage:

$ python check DATA_DIRECTORY

Compares the raw text and ScienceParse json files from the given directory. Assumes
that there are directories DATA_DIRECTORY/text and DATA_DIRECTORY/scienceparse

Also checks whether all file names have the standard length.

"""

import os, sys
from utils import trim_filename

STANDARD_FILENAME_LENGTH = 24


def check_directories(text_dir: str, scpa_dir: str):
    print()
    print(text_dir)
    print(scpa_dir)
    print()
    text_files = list(sorted([trim_filename(fname, '.txt') for fname in os.listdir(text_dir)]))
    scpa_files = list(sorted([trim_filename(fname, '_input.pdf.json') for fname in os.listdir(scpa_dir)]))
    text_files_set = set(text_files)
    scpa_files_set = set(scpa_files)
    text_files_extras = list(sorted(text_files_set.difference(scpa_files_set)))
    scpa_files_extras = list(sorted(scpa_files_set.difference(text_files_set)))
    print('  TEXT count', len(text_files), text_files[:4])
    print('  SCPA count', len(scpa_files), scpa_files[:4])
    print('  Extra in TEXT', len(text_files_extras), text_files_extras[:4])
    print('  Extra in SCPA', len(scpa_files_extras), scpa_files_extras[:4])
    for text_file in text_files:
        if len(text_file) != STANDARD_FILENAME_LENGTH:
            print(f'  Unexpected file name: {text_file}')


if __name__ == '__main__':

    data_directory = sys.argv[1]
    text_directory = os.path.join(data_directory, 'text')
    scpa_directory = os.path.join(data_directory, 'scienceparse')
    check_directories(text_directory, scpa_directory)
