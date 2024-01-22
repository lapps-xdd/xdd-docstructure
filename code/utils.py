import os, re, datetime
from pathlib import Path
from collections import Counter


def timestamp():
    dt = datetime.datetime.now()
    return "%04d%02d%02d-%02d%02d%02d" % (dt.year, dt.month, dt.day,
                                          dt.hour, dt.minute, dt.second)


def basename(path: str):
    """Like os.path.basename, but also splits off the extension."""
    return os.path.splitext(os.path.basename(path))[0]


def run_tests(tests: dict, scores) -> bool:
    """Return True if all the tests defined for the scores return True. The
    scores argument is either an instance of document.DocumentScores or an
    instance of document.ParagraphScores."""
    test_scores = []
    for test_name, val in scores.__dict__.items():
        if test_name in tests:
            test = tests[test_name][0]
            threshold_value = tests[test_name][1]
            test_scores.append(test(val, threshold_value))
    return False not in test_scores


def language_score(tokens: Counter, frequent_words: set) -> float:
    """This score measures what percentage of tokens are in a given list of
    frequent words. Returns a floating number between 0 and 1. This score
    tends to be below 0.1 when the text is not English or when it is more
    like a listing of results."""
    total_tokens = sum(tokens.values())
    in_frequent_words = sum([count for token, count in tokens.items()
                             if token in frequent_words])
    try:
        return in_frequent_words / total_tokens
    except ZeroDivisionError:
        return 0


def medrxiv_score(text: str, para_count: int) -> float:
    """Measures the number of occurrences of the string 'medRxiv' per
    paragraph in the text. When this score is over 0.1 then we tend to
    have a listing of abstracts."""
    count = len(list(re.finditer('medRxiv', text)))
    try:
        return count / para_count
    except ZeroDivisionError:
        return 0


def average_token_length(number_of_tokens: int, tokens: Counter):
    """Returns the average token length in characters."""
    total_length = 0
    for token, count in tokens.items():
        total_length += count * len(token)
    try:
        return total_length / number_of_tokens
    except ZeroDivisionError:
        return 0


def smaller(x, y):
    return x < y


def larger(x, y):
    return x > y


def between(x: int, pair: tuple):
    minimal_value, maximum_value = pair
    return minimal_value < x < maximum_value


def write_scores(fh, tests, scores, add_name=False, print_succes=False):
    """Write the scores that have tests associated with them as html table
    cells, add red background for the cell if the score failed the test."""
    success_color = light_green if print_succes else 'white'
    for test_name, val in scores.__dict__.items():
        if test_name in tests:
            test = tests[test_name][0]
            threshold_value = tests[test_name][1]
            good = test(val, threshold_value)
            bg_color = (' bgcolor="%s"' % success_color
                        if good else ' bgcolor="%s"' % light_red)
            if test_name == 'size':
                print_val = '%dK' % (val / 1000)
            elif type(val) == float:
                print_val = f'{val:.2f}'
            else:
                print_val = str(val)
            if add_name:
                print_val = '%s=%s' % (test_name, print_val)
            fh.write('  <td%s align=right>%s</td>\n' % (bg_color, print_val))


def trim_filename(name: str, extension: str = '') -> str:
    """Remove the extension an extension from the file name. In the context of
    current data this will be .txt for the text files and _input.pdf.json for
    the science parse files."""
    if name.endswith(extension):
        name = name[:-len(extension)]
    return name


def strip_extensions(file_name):
    fname = Path(file_name)
    while fname.suffix:
        fname = fname.with_suffix('')
    return fname


def td(cell, alert=False, align=None):
    alignment = '' if align is None else ' align="%s"' % align
    color = ' bgcolor=%s' % light_red if alert else ''
    return f'  <td{alignment}{color}>{cell}</td>\n'


light_grey = '#EEEEEE'
light_red = '#FDEDEC'
light_blue = '#EBF5FB'
light_green = '#E9F7EF'
