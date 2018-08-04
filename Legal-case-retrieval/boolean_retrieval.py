from retrieve_postings import get_postings
import re
from nltk.stem.porter import PorterStemmer

"""
    File name: boolean_retrieval.py
    Authors: Svilen Stefanov, Arijit Pramanik, Wang Chin-Hao and Madhav Goel
    Date created: 05/04/2018
    Date last modified: 18/04/2018
    Python Version: 2.7
"""

def merge_lists(l1, l2):
    """
    Create a list of all elements that are common for both lists.
    :param l1: the first list that is part of the merge
    :param l2: the second list that is part of the merge
    :return: the result after applying the AND merge on the two lists
    """
    l1_len = len(l1)
    l2_len = len(l2)
    ans = []
    if l1_len == 0 or l2_len == 0:
        return ans
    p1 = p2 = 0
    while p1 < l1_len and p2 < l2_len:
        l1_doc_id = l1[p1]
        l2_doc_id = l2[p2]
        
        # print l1_doc_id, l2_doc_id
        if l1_doc_id == l2_doc_id:
            ans.append(l1_doc_id)
            p1 += 1
            p2 += 1
        elif l1_doc_id < l2_doc_id:
            p1 += 1
        else:
            p2 += 1
    # print ans
    return ans


def order_by_size(term_list, dictionary, fp_postings):
    """
    Evaluates the size of the posting list of a given expression (if existing in the term dictionary).
    :param term_list:
    :param dictionary:
    :param fp_postings:
    :return: 0 - if not in the term dictionary
             document frequency of the term - if the term is present in the dictionary
    """
    smallest_index = 0
    smallest_f = 18000
    cur_index = 0
    for term in term_list:
        term = term.strip()
        expr_words = term.split()
        if len(expr_words) == 1:
            if term not in dictionary:
                res_list = get_postings(term, dictionary, fp_postings)
                res = len(res_list)
            else:
                res = dictionary[term]['f']
        elif len(expr_words) == 2 or len(expr_words) == 3:
            res_list = get_postings(expr_words, dictionary, fp_postings)
            res = len(res_list)
        else:
            print "Incorrect input"
            return 0
        # used to sort the boolean query by size for optimization purposes
        if res < smallest_f:
            smallest_index = cur_index
        cur_index += 1
    res_list = term_list
    if smallest_index != 0:
        tmp = res_list[smallest_index]
        res_list[smallest_index] = res_list[0]
        res_list[0] = tmp
    return res_list


def bool_retrieve(query, dictionary, fp_postings):
    """
    The main method for the boolean retrieval.
    The smallest sized list of postings should be merged first (orderBySize)
    :param query: a list of query terms
    :param dictionary:
    :param fp_postings:
    :return: return the result of all relevant docIDs
    """
    res = []
    for index, term in enumerate(query):
        term = re.sub(r'\"', '', term)
        term_list = term.strip().split()
        for i in range(len(term_list)):
            term = term_list[i]
            term = term.strip()
            term = re.sub(r'[^a-zA-Z0-9]', '', str(term))
            term = term.lower()
            term_list[i] = term

        term_postings = get_postings(term_list, dictionary, fp_postings)
        term_postings = [x[0] for x in term_postings]
        if index == 0:
            res = term_postings
        else:
            res = merge_lists(res, term_postings)
        # print res
    return res
