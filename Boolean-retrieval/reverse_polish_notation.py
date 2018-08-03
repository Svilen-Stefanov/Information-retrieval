from list_operations import or_operation, and_operation, not_operation, and_not_operation

"""
    File name: reverse_polish_notation.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 03/03/2018
    Python Version: 2.7
"""

operators = ["AND", "OR", "NOT", "ANDNOT"]


def rpn(expr):
    """
    Reverse Polish Notation (Shunting-yard) algorithm
    :return: the expression in Reverse Polish Notation (postfix)
    """
    rpn_list = []
    op_list = []
    new_expr = expr.replace('AND NOT', 'ANDNOT')
    query_elements = new_expr.split()
    for el in query_elements:
        if el in operators:
            if el == 'OR' and len(op_list) > 0 and op_list[-1] != '(':
                rpn_list.append(op_list.pop())
            elif (el == 'AND' or el == 'OR' or el == 'ANDNOT') and len(op_list) > 0 and op_list[-1] == 'ANDNOT':
                rpn_list.append(op_list.pop())
            elif el == 'ANDNOT' and len(op_list) > 0 and op_list[-1] == 'NOT':
                rpn_list.append(op_list.pop())
            op_list.append(el)
        elif el == '(':
            op_list.append(el)
        elif el == ')':
            while len(op_list) > 0 and op_list[-1] != '(':
                rpn_list.append(op_list.pop())
            op_list.pop()
        else:
            rpn_list.append(el)

    while op_list:
        rpn_list.append(op_list.pop())

    return rpn_list


def compute_expr(operator, l1, l_all=None, l2=None):
    """
    Depending on the operator, this method decides how to handle (merge) the lists.
    It's possible that there is only one list provided if the operator is NOT.
    :param operator: one of the boolean operators (OR, AND, NOT or AND NOT) as a string
    :param l1: the first list as operand to be merged (this parameter is a MUST)
    :param l2: the second list as operand to be merged (optional for the case of NOT)
    :return: the result after applying the operator on the parameters
    """

    if operator == 'OR':
        ans = or_operation(l1, l2)
    elif operator == 'AND':
        ans = and_operation(l1, l2)
    elif operator == 'NOT':
        ans = not_operation(l1, l_all)
    else:   # operator == ANDNOT
        ans = and_not_operation(l1, l2, l_all)
    return ans


def get_postings(term, term_dict, postings_file):
    """
    Retrieve the posting list for a given term. If the term is not in the dictionary, return an empty list.
    :param term: the term which posting list should be returned
    :param term_dict: the dictionary of all terms
    :param postings_file: the name of the file that contains all postings
    :return: [] - if not in the dictionary
            otherwise return the posting list for the given term
    """
    if term not in term_dict:
        return []
    value = term_dict[term]
    h = value['h']
    t = value['t']
    with open(postings_file, 'r') as postings_f:
        postings_f.seek(h, 0)
        postings = postings_f.read(t-h)
        postings_list = postings.split()
        postings_list_int = []
        for elem in postings_list:
            elem_list = elem.split('-')
            doc_id = int(elem_list[0])
            skip_pointer = int(elem_list[1])
            postings_list_int.append((doc_id, skip_pointer))
        postings_f.close()
    return postings_list_int


def compute_rpn(expr, term_dict, postings_file):
    """
    Compute the result of the query.
    :param expr: the boolean expression after the preprocessing phase
    :param term_dict: the dictionary of all terms
    :param postings_file: the name of the file that contains all postings
    :return: the result after processing the query
    """
    l_all = term_dict['ALL']['a']
    query_elements = rpn(expr)
    doc_ids = []
    while query_elements:
        el = query_elements.pop(0)
        if el in operators:
            term2 = doc_ids.pop()
            if type(term2) is list:
                l2 = term2
            else:
                l2 = get_postings(term2, term_dict, postings_file)
            # check for NOT alone (example NOT A)
            if el == 'NOT':
                doc_ids.append(compute_expr(el, l2, l_all))
            else:
                term1 = doc_ids.pop()
                if type(term1) is list:
                    l1 = term1
                else:
                    l1 = get_postings(term1, term_dict, postings_file)
                doc_ids.append(compute_expr(el, l1, l_all, l2))
        else:
            doc_ids.append(el)

    ans = doc_ids[0]
    if type(ans) is not list:
        ans_tuple = get_postings(ans, term_dict, postings_file)
        ans = [el[0] for el in ans_tuple]
    return ans
