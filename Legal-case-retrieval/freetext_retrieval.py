import re
from retrieve_postings import get_postings
from nltk.stem.porter import PorterStemmer
import math
from operator import mul
from synonyms import get_synonyms

"""
    File name: freetext_retrieval.py
    Authors: Svilen Stefanov, Arijit Pramanik, Wang Chin-Hao and Madhav Goel
    Date created: 05/04/2018
    Date last modified: 24/04/2018
    Python Version: 2.7
"""

ps = PorterStemmer()

# toggle Rocchio usage on and off using this
rocchio = False
# toggle thesaurus usage on and off using this
thesaurus_switch = False


def tf_val_for_term(original_term, occurrences, dictionary):
    """
    In this method a tf-idf vector for the term is build as in HW3.
    Need to handle synonyms for the terms that are not part of dict1 or dict 2.
    :param original_term:
    :param occurrences:
    :param dictionary:
    :return: the tf*itf for the term
    """
    term = ps.stem(original_term)
    if term not in dictionary:
        stemmed_term = term
        synonyms = get_synonyms(original_term)
        for synonym in synonyms:
            stemmed_synonym = ps.stem(synonym)
            # get the first synonym that exists in dictionary
            if stemmed_synonym in dictionary:
                term = stemmed_synonym
                break
        # all synonyms don't exist in dictionary
        if stemmed_term == term:
            return (0, None)

    log_tf = 1.0 + math.log10(occurrences) if occurrences != 0 else 0.0
    log_idf = math.log10(float(dictionary['N'])/float(dictionary[term]['F']))
    return log_tf * log_idf, [term]


def get_cosine_similarity(query_vec, norm_doc_vects, flag):
    """
    compute the cosine similarity between query_Vec and each document
    and return the document id's and their score pairs in sorted order
    of score if flag is true.
    """
    res_vect = []
    sorted_rel_docs = sorted(norm_doc_vects.keys())

    for doc in sorted_rel_docs:
        doc_vec = norm_doc_vects[doc]
        similarity = sum(map(mul, query_vec, doc_vec))
        res_vect.append((doc, round(similarity, 15)))
    # python sort method is stable and thus guarantee that docIDs with the same similarities
    # will remain in increasing order since they were inserted in the res_vect list in that order
    if flag == True:
        res_vect.sort(key=lambda x: x[1], reverse=True)
    return res_vect


def get_expanded_query(query_vec, norm_doc_vects, res_vect):
    """
    method to expand the query using rocchio formula.
    """
    rf_threshold = 0.01
    num_total = len(norm_doc_vects)
    num_relevant = int(math.ceil(rf_threshold * num_total))
    num_irrelevant = num_total - num_relevant
    centroid_relevant = [0.0 for i in range(len(query_vec))]
    centroid_irrelevant = [0.0 for i in range(len(query_vec))]

    alpha = 1
    beta = 0.75
    gamma = 0.15
    
    # compute centroid of relevant documents
    for i in range(num_relevant):
        doc_id_to_get = res_vect[i][0]
        doc_vec = norm_doc_vects[doc_id_to_get]
        centroid_relevant = [x + y for x, y in zip(centroid_relevant, doc_vec)]
        
    # compute centroid of irrelevant documents
    for i in range(num_relevant, num_total):
        doc_id_to_get = res_vect[i][0]
        doc_vec = norm_doc_vects[doc_id_to_get]
        centroid_irrelevant = [x + y for x, y in zip(centroid_irrelevant, doc_vec)]

    expanded_query_vec = []

    for x, y, z in zip(query_vec, centroid_relevant, centroid_irrelevant):
        a = alpha * x
        b = 0.0 if num_relevant == 0 else beta * y / num_relevant
        c = 0.0 if num_irrelevant == 0 else gamma * z / num_irrelevant
        expanded_query_vec.append(a + b + c)
    return expanded_query_vec


def freetext_retrieve(query, dictionary, thesaurus, fp_postings, flag):
    """
    The main method for the free text retrieval.
    :param query: a list of query terms
    :param dictionary:
    :param thesaurus:
    :param fp_postings:
    :return: return the result of all relevant docIDs in decreasing order of priority using a heap (heapq module)
    """
    query_vec = []
    doc_vecs = {}
    stemmed_query_dict = {}
    for term in query:
        original_term = term
        term = re.sub(r'[^a-zA-Z0-9]', '', str(term))
        term = ps.stem(term.lower())
        if term not in stemmed_query_dict:
            stemmed_query_dict[term] = []
        stemmed_query_dict[term].append(original_term)

        if thesaurus_switch == True:
            if term in thesaurus:
                thesaurus_list = thesaurus[term]
                # add each t in thesaurus list to the stemmed_query_dict
                for t in thesaurus_list:
                    if t not in stemmed_query_dict:
                        stemmed_query_dict[t] = []
                    stemmed_query_dict[t].append(t)
    # remove words appearing more than once because we count them in the t_f computation below
    stemmed_query_list = stemmed_query_dict.keys()

    for index, term in enumerate(stemmed_query_list):
        term_list = term.split()
        # don't check if term is in dictionary, because it will try to find synonyms in build_vec methods
        if len(term_list) == 1:
            original_term = stemmed_query_dict[term][0]
            val, new_term_list = tf_val_for_term(original_term, len(stemmed_query_dict[term]), dictionary)
            if new_term_list is not None:
                query_vec.append(val)
                stemmed_query_list[index] = new_term_list[0]
        else:
            print "Incorrect input"
            break

        if new_term_list is None:
            continue

        cur_docs = get_postings(new_term_list, dictionary, fp_postings)
        cur_docs = [(int(x[0]), x[1]) for x in cur_docs]
        for (doc, tf) in cur_docs:
            norm = dictionary['DOC_NORM'][str(doc)]
            t_f = 1 + math.log(tf, 10) if tf != 0 else 0.0
            val = t_f / norm
            new_term_string = new_term_list[0]
            if doc in doc_vecs:
                doc_vecs[doc][new_term_string] = val
            else:
                doc_vecs[doc] = {new_term_string: val}

    # Fill all document vectors with 0 for the query words they don't contain
    norm_doc_vects = {}
    for word in stemmed_query_list:
        if word in dictionary:
            for doc, dic in doc_vecs.iteritems():
                if word in dic:
                    # if doc in the dict, append the next normalized value
                    if doc in norm_doc_vects:
                        norm_doc_vects[doc].append(dic[word])
                    # if doc not in the dict of documents
                    else:
                        norm_doc_vects[doc] = [dic[word]]
                # if the word does not appear in the document
                else:
                    if doc in norm_doc_vects:
                        norm_doc_vects[doc].append(0)
                    else:
                        norm_doc_vects[doc] = [0]
                        
    # check if rocchio flag is turned on
    if not rocchio:
        res_vect = get_cosine_similarity(query_vec, norm_doc_vects, flag)
    else:
        # if on, first get expanded query and then do cosine similarity calculation again
        res_vect = get_cosine_similarity(query_vec, norm_doc_vects, True)
        expanded_query_vec = get_expanded_query(query_vec, norm_doc_vects, res_vect)
        res_vect = get_cosine_similarity(expanded_query_vec, norm_doc_vects, flag)

    return res_vect
