import sys

from nltk.stem.porter import PorterStemmer
from synonyms import handle_synonyms_unigram

"""
    File name: retrieve_postings.py
    Authors: Svilen Stefanov, Arijit Pramanik, Wang Chin-Hao and Madhav Goel
    Date created: 05/04/2018
    Date last modified: 24/04/2018
    Python Version: 2.7
"""

ps = PorterStemmer()


def positional_intersect(l1, l2):
    """
    Create a list of all elements that are common for both lists.
    :param l1: the first list that is part of the merge
    :param l2: the second list that is part of the merge
    :return: the result after applying the AND merge on the two lists
    """
    l1_len = len(l1.split(' ')) -1 
    l2_len = len(l2.split(' ')) -1
    ans = []

    if l1_len == 0 or l2_len == 0:
        return ans
    elif (l1_len == 1 and l1.split(' ')[0] == '') or (l2_len == 1 and l2.split(' ')[0] == ''):
        return ans

    pl1 = l1.split(' ')
    pl2 = l2.split(' ')

    p1 = p2 = 0
    while p1 < l1_len and p2 < l2_len:
        pl1pos = pl1[p1].split('-')
        pl2pos = pl2[p2].split('-')
        l1_doc_id = pl1pos[0]
        l2_doc_id = pl2pos[0]

        if l1_doc_id == l2_doc_id:

            # pos_ans = []
            pp1 = pp2 = 0

            pl1_len = len(pl1pos[1:])
            pl2_len = len(pl2pos[1:])

            while pp1 < pl1_len and pp2 < pl2_len:

                pos1 = pl1pos[pp1 + 1]
                pos2 = pl2pos[pp2 + 1]
                if (int(pos2) - int(pos1)) == 1:
                    ans.append((l1_doc_id, (pos1, pos2)))
                    pp1 += 1
                    pp2 += 1
                    
                elif int(pos2) > int(pos1) + 1:
                    pp1 += 1
                else:
                    pp2 += 1

                # while len(pos_ans) != 0 and (int(pos_ans[0]) - int(pos1)) != 1:
                #     pos_ans = pos_ans[1:]

                # for ps in pos_ans:
                #     ans.append((l1_doc_id, (pos1, ps)))

                # pp1 += 1

            # ans.append(l1_doc_id)
            p1 += 1
            p2 += 1
        elif l1_doc_id < l2_doc_id:
            p1 += 1
        else:
            p2 += 1
    return ans


def get_postings(term, dictionary, fp_postings):
    """
    This method returns the postings for a specific term from either dict1, dict2 or positional indexing.
    :param term: term of length 1, 2 or 3
    :param dictionary:
    :param fp_postings:
    :return: postings for the given term
    """
    if type(term) != list:
        unstemmed_term_list = term.split()
    else:
        unstemmed_term_list = term
    term_list = [ps.stem(x) for x in unstemmed_term_list]

    # for terms of length 1, freetext case basically
    if len(term_list) == 1:
        term1 = term_list[0]
        if term1 in dictionary:
            # if not in dict 1, call synonyms and check for each of the top synonym if in dict 1
            # else get postings for term from dictionary 1 from postings.txt
            fp_postings.seek(dictionary[term1]['H'])
            postings_string = fp_postings.read(dictionary[term1]['T'] - dictionary[term1]['H'])
            postings_list = postings_string.split()
        else:
            postings_list = handle_synonyms_unigram(unstemmed_term_list, dictionary, fp_postings).split()

        postings_list = [doc_id_position_string.split("-") for doc_id_position_string in postings_list]
        postings_list = [(doc_id_position_list[0], len(doc_id_position_list) - 1) for doc_id_position_list in
                         postings_list]

    elif len(term_list) == 2:
        # for terms of length 2, use the format of double indexing in dict'
        # check if term in dictionary 2
        term1 = term_list[0]
        term2 = term_list[1]

        # check if term is in dictionary
        if term1 in dictionary:
            fp_postings.seek(dictionary[term1]['H'])
            postings1_str = fp_postings.read(dictionary[term1]['T'] - dictionary[term1]['H'])
        # else get its synonym in dictionary from wordnet
        else:
            postings1_str = handle_synonyms_unigram([unstemmed_term_list[0]], dictionary, fp_postings)

        # check if term is in dictionary
        if term2 in dictionary:
            fp_postings.seek(dictionary[term2]['H'])
            postings2_str = fp_postings.read(dictionary[term2]['T'] - dictionary[term2]['H'])
        # else get its synonym in dictionary from wordnet
        else:
            postings2_str = handle_synonyms_unigram([unstemmed_term_list[1]], dictionary, fp_postings)

        # fetch postings list for individual terms  
        postings_string = positional_intersect(postings1_str, postings2_str)
        postings_list = list(set([x[0] for x in postings_string]))
        #remove duplicates
        postings_list = sorted(postings_list)

    # phrasal queries of length 3 handled here
    elif len(term_list) == 3:

        term1 = term_list[0]
        term2 = term_list[1]
        term3 = term_list[2]

        # check if term is in dictionary
        if term1 in dictionary:
            fp_postings.seek(dictionary[term1]['H'])
            postings1_string = fp_postings.read(dictionary[term1]['T'] - dictionary[term1]['H'])
        # else get its synonym in dictionary from wordnet
        else:
            postings1_string = handle_synonyms_unigram([unstemmed_term_list[0]], dictionary, fp_postings)

        # check if term is in dictionary
        if term2 in dictionary:
            fp_postings.seek(dictionary[term2]['H'])
            postings2_string = fp_postings.read(dictionary[term2]['T'] - dictionary[term2]['H'])
        # else get its synonym in dictionary from wordnet
        else:
            postings2_string = handle_synonyms_unigram([unstemmed_term_list[1]], dictionary, fp_postings)

        # check if term is in dictionary
        if term3 in dictionary:
            fp_postings.seek(dictionary[term3]['H'])
            postings3_string = fp_postings.read(dictionary[term3]['T'] - dictionary[term3]['H'])
        # else get its synonym in dictionary from wordnet
        else:
            postings3_string = handle_synonyms_unigram([unstemmed_term_list[2]], dictionary, fp_postings)

        # fetch postings list for individual terms       
        postings12_list = positional_intersect(postings1_string, postings2_string)
        postings23_list = positional_intersect(postings2_string, postings3_string)
        final_postings = []
        for tup1 in postings12_list:
            for tup2 in postings23_list:
                if tup1[0] == tup2[0] and tup1[1][1] == tup2[1][0]:
                    final_postings.append(tup1[0])

        # remove duplicates
        postings_list = list(set(final_postings))
        postings_list = sorted(postings_list)

    else:
        print "ERROR: phrase contains more than 3 terms"
        sys.exit(2)
    # if successfully reaches here without error, return fetched postings list

    postings_list_tuple = []
    # generatte output format to be sent back in
    for e in postings_list:
        if type(e) == tuple:
            postings_list_tuple.append((e[0], e[1]))
        else:
            postings_list_tuple.append((e, -1))

    return postings_list_tuple
