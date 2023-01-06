"""Document selection from XDD data drop

This selects a number of random documents from the sample of 103K XDD documents
or one of the 10-14K topic domains.

$ python3 --data DIR select.py DOMAIN N

    DOMAIN is one of '103k', 'bio', 'geo' or 'mol'
    N is an integer

The locations of the data drops are defined in the config module, in particular
in the BASE_DIR variable, use the --data option to overrule the config settings.

The selection is made from the text documents and the .txt extension if there
is one is stripped off.

The raw text and science parse directories and the document names are written
to a file in the "lists" directory. The file is named DOMAIN-TIMESTAMP-N.txt and
its contents will look like:

# TEXT /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/biomedical/text
# SCPA /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/biomedical/scienceparse
# PROC /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/biomedical/processed
63447e8e74bed2df5c47cb08
5be55aeccf58f163e6a2d563
622af1352688b71135605c55
5890ad88cf58f128aa944fe9
5ae7f472cf58f101a67b77a8

"""

import os, random, argparse
import config
import utils


def parse_args():
    parser = argparse.ArgumentParser(
        description='Select xDD files')
    parser.add_argument('domain', help="domain to select from")
    parser.add_argument('count', help="number of documents to select")
    parser.add_argument('--data', help="data directory, default is 'data'")
    return parser.parse_args()


def outfile_name(domain: str, number_of_documents: int):
    timestamp = utils.timestamp()
    return "../lists/%s-%s-%04d.txt" % (domain, timestamp, number_of_documents)


def select_documents(number_of_documents: int, domain: str):
    fnames = os.listdir(config.location(domain, "text"))
    selected_indices = set()
    selected_documents = set()
    while len(selected_indices) < number_of_documents:
        random_int = random.randint(0, len(fnames))
        selected_indices.add(random_int)
        selected_document = os.path.splitext(fnames[random_int])[0]
        selected_documents.add(selected_document)
    print("Selecting %d documents from domain '%s'" % (number_of_documents, domain))
    return selected_documents


if __name__ == '__main__':

    args = parse_args()
    print(config.DATA_DIR)
    print(args)
    if args.data:
        config.DATA_DIR = args.data
    docs = select_documents(int(args.count), args.domain)
    outfile = outfile_name(args.domain, int(args.count))
    with open(outfile, 'w') as fh:
        fh.write(f'# TEXT\t{os.path.abspath(config.location(args.domain, "text"))}\n')
        fh.write(f'# SCPA\t{os.path.abspath(config.location(args.domain, "scpa"))}\n')
        fh.write(f'# PROC\t{os.path.abspath(config.location(args.domain, "proc"))}\n')
        for doc in docs:
            print(doc)
            fh.write("%s\n" % doc)
