"""Minimal document structure parsing

Mostly aimed at extracting abstracts and other elements from unstructured xDD text,
but also at characterizing the entire document and individual paragraphs.

Takes output from ScienceParse and heuristics on the raw text.

Usage in production mode:

$ python3 parse.py --scpa DIR1 --text DIR2 --out DIR3 --limit N

Process a maximum on N documents from the ScienceParse (DIR1) and text (DIR2) directories
and write output to DIR3.

Usage in demo mode:

$ python3 parse.py --list ../lists/FILENAME

FILENAME is a file created by the select.py script, it contains the locations of the
raw text and ScienceParse directories and a list of filenames. All locations in the
list are used asinput. Output is written to directories in ../out, with the directory
name taken from the file list.

The following are calculated:

- A language score for the entire document and all paragraphs, this is a measure between
  0 and 1 that encodes what percentage of a sequence of tokens is in a dictionary of 
  frequent English words.
- A ratio of occurrences of the string 'medRxiv' over the number of paragraphs of a
  document. A larger number tends to indicate a list of abstracts.
- The average token length of a paragraph. Lower than 4 usually indicates that the text
  is some kind of listing.
- The average line length of a paragraph. Lower than 10 usually indicate that the
  paragraph is not running text.
- Singletons per token. If this is larger than 0.1 than the text is usually made up of a
  lot of single characters or numbers.
- Number of sections of ScienceParse output and the average length of those sections.
- Ratio of the number of headings in the output of ScienceParse to the total number of
  sections.

Does not do stand-off annotation of the text.

"""

# TODO: for the singletons, it often happens with ScienceParse that highlighted
#       text has spaces added (for example: "i n t r o d u c t i o n"), may want
#       to find a way to undo this
# TODO: the medRxiv score now counts the same medXriv reference multiple times

import os, sys, argparse
from utils import basename
from document import Documents


# Name for temporary file with all files to process, with their locations
FILE_LIST = "tmp-filelist.txt"


def parse_args():
    parser = argparse.ArgumentParser(description='Parse xDD document structure')
    parser.add_argument('--scpa', help="scienceparse directory")
    parser.add_argument('--text', help="text directory")
    parser.add_argument('--out', help="output directory")
    parser.add_argument('--list', help="Use list of files")
    parser.add_argument('--limit', help="Maximum number of documents to process",
                        type=int, default=sys.maxsize)
    return parser.parse_args()


def parse_files_in_list(file_list: str):
    """Parse all files in the file list and create html and json files for those
    files in the ../out/html/<subdir> and ../out/data/<subdir> directories, where
    <subdir> is the name of the data set, something like bio-20221208-154439-0025."""
    subdir = basename(file_list)
    if subdir == basename(FILE_LIST):
        subdir = 'tmp'
    html_dir = os.path.join('../out/html', subdir)
    data_dir = os.path.join('../out/data', subdir)
    docs = Documents(file_list, html_dir, data_dir)
    docs.write_output()
    docs.write_html()
    Documents.write_html_index('../out/html')


def parse_files_in_directory(scpa_dir: str, text_dir: str, out_dir: str, limit=sys.maxsize):
    _generate_filelist(FILE_LIST, scpa_dir, text_dir, limit)
    print(f'>>> Writing results to {out_dir}')
    # In production mode we only write JSON output, so the html_dir is set to None
    docs = Documents(FILE_LIST, None, out_dir)
    docs.write_output()


def _generate_filelist(file_list: str, scpa_dir: str, text_dir: str, limit=sys.maxsize):
    """Generate a list with input files and their location and save it in FILE_LIST."""
    with open(file_list, 'w') as fh:
        fh.write(f'# TEXT\t{text_dir}\n')
        fh.write(f'# SCPA\t{scpa_dir}\n')
        fnames_text = [f for f in os.listdir(text_dir) if f.endswith('.txt')][:limit]
        for name in sorted(fnames_text):
            if name.endswith('.txt') and len(name) == 28:
                fh.write(f'{name[:-4]}\n')
        print(f'>>> Generated {FILE_LIST} with {len(fnames_text):,} entries')



if __name__ == '__main__':

    args = parse_args()
    if args.list:
        parse_files_in_list(args.list)
    else:
        parse_files_in_directory(args.scpa, args.text, args.out, args.limit)
