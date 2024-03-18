"""Core of the document parser

Contains classes that implement the behavior of documents and paragraphs.

"""

import os, json, glob
import sys
from collections import Counter
from dataclasses import dataclass
import frequencies
import utils

FREQUENT_ENGLISH_WORDS = set(
    [line.split()[1] for line in frequencies.FREQUENCIES.split('\n') if line])

DOCUMENT_TESTS = {
    'size': (utils.between, (1000, 500000)),
    'language': (utils.larger, 0.2),
    'medrxiv': (utils.smaller, 0.1),
    'section_count': (utils.larger, 1),
    'section_length': (utils.between, (0, 10000)),
    'section_headers_ratio': (utils.larger, 0.1)
}

PARAGRAPH_TESTS = {
    'language': (utils.larger, 0.3),
    'average_line_length': (utils.larger, 10),
    'average_token_length': (utils.larger, 4),
    'singletons_per_token': (utils.smaller, 0.1)}


class Documents:

    def __init__(self, file_list: str, html_dir: str, data_dir: str):
        """Initialize with a file list, an output directory for the html analysis
        view and an output directory for the processed and filtered data."""
        self.html_dir = html_dir
        self.data_dir = data_dir
        with open(file_list) as fh:
            self.text_dir = fh.readline().split()[2]
            self.scpa_dir = fh.readline().split()[2]
            self.names = [name.strip() for name in fh if not name.startswith('#')]
        self.initialize_documents()

    def initialize_documents(self):
        # using a generator because there could be many documents
        self.documents = (
            Document(
                name,
                self.text_filename(name),
                self.scpa_filename(name),
                self.output_filename(name))
            for name in self.names)

    def __iter__(self):
        return iter(self.documents)

    def __str__(self):
        return f'<Documents data_dir={self.data_dir} size={len(self.names)}>'

    def scpa_filename(self, name: str):
        return os.path.join(self.scpa_dir, f"{name}_input.pdf.json")

    def text_filename(self, name: str):
        return os.path.join(self.text_dir, f"{name}.txt")

    def output_filename(self, name: str):
        return os.path.join(self.data_dir, f"{name}.json")

    def write_output(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        count = 0
        for doc in self:
            count += 1
            if count % 100 == 0:
                print(count)
            doc.write_data(self.data_dir)

    def write_html(self):
        print('HTML', self.html_dir)
        if not os.path.exists(self.html_dir):
            os.makedirs(self.html_dir)
        with open(os.path.join(self.html_dir, 'index.html'), 'w') as fh:
            fh.write('<html>\n<head>\n</head>\n<body>\n')
            fh.write('<table width="100%" height="100%" cellspacing="10">\n')
            fh.write('<tr>\n')
            fh.write('<td valign="top" width="40%" height="100%">\n')
            fh.write('<table cellpadding=5 cellspacing=0 border=1 width="100%">\n')
            self._write_domain_name(fh)
            self._write_table_headers(fh)
            # recreate the generator because it was already used to print output
            self.initialize_documents()
            for i, doc in enumerate(self):
                doc.write_characteristics(fh, i)
                doc.write_analysis(self.html_dir, i)
            fh.write('</table>\n</td>\n')
            self._write_iframe(fh)
            fh.write('</tr>\n')
            fh.write('</table>\n</body>\n</html>\n')

    def _write_domain_name(self, fh):
        fh.write('<tr>\n')
        fh.write('  <td style="font-size: larger" colspan=12><b>%s</b></td>\n' % os.path.basename(self.html_dir))
        fh.write('</tr>\n')

    @staticmethod
    def _write_table_headers(fh):
        fh.write('<tr>\n')
        for header in ('n', 'document', 'links', 'size', 'text',
                       'lang', 'rxiv', '#s', 'avg(s)', 'h/s','ah', 'asp'):
            fh.write('  <td>%s</td>\n' % header)
        fh.write('</tr>\n')

    def _write_iframe(self, fh):
        """Print and empty iframe."""
        size = 'height="100%%" width="100%%"'
        fh.write('  <td valign="top" width="*" height="100%">\n')
        fh.write('    <iframe src="" %s name="doc"></iframe>\n' % size)
        fh.write('  </td>\n')

    @classmethod
    def write_html_index(cls, directory: str):
        directories = glob.glob(os.path.join(directory, "*-*-*-*"))
        with open(os.path.join(directory, 'index.html'), 'w') as fh:
            fh.write(f'<html>\n<body>\n<h2>Document structure parses</h2>\n<ul>\n')
            for subdir in sorted(directories):
                subdir = os.path.basename(subdir)
                url = os.path.join(subdir, 'index.html')
                fh.write(f'  <li><a href="{url}">{subdir}</a>\n')
            fh.write(f'</ul>\n</body>\n</html>\n')


class Document:

    def __init__(self, name: str, text_file: str, scpa_file: str, out_file: str):
        """Created from the name of the document ("5cd7d9e40b45c76caf88d812")
        and the locations of the text file and the ScienceParse file."""
        self.name = name
        self.text_file = os.path.abspath(text_file)
        self.scpa_file = os.path.abspath(scpa_file)
        self.out_file = os.path.abspath(out_file)
        with open(text_file) as fh:
            self.content = fh.read()
        self.paras = [Paragraph(p, self) for p in self.content.split("\n\n")]
        self.lines = self.content.split("\n")
        self.tokens = Counter(self.content.split())
        self.abstract = None
        self.para_count = len(self.paras)
        self.line_count = len(self.lines)
        self.token_count = sum(self.tokens.values())
        self.scpa_doc = ScpaDocument(scpa_file)
        self.tests = DOCUMENT_TESTS
        self.scores = DocumentScores(self)
        self.link_paragraphs()
        self.parse_paragraphs()
        # this will be filled in when the output string is created
        self.output_size = None

    def __str__(self):
        abstract = ' heur_abstract' if self.abstract else ''
        abstract_text = ' scpa_abstract' if self.scpa_doc.abstract else ''
        return ("<%s %s lang=%.2f len=%06d%s%s>"
                % (self.class_name(), self.name, self.scores.language,
                   len(self), abstract, abstract_text))

    def __len__(self):
        return len(self.content)

    def link_paragraphs(self):
        """Turn the paragraph list into a linked list."""
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
        return self.scpa_doc.abstract if self.scpa_doc.abstract else None

    def has_abstract(self):
        return self.abstract_content() is not None

    def has_abstract_scpa(self):
        return self.abstract_content_scpa() is not None

    def pick_abstract(self):
        """Pick the best available abstract. We go for the heuristics abstract
        over the ScienceParse abstract."""
        if self.has_abstract():
            return {'source': 'text', 'abstract': self.abstract_content()}
        if self.has_abstract_scpa():
            return {'source': 'scpa', 'abstract': self.scpa_doc.get_abstract()}
        else:
            return None

    def is_useful(self):
        """Return True if all the tests defined for the scores return True."""
        #print('DOC', self)
        return utils.run_tests(self.tests, self.scores)

    def write_characteristics(self, fh, i: int):
        """Write characteristics of the file to the table."""
        def color_mark(doc):
            return '' if doc.is_useful() else f' bgcolor="{utils.light_red}"'
        fh.write('<tr>\n')
        fh.write(f'  <td align=right>{i}</td>\n')
        # fh.write(f'  <td{color_mark(self)}>{self.name}</td>\n')
        fh.write(f'  <td>{self.name}</td>\n')
        fh.write(f'  <td>\n')
        fh.write(f'    <a href="{self.text_file}" target="doc">text</a>\n')
        fh.write(f'    <a href="{self.scpa_file}" target="doc">scpa</a>\n')
        fh.write(f'    <a href="{self.out_file}" target="doc">out</a>\n')
        fh.write(f'    <a href="{self.name}.html" target="doc">html</a>\n')
        fh.write(f'  </td>\n')
        # size = int((len(self)/1000))
        outsize = int(os.path.getsize(self.out_file) / 1000)
        fh.write(utils.td(f"{outsize:d}K", align='right'))
        utils.write_scores(fh, self.tests, self.scores)
        fh.write(utils.td("&#10003;" if self.has_abstract() else "&nbsp;"))
        fh.write(utils.td("&#10003;" if self.has_abstract_scpa() else "&nbsp;"))
        fh.write('</tr>\n')

    def write_analysis(self, directory: str, i: int):
        file_name = os.path.join(directory, self.name + '.html')
        with open(file_name, 'w') as fh:
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

    def write_data(self, directory: str):
        morsels = Morsels(self)
        with open(self.out_file, 'w') as fh:
            output = json.dumps(morsels.as_json(), indent=4)
            self.output_size = len(output)
            fh.write(output)


@dataclass()
class DocumentScores:
    size: int = 0
    language: float = 0
    medrxiv: float = 0
    section_count: int = 0
    section_length: int = 0
    section_headers_ratio: float = 0.0

    def __init__(self, document: Document):
        self.document = document
        scpa_doc = self.document.scpa_doc
        self.size = len(self.document)
        self.language = utils.language_score(document.tokens, FREQUENT_ENGLISH_WORDS)
        self.medrxiv = utils.medrxiv_score(document.content, document.para_count)
        self.section_count = len(scpa_doc.sections)
        self.section_length = scpa_doc.section_length
        self.section_headers_ratio = scpa_doc.section_headers_ratio


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
        self.scores = ParagraphScores(self)

    def __str__(self):
        return ("<%s doc=%s abstract=%s len=%s>"
                % (self.__class__.__name__,
                   self.document.name,
                   1 if self.is_abstract else 0,
                   len(self)))

    def __len__(self):
        return len(self.content)

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
        #print('PAR', self, self.content[:100])
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

    def write_output(self):
        pass


@dataclass()
class ParagraphScores:

    size: int = 0
    language: float = 0
    average_line_length: float = 0.0
    average_token_length: float = 0.0
    singletons_per_token: float = 0.0

    def __init__(self, paragraph):
        self.size = len(paragraph)
        self.language = utils.language_score(paragraph.tokens, FREQUENT_ENGLISH_WORDS)
        self.average_line_length = paragraph.average_line_length()
        self.average_token_length = paragraph.average_token_length()
        self.singletons_per_token = paragraph.singletons_per_token()

    def __str__(self):
        return (
            f"<ParagraphScores lan={self.language:.2f} ll={self.average_line_length:.2f}"
            + f" tl={self.average_token_length:.2f} st={self.singletons_per_token:.2f}>")


class ScpaDocument:

    # NOTE: could consider introducing a ScpaScores class, on a par with the
    # DocumentScores class, but we are already using DocumentScores to include
    # scores from the SCPA file

    def __init__(self, scpa_file):
        self.scpa_file = scpa_file
        try:
            with open(scpa_file) as fh:
                self.json = json.load(fh)
        except FileNotFoundError:
            self.json = {}
        self.metadata = self.json.get('metadata', {})
        self.title = self.get_title()
        self.abstract = self.get_abstract()
        self.sections = self.get_sections()
        self.section_length = self.get_average_section_length()
        self.section_headers = [s['heading'] for s in self.sections if s['heading']]
        self.section_headers_ratio = self.get_section_headers_ratio()

    def __str__(self):
        abstract = '' if self.abstract is None else ' abstract'
        return "<%s %s%s>" % (self.__class__.__name__, self.short_name(), abstract)

    def short_name(self):
        return os.path.basename(self.scpa_file)

    def get_title(self):
        return self.metadata.get('title')

    def get_abstract(self):
        return self.metadata.get('abstractText')

    def get_sections(self):
        sections = self.metadata.get('sections', [])
        return [] if sections is None else sections

    def get_average_section_length(self):
        try:
            return int(sum([len(s['text']) for s in self.sections]) / len(self.sections))
        except ZeroDivisionError:
            return 0

    def get_section_headers_ratio(self):
        try:
            return len(self.section_headers) / len(self.sections)
        except ZeroDivisionError:
            return 0.0


class Morsels:

    """Picking the best available data from the document, choosing from the
    ScienceParse document and the heuristics."""

    # TODO: why is this not using the tests?

    def __init__(self, doc: Document):
        self.doc = doc
        self.title = doc.scpa_doc.title
        self.abstract = None
        self.sections = []
        if doc.scores.section_count > 1 and doc.scores.section_length < 10000:
            # use SCPA analysis if the sections are not too long
            self.mode = 'scpa'
        else:
            # otherwise go with the text
            self.mode = 'text' if doc.scores.language > 0.2 else 'none'
        # self.pp()
        if self.mode in ('scpa', 'text'):
            self.abstract = doc.pick_abstract()
        if self.mode == 'scpa':
            for section in doc.scpa_doc.sections:
                tokens = Counter(section['text'].split())
                language = utils.language_score(tokens, FREQUENT_ENGLISH_WORDS)
                if language > 0.3:
                    self.sections.append(
                        {'source': 'scpa',
                         'heading': section['heading'],
                         'text': section['text']})
        elif self.mode == 'text':
            for para in doc.paras:
                # TODO: some code potentially useful for more fine-grained filtering
                #print('\n'); print(para, para.scores); print()
                #print(para.content.strip()); print()
                #for line in para.content.split('\n'):
                #    p = Paragraph(line, self.doc)
                #    print(f"\t{p.scores}\t{line[:120]}")
                language = utils.language_score(para.tokens, FREQUENT_ENGLISH_WORDS)
                if language > 0.3:
                    self.sections.append(
                        {'source': 'text',
                         'heading': None,
                         'text': para.content})

    def as_json(self):
        return {'title': self.title,
                'abstract': self.abstract,
                'sections': self.sections}

    def pp(self):
        print(f'{self.doc.name}  {self.doc.scores.language:.2f}'
              f'  {self.doc.scores.section_count:2d}'
              f'  {self.doc.scores.section_length:6d}  {self.mode}')
