"""Document selection from XDD data drop

This select N random documents from the sample of 103K XDD documents. All
these documents are unstructured text.

$ python3 select.py N

The document names are written to a file in the lists directory.

The selection is made from the text documents.

"""

import os, sys, random, datetime

SOURCE = '/Users/Shared/data/xdd/doc2vec/xdd-covid-19-8Dec-doc2vec_text'


def outfile_name(number_of_documents):
    dt = datetime.datetime.now()
    timestamp = "%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day,
                                               dt.hour, dt.minute, dt.second)
    return "../lists/documents-%s-%04d.txt" % (timestamp, number_of_documents)


def select_documents(number_of_documents):
    selected_indices = set()
    selected_documents = set()
    while len(selected_indices) < number_of_documents:
        random_int = random.randint(start, end)
        selected_indices.add(random_int)
        selected_documents.add(fnames[random_int])
    selected_documents = sorted([d for d in selected_documents if d.startswith('5')])
    print("Selected %d random integers" % number_of_documents)
    print("Selected %d random documents" % len(selected_documents))
    return selected_documents


if __name__ == '__main__':

    fnames = os.listdir(SOURCE)
    start = 0
    end = len(fnames)
    n = int(sys.argv[1])

    docs = select_documents(n)
    outfile = outfile_name(n)
    with open(outfile, 'w') as fh:
        for doc in docs:
            print(doc)
            fh.write("%s\n" % doc)
