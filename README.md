# xdd-docstructure

Code to analyze and filter xDD documents. Instructions here are for Linux/OSX.

Use Python 3.8 or higher, no non-standard modules are needed.


## Data setup

The code here assumes an input data directory with the following top-level structure:

```
some_directory
├── metadata.json
├── scienceparse
└── text
```

The `scienceparse` directory contains the results of running science parse over a set of PDFs and the `text` directory has the results of a simple text extract from the PDF files. The contains metadata for all files, it is only relevant for later processing and is not used for document structure parsing.


## Usage

First change the working directory to the code directory, then run the document structure parser on a directory:

```bash
$ python parse.py -i DATA_DIRECTORY -o OUTPUT --limit N
```

The parse.py script reads files from `text` and `scienceparse` and writes output to `${DATA_DIRECTORY}/output/doc`. The relative path within the data directory can be changed with the -o option. The --limit option sets a limit to the number of documents processed.

<!--

TODO: make a mini directory with three files with shrink.py and print tree representations of input and output.

-->

<!--

In development mode you can run the parser on small random subsets of the domains and view an HTML version of the output. For this you first create a list in the `lists` directory:

```bash
$ python select.py --data DIR select.py DOMAIN N
```

N is the number of documents to select and --data is used to overrule the default data directory. Output is written to `lists/DOMAIN-TIMSTAMP-N.txt`. Once you have this list you can run the code in developmemnt mode on a file list:

```bash
$ python parse.py --list ../lists/FILE_LIST
```

Results are written to `../out/data`, which has the same output as produced when running the document parser on a domain,  and `../out/html`, which contains an `index.html` file as a top-level page.
-->