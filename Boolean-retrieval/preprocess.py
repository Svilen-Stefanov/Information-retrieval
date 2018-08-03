import re
from nltk.stem.porter import PorterStemmer

"""
    File name: preprocess.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 06/03/2018
    Python Version: 2.7
"""

ps = PorterStemmer()

all_operators = ["AND", "OR", "NOT", "AND NOT", "(", ")"]


def preprocess_andnot(expr):
    """
    For all expressions of type NOT A AND B, where A and B can also be expressions in parenthesis,
    convert the query in the form B AND NOT A. AND NOT will be considered as a special operator after the call of this
    method.
    :param expr: the query as a boolean expression
    :return: the reordered boolean expression
    """
    # NOT (A) AND (B) -> A and B can be longer expressions without nested parenthesis
    original_expr = re.findall(r'NOT (?P<not_clause>\([^\)]*\)) AND (?P<and_clause>\([^\)]*\))', expr)
    for not_cl, and_cl in original_expr:
        expr_to_replace = 'NOT ' + not_cl + ' AND ' + and_cl
        reorder_expr = and_cl + ' AND NOT ' + not_cl
        expr = expr.replace(expr_to_replace, reorder_expr)

    # NOT (A) AND B -> B is a single word
    original_expr = re.findall(r'NOT (?P<not_clause>\([^\)]*\)) AND (?P<and_clause>[a-zA-Z0-9]+)', expr)
    for not_cl, and_cl in original_expr:
        if and_cl != 'NOT':
            expr_to_replace = 'NOT ' + not_cl + ' AND ' + and_cl
            reorder_expr = and_cl + ' AND NOT ' + not_cl
            expr = expr.replace(expr_to_replace, reorder_expr)

    # NOT A AND (B) -> A is a single word
    original_expr = re.findall(r'NOT (?P<not_clause>[a-zA-Z0-9]+) AND (?P<and_clause>\([^\)]*\))', expr)
    for not_cl, and_cl in original_expr:
        expr_to_replace = 'NOT ' + not_cl + ' AND ' + and_cl
        reorder_expr = and_cl + ' AND NOT ' + not_cl
        expr = expr.replace(expr_to_replace, reorder_expr)

    # NOT A AND B -> A, B are single words
    original_expr = re.findall(r'NOT (?P<not_clause>[a-zA-Z0-9]+) AND (?P<and_clause>[a-zA-Z0-9]+)', expr)
    for not_cl, and_cl in original_expr:
        if and_cl != 'NOT':
            expr_to_replace = 'NOT ' + not_cl + ' AND ' + and_cl
            reorder_expr = and_cl + ' AND NOT ' + not_cl
            expr = expr.replace(expr_to_replace, reorder_expr)
    return expr


def eval_expr_size(expr, term_dict):
    """
    Evaluates the size of the posting list of a given expression (if existing in the term dictionary).
    The expression can also contain more than a single term. For example ( A AND B OR C ) would be a valid value for expr.
    :param expr: the given boolean expression for which the size will be calculated
    :param term_dict: the dictionary with all terms and their frequency
    :return: 0 - if not in the term dictionary
             document frequency of the term - if the term is present in the dictionary
    """
    res = 0
    expr = expr.strip()
    expr_words = expr.split()
    if len(expr_words) == 1:
        if expr not in term_dict:
            return 0
        res = term_dict[expr]['f']
    elif len(expr_words) == 2 and expr_words[0] == 'NOT':
        if expr_words[1] not in term_dict:
            return 0
        res = term_dict['ALL']['f'] - term_dict[expr_words[1]]['f']
    elif '(' in expr:
        # I make sure that the parenthesis are always first and last char of string in this case
        and_clauses = re.split(r' OR (?![^(]*\))', expr[2:-2])
        for and_cl in and_clauses:
            term_list = re.split(r' AND (?![^(]*\))', and_cl)
            min_size = eval_expr_size(term_list[0], term_dict)
            for term in term_list[1:]:
                cur_size = eval_expr_size(term, term_dict)
                if min_size > cur_size:
                    min_size = cur_size
            res += min_size
    return res


def reorder_based_on_size(expr, term_dict):
    """
    Find the smallest term based on posting list length for every subexpression in CNF and put it at the end of the
    CNF so that it can be merged first later on.
    :param expr: boolean expression that will be reordered
    :param term_dict: the dictionary with all terms
    :return: the reordered expression
    """
    and_clauses = re.split(r' OR (?![^(]*\))', expr)
    result = []
    for and_cl in and_clauses:
        term_list = re.split(r' AND (?![^(]*\))', and_cl)
        last_index = len(term_list) - 1
        smallest_element_index = cur_index = 0
        min_size = term_dict['ALL']['f']
        for term in term_list:
            if 'NOT (' in term:
                exp_in_parenthesis = reorder_based_on_size(term[6:-2], term_dict)
                term_list[cur_index] = 'NOT ( ' + exp_in_parenthesis + ' )'
                cur_size = term_dict['ALL']['f'] - eval_expr_size(exp_in_parenthesis, term_dict)
            elif '(' in term:
                term_list[cur_index] = '( ' + reorder_based_on_size(term[2:-2], term_dict) + ' )'
                cur_size = eval_expr_size(term_list[cur_index], term_dict)
            else:
                cur_size = eval_expr_size(term, term_dict)
            if min_size > cur_size:
                min_size = cur_size
                smallest_element_index = cur_index
            cur_index += 1

        # set smallest element at the end so that the rpn can evaluate it first
        if smallest_element_index != last_index:
            tmp = term_list[last_index]
            term_list[last_index] = term_list[smallest_element_index]
            term_list[smallest_element_index] = tmp

        result.append(' AND '.join(term_list))
    return ' OR '.join(result)


def preprocess(expr, term_dict):
    """
    Format the boolean expression and using the methods from above return the reordered expression.
    :param expr: boolean expression that will be reordered
    :param term_dict: the dictionary with all terms
    :return: the final reordered expression
    """

    # format parentheses
    modified_expr = expr.replace('(', '( ').replace(')', ' )')

    # stem the query
    modified_expr = modified_expr.split()
    expr_list = []
    for i in modified_expr:
        term = re.sub(r'[^a-zA-Z0-9]', '', i)
        if i not in all_operators:
            stemmed_term = ps.stem(term.lower())
            expr_list.append(stemmed_term)
        else:
            expr_list.append(i)
    modified_expr = ' '.join(x for x in expr_list)

    # remove unnecessary NOT's
    modified_expr = re.sub(r'(NOT NOT| NOT NOT| NOT NOT |NOT NOT )*', '', modified_expr).strip()

    # sort by size of expressions
    modified_expr = reorder_based_on_size(modified_expr, term_dict)

    # convert expressions like (NOT A AND B) to (B AND NOT A) -> makes computation faster later on
    # NOT (A) AND (B)
    modified_expr = preprocess_andnot(modified_expr)

    return modified_expr
