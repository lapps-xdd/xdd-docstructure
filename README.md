# xdd-docstructure

Code to analyze and filter xDD documents. Instructions here are for Linux/OSX.

Requirements are Python 3.8 or higher (Python 3.7 will probably work).

## Data setup

The code here assume three data drops from the University of Wisconsin:

- xdd-covid-19-8Dec-doc2vec_text.zip
- xdd-covid-19-8Dec-scienceparse.zip
- topic_doc2vecs.zip

The first two have the raw text and ScienceParse results for a 103K COVID-related documents, the third contains raw text and ScienceParse results for three domains (10K each for biomedical, geoarchive and molecular_physics). Put these in a separate directory:

```bash
$ mkdir data
$ cp *.zip data
```

Now unpack the three zips, they are structured differently so their are minor differences in how you do that. What you want to end up with to use this document structure code is the following directory structure:

```
.
├── topic_doc2vecs
│   ├── biomedical
│   │   ├── scienceparse
│   │   └── text
│   ├── geoarchive
│   │   ├── scienceparse
│   │   └── text
│   └── molecular_physics
│       ├── scienceparse
│       └── text
├── xdd-covid-19-8Dec-doc2vec_text
└── xdd-covid-19-8Dec-scienceparse
    └── scienceparse
```

This can be done with the following sequence of commands:

```bash
$ cd data
$ unzip topic_doc2vecs.zip
$ mkdir xdd-covid-19-8Dec-doc2vec_text
$ cp xdd-covid-19-8Dec-doc2vec_text.zip xdd-covid-19-8Dec-doc2vec_text
$ cd xdd-covid-19-8Dec-doc2vec_text
$ unzip xdd-covid-19-8Dec-doc2vec_text.zip
$ cd ..
$ mkdir xdd-covid-19-8Dec-scienceparse
$ cp xdd-covid-19-8Dec-scienceparse.zip xdd-covid-19-8Dec-scienceparse
$ cd xdd-covid-19-8Dec-scienceparse
$ unzip xdd-covid-19-8Dec-scienceparse.zip
```

## Usage

First change the working directory to the code directory.

To run the parser on a domain:

```bash
$ python parse.py --domain DOMAIN --limit N --data DIR
```

Here, DOMAIN is one of '103k', 'bio', 'geo' and 'mol'. The --limit option sets a limit to the number of documents processed and --data allows you to overrule the default in the `config.py` file. Where the output is printed depends on the domain:

| domain | output directory                                       |
| ------ | ------------------------------------------------------ |
| 103k   | DATA_DIR/xdd-covid-19-8Dec-processed/                  |
| bio    | DATA_DIR/topic\_doc2vecs/biomedical/processed/         |
| geo    | DATA_DIR/topic\_doc2vecs/geoarchive/processed/         |
| mol    | DATA_DIR/topic\_doc2vecs/molecular\_physics/processed/ |

In development mode you can run the parser on small random subsets of the domains and view an HTML version of the output. For this you first create a list in the `lists` directory:

```bash
$ python select.py --data DIR select.py DOMAIN N
```

N is the number of documents to select and --data is used to overrule the default data directory. Output is written to `lists/DOMAIN-TIMSTAMP-N.txt`. Once you have this list you can run the code in developmemnt mode on a file list:

```bash
$ python parse.py --list ../lists/FILE_LIST
```

Results are written to `../out/data`, which has the same output as produced when running the document parser on a domain,  and `../out/html`, which contains an `index.html` file as a top-level page.
