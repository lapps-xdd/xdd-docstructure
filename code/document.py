"""Core of the document parser

Contains classes that implement the behavior of documents and paragraphs.

"""

import os, json
from collections import Counter
from dataclasses import dataclass
import frequencies
import utils

FREQUENT_ENGLISH_WORDS = set(
    [line.split()[1] for line in frequencies.FREQUENCIES.split('\n') if line])

DOCUMENT_TESTS = {
    'size': (utils.larger, 1000),
    'language': (utils.larger, 0.2),
    'medrxiv': (utils.smaller, 0.1)}

PARAGRAPH_TESTS = {
    'language': (utils.larger, 0.2),
    'average_line_length': (utils.larger, 10),
    'average_token_length': (utils.larger, 4),
    'singletons_per_token': (utils.smaller, 0.1)}


class Documents:

    def __init__(self, file_list: str, html_dir: str, exp=''):
        self.html_dir = html_dir
        self.documents = []
        with open(file_list) as fh:
            text_dir = fh.readline().split()[2]
            scpa_dir = fh.readline().split()[2]
            print('TEXT', text_dir)
            print('SCPA', scpa_dir)
            for line in fh:
                if exp in line:
                    name = line.strip()
                    text_file = "%s.txt" % name
                    scpa_file = "%s_input.pdf.json" % name
                    text_path = os.path.join(text_dir, text_file)
                    scpa_path = os.path.join(scpa_dir, scpa_file)
                    doc = Document(name, text_path, scpa_path)
                    self.documents.append(doc)

    def __getitem__(self, item):
        return self.documents[item]

    def __iter__(self):
        return iter(self.documents)

    def write_html(self):
        print('Writing results to', self.html_dir)
        if not os.path.exists(self.html_dir):
            os.makedirs(self.html_dir)
        with open(os.path.join(self.html_dir, 'index.html'), 'w') as fh:
            fh.write('<html>\n<head>\n</head>\n<body>\n')
            fh.write('<table width="100%" height="100%" cellspacing="10">\n')
            fh.write('<tr>\n')
            fh.write('<td valign="top" width="30%" height="100%">\n')
            # fh.write('<h2>%s</h2>\n' % os.path.basename(directory))
            fh.write('<table cellpadding=5 cellspacing=0 border=1 width="100%">\n')
            # write the table headers
            fh.write('<tr>\n')
            for header in ('n', 'document', 'links', 'size',
                           'lang', 'rxiv', 'h', 'sp'):
                fh.write('  <td>%s</td>\n' % header)
            fh.write('</tr>\n')
            # deal with all the documents
            for i, doc in enumerate(self):
                print("%d %s" % (i, doc))
                doc.write_html_to_file(self.html_dir, i)
                doc.write_characteristics(fh, i)
            fh.write('</table>\n</td>\n')
            self._write_iframe(fh)
            fh.write('</tr>\n')
            fh.write('</table>\n</body>\n</html>\n')

    def _write_iframe(self, fh):
        """Print the iframe with the first document to the index file."""
        first_document = self.documents[0]
        first_doc_url = f"{first_document.name}.html"
        # first_doc_scpa_url = first_document.scpa_file
        size = 'height="100%%" width="100%%"'
        fh.write('  <td valign="top" width="*" height="100%">\n')
        fh.write('    <iframe src="%s" %s name="doc"></iframe>\n' % (first_doc_url, size))
        fh.write('  </td>\n')


@dataclass
class DocumentScores:
    size: int = 0
    language: float = 0
    medrxiv: float = 0


class Document:

    # TODO: feed in the abstract from spca and its characteristics

    def __init__(self, name: str, text_file: str, scpa_file: str):
        self.name = name
        self.text_file = text_file
        self.scpa_file = scpa_file
        with open(text_file) as fh:
            self.content = fh.read()
        self.paras = [Paragraph(p, self) for p in self.content.split("\n\n")]
        self.lines = self.content.split("\n")
        self.tokens = Counter(self.content.split())
        self.abstract = None
        self.para_count = len(self.paras)
        self.line_count = len(self.lines)
        self.token_count = sum(self.tokens.values())
        self.json_doc = JsonDocument(scpa_file)
        self.tests = DOCUMENT_TESTS
        self.scores = DocumentScores()
        self.set_scores()
        self.link_paragraphs()
        self.parse_paragraphs()

    def __str__(self):
        abstract = ' heur_abstract' if self.abstract else ''
        abstract_text = ' scpa_abstract' if self.json_doc.abstract else ''
        return "<%s %s lang=%.2f len=%06d%s%s>" % (self.class_name(), self.name, self.scores.language,
                                                   len(self), abstract, abstract_text)

    def __len__(self):
        return len(self.content)

    def set_scores(self):
        self.scores.size = len(self)
        self.scores.language = utils.language_score(self.tokens, FREQUENT_ENGLISH_WORDS)
        self.scores.medrxiv = utils.medrxiv_score(self.content, self.para_count)

    def link_paragraphs(self):
        """Turn the paragraph list in to a linked list."""
        for i in range(len(self.paras) - 1):
            self.paras[i].next = self.paras[i + 1]
            self.paras[i + 1].previous = self.paras[i]

    def parse_paragraphs(self):
        for para in self.paras:
            para.parse()

    def class_name(self):
        return self.__class__.__name__

    def abstract_content(self):
        return self.abstract.abstract_content() if self.abstract else None

    def abstract_content_scpa(self):
        return self.json_doc.abstract if self.json_doc.abstract else None

    def has_abstract(self):
        return self.abstract_content() is not None

    def has_abstract_scpa(self):
        return self.abstract_content_scpa() is not None

    def is_useful(self):
        """Return True if all the tests defined for the scores return True."""
        return utils.run_tests(self.tests, self.scores)

    def write_html_to_file(self, directory: str, i: int):
        file_name = os.path.join(directory, self.name + '.html')
        with open(file_name, 'w') as fh:
            self.write_html(fh, i)

    def write_html(self, fh, i: int):
        with open('style.css') as style_fh:
            fh.write(style_fh.read())
        h2_style = 'style="background: %s; padding: 5;"' % utils.light_red
        if self.is_useful():
            h2_style = 'style="background: %s; padding: 5;"' % utils.light_green
        fh.write('<h2 %s">%s - %s</h2>\n' % (h2_style, i, self.name))
        heur_abstract = self.abstract_content()
        scpa_abstract = self.abstract_content_scpa()
        if heur_abstract:
            fh.write('<h3>Abstract from simple heuristics</h3>\n')
            fh.write('%s</p>\n' % self.abstract_content().replace('\n', '<br>\n'))
        if scpa_abstract:
            fh.write('<h3>Abstract from ScienceParse</h3>\n')
            fh.write('%s\n' % self.abstract_content_scpa().replace('\n', '<br>\n'))
        fh.write('<h3>Paragraphs</h3>\n')
        for para in self.paras:
            para.write_html(fh)

    def write_characteristics(self, fh, i: int):
        def color_mark(doc):
            return '' if doc.is_useful() else f' bgcolor="{utils.light_red}"'
        fh.write('<tr>\n')
        fh.write(f'  <td align=right>{i}</td>\n')
        fh.write(f'  <td{color_mark(self)}>{self.name}</td>\n')
        fh.write(f'  <td>\n')
        fh.write(f'    <a href="{self.name}.html" target="doc">parse</a>\n')
        fh.write(f'    <a href="{self.text_file}" target="doc">text</a>\n')
        fh.write(f'    <a href="{self.scpa_file}" target="doc">scpa</a>\n')
        fh.write(f'  </td>\n')
        # size = int((len(self)/1000))
        utils.write_scores(fh, self.tests, self.scores)
        fh.write(utils.td("&#10003;" if self.has_abstract() else "&nbsp;"))
        fh.write(utils.td("&#10003;" if self.has_abstract_scpa() else "&nbsp;"))
        fh.write('</tr>\n')


@dataclass
class ParagraphScores:
    size: int = 0
    language: float = 0
    average_line_length: float = 0.0
    average_token_length: float = 0.0
    singletons_per_token: float = 0.0


class Paragraph:

    def __init__(self, content: str, doc: Document):
        self.document = doc
        self.content = content.strip()
        self.lines = self.content.split("\n")
        self.tokens = Counter(self.content.split())
        self.line_count = len(self.lines)
        self.token_count = sum(self.tokens.values())
        self.previous = None
        self.next = None
        self.is_abstract = False
        self.tests = PARAGRAPH_TESTS
        self.scores = ParagraphScores()
        self.set_scores()

    def __str__(self):
        return ("<%s doc=%s abstract=%s len=%s>"
                % (self.__class__.__name__,
                   self.document.name,
                   1 if self.is_abstract else 0,
                   len(self)))

    def __len__(self):
        return len(self.content)

    def set_scores(self):
        self.scores.size = len(self)
        self.scores.language = utils.language_score(self.tokens, FREQUENT_ENGLISH_WORDS)
        self.scores.average_line_length = self.average_line_length()
        self.scores.average_token_length = self.average_token_length()
        self.scores.singletons_per_token = self.singletons_per_token()

    def average_line_length(self):
        return len(self) / self.line_count

    def average_token_length(self):
        return utils.average_token_length(self.token_count, self.tokens)

    def singletons_per_token(self) -> float:
        singletons = [t for t in self.tokens if len(t) == 1]
        try:
            return len(singletons) / self.token_count
        except ZeroDivisionError:
            return 0.0

    def abstract_content(self) -> str:
        """Return the text of the paragraph after the line with 'abstract',
        the returned text can be the empty string."""
        # TODO: include lines from the next paragraph, especially if this
        #       returns an emtpy string after the abstract line
        for i, line in enumerate(self.lines):
            if line.lower() == 'abstract':
                return '\n'.join(self.lines[i + 1:])
        return ''

    def parse(self):
        for i, line in enumerate(self.lines):
            if line.lower() == 'abstract':
                if self.abstract_content():
                    self.is_abstract = True
                    self.document.abstract = self
                break

    def is_useful(self):
        """Return True if the paragraph is an abstract or if all the tests
        defined for the scores return True."""
        return self.is_abstract or utils.run_tests(self.tests, self.scores)

    def write_html(self, fh):
        if self.is_abstract or self.is_useful():
            bg_color = utils.light_green
        else:
            bg_color = 'white'
        content = self.content.replace('\n', '<br>\n')
        self.write_characteristics(fh)
        style = 'background-color: %s; padding: 5px;' % bg_color
        fh.write('<p style="%s">%s</p>\n' % (style, content))

    def write_characteristics(self, fh):
        # def color_mark(doc):
        #     return '' if doc.is_useful() else f' bgcolor="{utils.light_red}"'
        fh.write('<table cellspacing=0 cellpadding=5 border=1>\n')
        fh.write('<tr>\n')
        bg_color = 'bgcolor="%s"' % utils.light_grey
        fh.write(f'  <td {bg_color}>size={len(self)}</td>\n')
        fh.write(f'  <td {bg_color}>lines={self.line_count}</td>\n')
        fh.write(f'  <td {bg_color}>tokens={self.token_count}</td>\n')
        if self.is_abstract:
            bg_color = 'bgcolor="%s"' % utils.light_blue
        fh.write(f'  <td {bg_color}>abstract={self.is_abstract}</td>\n')
        utils.write_scores(fh, self.tests, self.scores, add_name=True, print_succes=True)
        fh.write('</tr>\n')
        fh.write('</table>\n')


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
