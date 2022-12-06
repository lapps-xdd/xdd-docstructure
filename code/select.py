"""Document selection from XDD data drop

This selects a number of random documents from the sample of 103K XDD documents
or one of the 10-14K topic domains.

$ python3 select.py DOMAIN N

DOMAIN is one of '103k', 'bio', 'geo' or 'mol'
N is an integer

The locations of the data drops are defined in the config module, in particular
in the BASE_DIR variable.

The selection is made from the text documents and the .txt extension if there
is one is stripped off.

The raw text and science parse directories and the document names are written
to a file in the "lists" directory. The file is named DOMAIN-TIMESTAMP-N.txt and
its contents will look like:

# TEXT /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/biomedical/text
# SCPA /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/biomedical/scienceparse
63447e8e74bed2df5c47cb08
5be55aeccf58f163e6a2d563
622af1352688b71135605c55
5890ad88cf58f128aa944fe9
5ae7f472cf58f101a67b77a8

"""

import os, sys, random, datetime
import config

CORPORA = { '103k': (config.TEXT_103K, config.SCPA_103K),
            'bio': (config.TEXT_BIO, config.SCPA_BIO),
            'geo': (config.TEXT_GEO, config.SCPA_GEO),
            'mol': (config.TEXT_MOL, config.SCPA_MOL) }


def outfile_name(domain: str, number_of_documents: int):
    dt = datetime.datetime.now()
    timestamp = "%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day,
                                               dt.hour, dt.minute, dt.second)
    return "../lists/%s-%s-%04d.txt" % (domain, timestamp, number_of_documents)


def select_documents(number_of_documents: int, domain: str):
    fnames = os.listdir(CORPORA[domain][0])
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

    selected_domain = sys.argv[1]
    n = int(sys.argv[2])

    docs = select_documents(n, selected_domain)
    outfile = outfile_name(selected_domain, n)
    with open(outfile, 'w') as fh:
        fh.write(f'# TEXT {CORPORA[selected_domain][0]}\n')
        fh.write(f'# SCPA {CORPORA[selected_domain][1]}\n')
        for doc in docs:
            print(doc)
            fh.write("%s\n" % doc)
