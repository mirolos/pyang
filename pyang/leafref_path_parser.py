"""XPath 1.0 parser

PLY-based parser to build an AST for a YANG leafref path expression

"""

import collections

from . import yacc
from . import leafref_path_lexer

def parse(source):
    """Parse a Leafref path expression.

    A deref function invocation is permitted above the grammar defined in
    RFC7950. Whitespace is allowed exactly as in the RFC7950 grammar.
    Each identifier is a plain string or 2-tuple if prefix is used.

    The resulting parsed structure is a 4-tuple:
    - up - integer count of ../ fragments in relative path, or -1 for absolute
    - dn - list of identifiers or key predicates to follow down
    - derefup - integer count of ../ fragments in deref invocation
    - derefdn - list of identifiers or predicates in deref invocation, or None

    Each predicate is another 4-tuple:
    - literal - 'predicate'
    - node_id - left-hand node identifier
    - up - integer count of ../ fragments after current() invocation
    - dn - list of segments to follow
    """
    return parser.parse(source, lexer=lexer, debug=False)


LeafrefPathArg = collections.namedtuple(
    'LeafrefPathArg', ['up', 'dn', 'derefup', 'derefdn'])


LeafrefPathPredicate = collections.namedtuple(
    'LeafrefPathPredicate', ['literal', 'node_id', 'up', 'dn'])


### Parser follows

def p_path_arg(p):
    '''path_arg : deref_expr
                | path_str'''
    if len(p[1]) == 2:
        args = p[1] + (0, None)
    else:
        args = p[1]
    p[0] = LeafrefPathArg(*args)

def p_deref_expr(p):
    '''deref_expr : deref_function_invocation wsp_slash_wsp relative_path'''
    p[0] = p[3] + p[1]  # up, dn + derefup, derefdn

def p_path_str(p):
    '''path_str : absolute_path
                | relative_path'''
    if isinstance(p[1], tuple):
        p[0] = p[1]  # relative path
    else:
        p[0] = -1, p[1]

def p_absolute_path(p):
    '''absolute_path : absolute_path_segment absolute_path_segment_list'''
    p[1].extend(p[2])
    p[0] = p[1]

def p_relative_path(p):
    '''relative_path : dots_slash_seq descendant_path'''
    p[0] = p[1], p[2]

def p_descendant_path(p):
    '''descendant_path : node_identifier
                       | node_identifier path_predicate_list absolute_path'''
    p[0] = [p[1]]
    if len(p) == 4:
        p[0].extend(p[2])
        p[0].extend(p[3])

def p_path_predicate(p):
    '''path_predicate : left_square_bracket_wsp path_equality_expr \
                        wsp_right_square_bracket'''
    p[0] = p[2]

def p_path_equality_expr(p):
    '''path_equality_expr : node_identifier wsp_equal_wsp path_key_expr'''
    p[0] = LeafrefPathPredicate('predicate', p[1], *p[3])

def p_path_key_expr(p):
    '''path_key_expr : current_function_invocation wsp_slash_wsp \
                       rel_path_keyexpr'''
    p[0] = p[3]

def p_rel_path_keyexpr(p):
    '''rel_path_keyexpr : dots_wsp_slash_wsp_seq \
                          node_identifier_wsp_slash_wsp_list node_identifier'''
    p[2].append(p[3])
    p[0] = p[1], p[2]

def p_current_function_invocation(p):
    '''current_function_invocation : CURRENT_KEYWORD wsp_left_parenthesis_wsp \
                                     RIGHT_PARENTHESIS'''
    p[0] = 'current()'

def p_deref_function_invocation(p):
    '''deref_function_invocation : DEREF_KEYWORD wsp_left_parenthesis_wsp \
                                   relative_path wsp_right_parenthesis'''
    p[0] = p[3]

def p_node_identifier(p):
    '''node_identifier : prefix COLON identifier
                       | identifier'''
    if len(p) == 4:
        p[0] = p[1], p[3]
    else:
        p[0] = p[1]

def p_identifier(p):
    '''identifier : IDENTIFIER
                  | CURRENT_KEYWORD
                  | DEREF_KEYWORD
       prefix : identifier'''
    p[0] = p[1]

# accumulators for repetitions in main grammar

def p_dots_slash_seq(p):
    '''dots_slash_seq : dots_slash_seq DOTS SLASH
                      |
       dots_wsp_slash_wsp_seq : dots_wsp_slash_wsp_seq DOTS wsp_slash_wsp
                              |'''
    if len(p) == 1:
        p[0] = 0  # start counter on empty sequence
    else:
        p[0] = p[1] + 1

def p_absolute_path_segment(p):
    'absolute_path_segment : SLASH node_identifier path_predicate_list'
    p[3].insert(0, p[2])
    p[0] = p[3]  # reuse accumulator

def p_zero_or_more_lists(p):
    '''path_predicate_list : path_predicate_list path_predicate
                           |
       node_identifier_wsp_slash_wsp_list : node_identifier_wsp_slash_wsp_list \
                                            node_identifier wsp_slash_wsp
                                          |
       absolute_path_segment_list : absolute_path_segment_list \
                                    absolute_path_segment
                                  |'''
    if len(p) == 1:
        p[0] = []  # start accumulator
    else:
        p[0] = p[1]  # reuse accumulator
        if isinstance(p[2], list):
            p[0].extend(p[2])
        else:
            p[0].append(p[2])

# literals with optional whitespace around

def p_wsp_slash_wsp(p):
    '''wsp_slash_wsp : SLASH
                     | WSP SLASH
                     | SLASH WSP
                     | WSP SLASH WSP'''
    p[0] = '/'

def p_wsp_equal_wsp(p):
    '''wsp_equal_wsp : EQUAL
                     | WSP EQUAL
                     | EQUAL WSP
                     | WSP EQUAL WSP'''
    p[0] = '='

def p_left_square_bracket_wsp(p):
    '''left_square_bracket_wsp : LEFT_SQUARE_BRACKET
                               | LEFT_SQUARE_BRACKET WSP'''
    p[0] = '['

def p_wsp_right_square_bracket(p):
    '''wsp_right_square_bracket : RIGHT_SQUARE_BRACKET
                                | WSP RIGHT_SQUARE_BRACKET'''
    p[0] = ']'

def p_wsp_left_parenthesis_wsp(p):
    '''wsp_left_parenthesis_wsp : LEFT_PARENTHESIS
                                | WSP LEFT_PARENTHESIS
                                | LEFT_PARENTHESIS WSP
                                | WSP LEFT_PARENTHESIS WSP'''
    p[0] = '('

def p_wsp_right_parenthesis(p):
    '''wsp_right_parenthesis : RIGHT_PARENTHESIS
                             | WSP RIGHT_PARENTHESIS'''
    p[0] = ')'


def p_error(token):
    if token:
        raise SyntaxError(
            '[L{line}:C{column}]:, before {value!r}'.format(
                line=token.lineno, column=token.lexpos, value=token.value))
    else:
        raise SyntaxError('unexpected end of expression')


tokens = leafref_path_lexer.token_defs()
lexer = leafref_path_lexer.LeafrefPathLexer()
parser = yacc.yacc(tabmodule="leafref_path_parsetab", debug=False)
