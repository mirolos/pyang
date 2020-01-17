"""XPath 1.0 lexer / scanner

Used with the PLY-based parser xpath_parser.py.

See http://www.w3.org/TR/1999/REC-xpath-19991116
"""

import collections
import re


LeafrefPathTok = collections.namedtuple(
    'LeafrefPathTok', ['type', 'value', 'lineno', 'lexpos', 'lexer'])


class LeafrefPathLexer(object):

    tokens = None

    def input(self, source):
        self.tokens = scan(source, self)

    def token(self):
        if self.tokens is not None:
            try:
                return next(self.tokens)
            except StopIteration:
                self.tokens = None
            except SyntaxError:
                self.tokens = None
                raise
        return None

    def __repr__(self):
        return 'LPL'

patterns = [
    # whitespace collapsed into one token
    ('WSP', re.compile(r'[ \t]+')),
    ('LEFT_PARENTHESIS', re.compile(r'\(')),
    ('RIGHT_PARENTHESIS', re.compile(r'\)')),
    ('LEFT_SQUARE_BRACKET', re.compile(r'\[')),
    ('RIGHT_SQUARE_BRACKET', re.compile(r'\]')),
    ('DOTS', re.compile(r'\.\.')),
    ('SLASH', re.compile(r'\/')),
    ('EQUAL', re.compile(r'=')),
    ('COLON', re.compile(r':')),
    ('IDENTIFIER', re.compile(r'[a-zA-Z_][a-zA-Z0-9_\-.]*')),
    ]


functions = {
    # only these two functions are available, and have special tokens
    'current': 'CURRENT_KEYWORD',
    'deref': 'DEREF_KEYWORD',
    }


def token_defs():
    tokens = [p[0] for p in patterns]
    tokens.extend(functions.values())
    return tokens


def scan(source, lexer):
    """Generate sequence of tokens, or raise SyntaxError on failure.
    """
    line = 1  # no line breaks in paths allowed
    linepos = 1
    pos = 0
    while pos < len(source):
        for tokname, pattern in patterns:
            match = pattern.match(source, pos)
            if match is not None:
                value = match.group(0)
                if tokname == 'IDENTIFIER':
                    tokname = functions.get(value, tokname)

                yield LeafrefPathTok(tokname, value, line, linepos, lexer)

                length = len(value)
                pos += length
                linepos += length
                break
        else:
            raise SyntaxError('syntax error', line, linepos)
