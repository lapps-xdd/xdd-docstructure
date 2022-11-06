import re
from collections import Counter


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


def write_scores(fh, tests, scores, add_name=False, print_succes=False):
    """Write the scores that have tests associated with them as html table
    cells, add red background for the cell if the score failed the test."""
    succes_color = light_green if print_succes else 'white'
    for test_name, val in scores.__dict__.items():
        if test_name in tests:
            test = tests[test_name][0]
            threshold_value = tests[test_name][1]
            good = test(val, threshold_value)
            bgcolor = ' bgcolor="%s"' % succes_color if good else ' bgcolor="%s"' % light_red
            if test_name == 'size':
                print_val = '%dK' % (val / 1000)
            elif type(val) == float:
                print_val = f'{val:.2f}'
            else:
                print_val = str(val)
            if add_name:
                print_val = '%s=%s' % (test_name, print_val)
            fh.write('<td align=right%s>%s</td>\n' % (bgcolor, print_val))


def td(cell, alert=False, align=None):
    alignment = '' if align is None else ' align="%s"' % align
    color = ' bgcolor=%s' % light_red if alert else ''
    return f'  <td{alignment}{color}>{cell}</td>\n'


light_red = '#FDEDEC'
light_blue = '#EBF5FB'
light_green = '#E9F7EF'
