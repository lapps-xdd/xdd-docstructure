"""Extracting abstracts from unstructured text

Makes a guess as to what the abstract is and return the text of the abstract.

Does not do stand-off annotation of the text.

TODO: recognize repetition of medRxiv as indicator of overview article or list
      (see 5f981c2f853f777558b34307 for an example, these are not rare)

"""

import os, sys, json
from collections import Counter
import frequencies

TEXT_DIR = '/Users/Shared/data/xdd/doc2vec/xdd-covid-19-8Dec-doc2vec_text'
SCPA_DIR = '/Users/Shared/data/xdd/doc2vec/xdd-covid-19-8Dec-scienceparse/scienceparse'

FREQUENT_ENGLISH_WORDS = set(
    [line.split()[1] for line in frequencies.FREQUENCIES.split('\n') if line])


class Document:

    def __init__(self, identifier: str, text_file: str, scpa_file: str):
        self.identifier = identifier
        self.text_file = text_file
        self.scpa_file = scpa_file
        with open(text_file) as fh:
            self.content = fh.read()
        self.jsondoc = JsonDocument(scpa_file)
        self.paras = [Paragraph(p, self) for p in self.content.split("\n\n")]
        self.tokens = Counter(self.content.split())
        self.abstract = None
        self.language = None
        self.set_language_score()
        self.link()
        self.parse()

    def __str__(self):
        abstract = ' heur_abstract' if self.abstract else ''
        abstract_text = ' scpa_abstract' if self.jsondoc.abstract else ''
        return "<%s %s lang=%.2f len=%06d%s%s>" % (self.class_name(), self.short_name(), self.language,
                                                   len(self), abstract, abstract_text)

    def __len__(self):
        return len(self.content)

    def set_language_score(self):
        """This score measures what percentage of tokens are in a list of the 500
        most frequent words in English. This score tends to be below 0.1 for papers
        in other languages or papers that are more like listings of results."""
        in_frequent_words = 0
        total_tokens = 0
        for token, count in self.tokens.items():
            total_tokens += count
            if token in FREQUENT_ENGLISH_WORDS:
                in_frequent_words += count
        self.language = in_frequent_words / total_tokens

    def link(self):
        """Turn the paragraph list in to a linked list."""
        for i in range(len(self.paras) - 1):
            self.paras[i].next = self.paras[i + 1]
            self.paras[i + 1].previous = self.paras[i]

    def parse(self):
        for para in self.paras:
            para.parse()

    def class_name(self):
        return self.__class__.__name__

    def short_name(self):
        return os.path.basename(self.text_file[:-4])

    def abstract_content(self):
        return self.abstract.abstract_content() if self.abstract else None

    def abstract_content_scpa(self):
        return self.jsondoc.abstract if self.jsondoc.abstract else None

    def has_abstract(self):
        return self.abstract_content() is not None

    def has_abstract_scpa(self):
        return self.abstract_content_scpa() is not None

    def pp(self):
        print('=' * 80)
        print(self.text_file)
        print('=' * 80)
        for para in self.paras:
            print(para.content)
            print('-' * 80)
        print()

    def print_abstracts(self, directory: str):
        file_name = os.path.join(directory, self.short_name() + '.html')
        with open(file_name, 'w') as fh:
            fh.write('<h2>%s</h2>\n' % self.short_name())
            heur_abstract = self.abstract_content()
            scpa_abstract = self.abstract_content_scpa()
            if heur_abstract:
                fh.write('<p><b>Abstract from simple heuristics</b><br/>\n')
                fh.write('%s</p>\n' % self.abstract_content())
            if scpa_abstract:
                fh.write('<p><b>Abstract from ScienceParse</b><br/>\n')
                fh.write('%s</p>\n' % self.abstract_content_scpa())
            fh.write('<hr/>\n')
            fh.write('%s\n' % self.content_as_html())

    def content_as_html(self):
        text = self.content
        a1 = self.abstract_content()
        a2 = self.abstract_content_scpa()
        if a1 is not None:
            idx = text.find(a1[:25])
            text = text[:idx] + '<b><span style="color:red">HEUR&gt; </span></b>' + text[idx:]
        if a2 is not None:
            idx = text.find(a2[:25])
            text = text[:idx] + '<b><span style="color:blue">SCPA&gt; </span></b>' + text[idx:]
        text = text.replace('\n', '<br>\n')
        return text


class Paragraph:

    def __init__(self, content: str, doc: Document):
        self.document = doc
        self.content = content.strip()
        self.lines = self.content.split("\n")
        self.previous = None
        self.next = None
        self.is_abstract = False

    def __str__(self):
        return ("<%s doc=%s abstract=%s len=%s>"
                % (self.__class__.__name__,
                   self.document.short_name(),
                   1 if self.is_abstract else 0,
                   len(self)))

    def __len__(self):
        return len(self.content)

    def abstract_content(self):
        if self.is_abstract:
            for i, line in enumerate(self.lines):
                if line.lower() == 'abstract':
                    return '\n'.join(self.lines[i + 1:])
        return ''

    def parse(self):
        if self.lines[0].lower() == 'abstract':
            self.is_abstract = True
            self.document.abstract = self
            return
        for line in self.lines:
            if line.lower() == 'abstract':
                self.is_abstract = True
                self.document.abstract = self
                return


class JsonDocument:

    def __init__(self, scpa_file):
        self.scpa_file = scpa_file
        with open(scpa_file) as fh:
            self.json = json.load(fh)
        self.abstract = self.get_abstract()
        self.sections = self.get_sections()
        self.headings = [section['heading'] for section in self.sections]

    def __str__(self):
        abstract = '' if self.abstract is None else ' abstract'
        return "<%s %s%s>" % (self.__class__.__name__, self.short_name(), abstract)

    def short_name(self):
        return os.path.basename(self.scpa_file)

    def get_abstract(self):
        if 'abstractText' in self.json['metadata']:
            return self.json['metadata']['abstractText']
        else:
            return None

    def get_sections(self):
        sections = self.json['metadata']['sections']
        return [] if sections is None else sections


def collect_documents(file_list):
    def document_from_line(line):
        text_file = line.strip()
        scpa_file = "%s_input.pdf.json" % text_file[:-4]
        identifier = text_file[:-4]
        text_path = os.path.join(TEXT_DIR, text_file)
        scpa_path = os.path.join(SCPA_DIR, scpa_file)
        return Document(identifier, text_path, scpa_path)

    with open(file_list) as fh:
        return [document_from_line(line) for line in fh]


def print_output(documents, directory: str):
    with open(os.path.join(directory, 'index.html'), 'w') as fh:
        fh.write('<body>\n')
        fh.write('<h1>%s</h1>\n' % directory)
        fh.write('<table width="100%" height="100%">\n')
        fh.write('<tr>\n')
        fh.write('<td valign="top" width="20%" height="100%">\n')
        fh.write('<table cellpadding=5 cellspacing=0 border=1 width="100%">\n')
        fh.write('<tr>\n')
        fh.write('  <td>document</td>\n')
        fh.write('  <td>lang</td>\n')
        fh.write('  <td>h</td>\n')
        fh.write('  <td>sp</td>\n')
        fh.write('</tr>\n')
        for doc in documents:
            print("%s" % doc)
            doc.print_abstracts(directory)
            name = doc.short_name()
            fh.write('<tr>\n')
            fh.write(f'  <td><a href="{name}.html" target="document">{name}</a><br/></td>\n')
            fh.write(f'  <td>{doc.language:.2f}</td>\n')
            fh.write(f'  <td>{"&#10003;" if doc.has_abstract() else "&nbsp;"}</td>\n')
            fh.write(f'  <td>{"&#10003;" if doc.has_abstract_scpa() else "&nbsp;"}</td>\n')
            fh.write('</tr>\n')
        fh.write('</table>\n')
        fh.write('</td>\n')
        fh.write('<td>&nbsp;</td>\n')
        fh.write('<td valign="top" width="80%" height="100%">\n')
        fh.write('<iframe src="" height="100%" width="100%" name="document" title="document"></iframe>\n')
        fh.write('</td>\n')
        fh.write('</tr>\n')
        fh.write('</table>\n')


if __name__ == '__main__':

    file_list = sys.argv[1]
    dir_name = os.path.join('../out', os.path.splitext(os.path.basename(file_list))[0])
    print('Writing results to', dir_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    docs = collect_documents(file_list)
    print_output(docs, dir_name)
