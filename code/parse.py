"""Minimal document structure parsing

Mostly aimed at extracting abstracts and other elements from unstructured xDD text,
but also at characterizing the entire document and individual paragraphs.

Takes output from ScienceParse and heuristics on the raw text and weighs its options.

Usage in production mode:
$ python3 parse.py -i DATA_DIRECTORY -o OUTPUT_DIRECTORY --limit N

Process a maximum on N documents from DATA_DIRECTORY. Write output to a subdirectory
of DATA_DIRECTORY, by default this is "output/doc", but this can be overwritten with
the -o option, where OUTPUT_DIRECTORY is a relative path within DATA_DIRECTORY.

Usage in demo mode:
$ python3 parse.py --list ../lists/FILENAME

FILENAME is a file created by the select.py script, it contains the locations of the
raw text and ScienceParse directories and a list of filenames. In the second invocation
all files in the lists directory are used. Output is written to directories in ../out,
with the directory name taken from the file list.

See the README.md file for more details.

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

import os, sys, glob, argparse

import config
from document import Documents


def parse_args():
    parser = argparse.ArgumentParser(description='Parse xDD files')
    parser.add_argument('-i', help="source directory")
    parser.add_argument('-o', help="output directory within source directory", default='output/doc')
    parser.add_argument('--list', help="Use list of files")
    parser.add_argument('--limit', help="Maximum number of documents to process for a domain")
    return parser.parse_args()


def parse_files_in_list(file_list: str, index=True):
    """Parse all files in the file list and create html and json files for those
    files in the ../out/html/<subdir> and ../out/data/<subdir> directories, where
    <subdir> is the name of the data set, something like bio-20221208-154439-0025."""
    subdir = os.path.splitext(os.path.basename(file_list))[0]
    html_dir = os.path.join('../out/html', subdir)
    data_dir = os.path.join('../out/data', subdir)
    docs = Documents(file_list, html_dir, data_dir)
    docs.write_output()
    docs.write_html()
    if index:
        Documents.write_html_index('../out/html')


def parse_files_in_directory(indir: str, outdir='output/doc', limit=sys.maxsize):
    # In production mode we only write JSON output, and by default we write it to
    # the output/doc directory within the input directory.
    file_list = generate_filelist(indir)
    print(f'>>> Writing results to {indir}/{outdir}')
    docs = Documents(file_list, '', os.path.join(indir, outdir))
    docs.write_output(limit=limit)


def generate_filelist(directory: str):
    """Generate a file list for the directory and return the location of the list."""
    file_list = f"filelist-{os.path.basename(directory)}.txt"
    with open(file_list, 'w') as fh:
        fh.write(f'# TEXT\t{directory}/text\n')
        fh.write(f'# SCPA\t{directory}/scpa\n')
        fh.write(f'# PROC\t{directory}/output/doc\n')
        fnames_text = os.listdir(os.path.join(directory, 'text'))
        for name in sorted(fnames_text):
            if name.endswith('.txt') and len(name) == 28:
                fh.write(f'{name[:-4]}\n')
        print(f'>>> Generated {file_list} with {len(fnames_text):,} entries')
    return file_list



if __name__ == '__main__':

    args = parse_args()
    if args.i:
        limit = int(args.limit) if args.limit else sys.maxsize
        parse_files_in_directory(args.i, args.o, limit=limit)
    elif args.list:
        parse_files_in_list(args.list)
