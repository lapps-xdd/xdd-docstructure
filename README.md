# xdd-docstructure

Code to analyze and filter xDD documents.

Use Python 3.8 or higher, no third-party modules are needed.

To run the document structure parser:

```bash
$ python3 parse.py --scpa DIR1 --text DIR2 --out DIR3 --limit N
```

The DIR1 input directory contains the results of running Science Parse over a set of PDFs and the DIR2 input directory has the results of a simple text extract from the PDF files. Outpus is written to DIR3. If --limit is used then a maximum on N documents will be processed.

With a typical real-life example of our data you would do something like


```
$ export DIR=/Users/Shared/data/xdd/topics/climate-change-modeling
$ python3 parse.py --scpa $DIR/scienceparse/ --text $DIR/text/ --out $DIR/output/doc
```


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