"""Document selection from XDD data drop

$ python3 select.py DIRECTORY NAME COUNT

This selects COUNT random documents from DIRECTORY and writes output to /lists.

This assumes that DIRECTORY has subdirectories named text and scienceparse. The
selection is made from the text documents and the .txt extension if there is one
is stripped off.

The raw text and science parse directories and the document names are written
to a file in the "lists" directory. The file is named NAME-TIMESTAMP-N.txt and
its contents will look like:

# TEXT /Users/Shared/data/xdd/topics/random/text/text
# SCPA /Users/Shared/data/xdd/topics/random/text/scienceparse
5c02a2371faed6554886c814
5b288e19cf58f13242cb8987
5a2ab736cf58f1811f9a4e09
642c0f0714b4ac75a269b131
5adc4145cf58f164ffe84c6c

"""

import os, random, argparse
from utils import timestamp


def parse_args():
    parser = argparse.ArgumentParser(
        description='Select xDD files')
    parser.add_argument('data', help="data directory")
    parser.add_argument('name', help="basename for the output file")
    parser.add_argument('count', help="number of documents to select")
    return parser.parse_args()


def outfile_name(name: str, number_of_documents: int):
    return "../lists/%s-%s-%04d.txt" % (name, timestamp(), number_of_documents)


def select_documents(number_of_documents: int, data_directory: str):
    fnames = os.listdir(os.path.join(data_directory, "text"))
    selected_indices = set()
    selected_documents = set()
    while len(selected_indices) < number_of_documents:
        random_int = random.randint(0, len(fnames))
        selected_indices.add(random_int)
        selected_document = os.path.splitext(fnames[random_int])[0]
        selected_documents.add(selected_document)
    print("Selecting %d documents from '%s'" % (number_of_documents, data_directory))
    return selected_documents


if __name__ == '__main__':

    args = parse_args()
    print(args)
    docs = select_documents(int(args.count), args.data)
    outfile = outfile_name(args.name, int(args.count))
    with open(outfile, 'w') as fh:
        fh.write(f'# TEXT\t{os.path.abspath(os.path.join(args.data, "text"))}\n')
        fh.write(f'# SCPA\t{os.path.abspath(os.path.join(args.data, "scienceparse"))}\n')
        for doc in docs:
            print(doc)
            fh.write("%s\n" % doc)
