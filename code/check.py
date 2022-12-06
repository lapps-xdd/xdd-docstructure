"""Data set checks

Compares the raw text and ScienceParse json files from the following data sets:

- The 104K data drop from September 2022
- The three 10-14K data drops for three domains from December 2022

"""

# TODO: add check of length of filename

import os
import config
from utils import trim_filename


def check_directories(text_dir: str, scpa_dir: str):
    print()
    print(text_dir)
    print(scpa_dir)
    print()
    text_files = list(sorted([trim_filename(fname) for fname in os.listdir(text_dir)]))
    scpa_files = list(sorted([trim_filename(fname) for fname in os.listdir(scpa_dir)]))
    text_files_set = set(text_files)
    scpa_files_set = set(scpa_files)
    text_files_extras = list(sorted(text_files_set.difference(scpa_files_set)))
    scpa_files_extras = list(sorted(scpa_files_set.difference(text_files_set)))
    print('  TEXT count', len(text_files), text_files[:4])
    print('  SCPA count', len(scpa_files), scpa_files[:4])
    print('  Extra in TEXT', len(text_files_extras), text_files_extras[:4])
    print('  Extra in SCPA', len(scpa_files_extras), scpa_files_extras[:4])


if __name__ == '__main__':

    for text_directory, scpa_directory in zip(config.TEXT_DIRS, config.SCPA_DIRS):
        check_directories(text_directory, scpa_directory)
