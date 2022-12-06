"""Minimal document structure parsing

Mostly aimed at extracting abstracts from unstructured xDD text, but also at
characterizing the entire document and individual paragraphs.

Usage:
$ python3 parse ../lists/FILENAME
$ python3 parse ../lists

FILENAME is a file created by the select.py script, it contains the locations
of the raw text and ScienceParse directories and a list of filenames. In the
second invocation all files in the lists directory are used. Output is written
to directories in ../out, with the directory name taken from the file list.

The following are calculated:

- A language score for the entire document and all paragraphs, this is a
  measure between 0 and 1 that encodes what percentage of a sequence of
  tokens is in a dictionary of frequent English words.
- A ratio of occurrences of the string 'medRxiv' over the number of paragraphs
  of a document. A larger number tends to indicate a list of abstracts.
- The average token length of a paragraph. Lower than 5 usually indicates
  that the text is some kind of listing.

Does not do stand-off annotation of the text.

"""

import os, sys, glob
from document import Documents


if __name__ == '__main__':

    file_spec = sys.argv[1]
    if os.path.isdir(file_spec):
        file_lists = glob.glob(os.path.join(file_spec, '*.txt'))
    else:
        file_lists = [file_spec]

    for file_list in file_lists:
        html_dir = os.path.join('../out', os.path.splitext(os.path.basename(file_list))[0])
        docs = Documents(file_list, html_dir, exp='')
        docs.write_html()
