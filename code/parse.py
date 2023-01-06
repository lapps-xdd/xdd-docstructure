"""Minimal document structure parsing

Mostly aimed at extracting abstracts and other elements from unstructured xDD
text, but also at characterizing the entire document and individual paragraphs.

Takes output from ScienceParse and heuristics on the raw text and weighs its
options.

Usage in production mode:
$ python3 parse --domain DOMAIN --limit N --data DIR

Process a maximum on N documents from the domain and write output to a subdirectory
of DIR, if --data is not used then the default from the config file will be used.

Usage in demo mode:
$ python3 parse --list ../lists/FILENAME
$ python3 parse --lists ../lists

FILENAME is a file created by the select.py script, it contains the locations
of the raw text and ScienceParse directories and a list of filenames. In the
second invocation all files in the lists directory are used. Output is written
to directories in ../out, with the directory name taken from the file list.

See the README.md file for more details.

The following are calculated:

- A language score for the entire document and all paragraphs, this is a
  measure between 0 and 1 that encodes what percentage of a sequence of
  tokens is in a dictionary of frequent English words.
- A ratio of occurrences of the string 'medRxiv' over the number of paragraphs
  of a document. A larger number tends to indicate a list of abstracts.
- The average token length of a paragraph. Lower than 4 usually indicates
  that the text is some kind of listing.
- The average line length of a paragraph. Lower than 10 usually indicate that
  the paragraph is not running text.
- Singletons per token. If this is larger than 0.1 than the text is usually made
  up of a lot of single characters or numbers.
- Number of sections of ScienceParse output and the average length of those
  sections.
- Ratio of the number of headings in the output of ScienceParse to the total
  number of sections.

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
    domain_help = \
        ('Parse all files in the domain where domain is one of 103k, bio, geo and mol. '
         'Does not generate html files and uses the specifications in the config module '
         'to determine where the output goes.')
    data_help = \
        ("Data location, the default is 'data' (in the code directory), which could be "
         "a symbolic link. This is only relevant when using the --domain option because "
         "list files include the data directories.")
    parser = argparse.ArgumentParser(
        description='Parse xDD files')
    parser.add_argument('--list', help="Use list of files")
    parser.add_argument('--lists', help="Use a directory with lists of files")
    parser.add_argument('--domain', help=domain_help)
    parser.add_argument('--limit', help="Maximum number of documents to process for a domain")
    parser.add_argument('--data', help=data_help)
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


def parse_files_in_lists(directory: str):
    """Parse all files in all file list in the directory and create html and json
    files for those files in the ../out/html/<subdir> and ../out/data/<subdir>
    directories, where <subdir> is the name of the data set, something like
    bio-20221208-154439-0025."""
    file_lists = glob.glob(os.path.join(directory, '*.txt'))
    for file_list in file_lists:
        parse_files_in_list(file_list, index=False)
    Documents.write_html_index('../out/html')


def parse_files_in_domain(domain: str, limit=sys.maxsize):
    # In production mode we only write JSON output, and we write it to
    # the output directories specified in the config module
    file_list = generate_file_list_from_domain(domain)
    docs = Documents(file_list, '', config.proc_directories_idx()[domain])
    docs.write_output(limit=limit)


def generate_file_list_from_domain(domain: str):
    """Generate a file list for the domain and return the location of the list."""
    file_list = f"filelist-{domain}.txt"
    with open(file_list, 'w') as fh:
        fh.write(f'# TEXT\t{config.location(domain, "text")}\n')
        fh.write(f'# SCPA\t{config.location(domain, "scpa")}\n')
        fh.write(f'# PROC\t{config.location(domain, "proc")}\n')
        fnames_text = os.listdir(config.location(domain, 'text'))
        for name in sorted(fnames_text):
            if name.endswith('.txt') and len(name) == 28:
                fh.write(f'{name[:-4]}\n')
        print(f'Generated {file_list} with {len(fnames_text):,} entries')
    return file_list


if __name__ == '__main__':

    args = parse_args()
    if args.data:
        config.DATA_DIR = args.data
    if args.list:
        parse_files_in_list(args.list)
    elif args.lists:
        parse_files_in_lists(args.lists)
    elif args.domain:
        limit = int(args.limit) if args.limit else sys.maxsize
        parse_files_in_domain(args.domain, limit=limit)
