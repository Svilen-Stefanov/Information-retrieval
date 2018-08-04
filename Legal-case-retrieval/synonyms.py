import re
from nltk.corpus import wordnet

from nltk.stem.porter import PorterStemmer

"""
    File name: synonyms.py
    Authors: Svilen Stefanov, Arijit Pramanik, Wang Chin-Hao and Madhav Goel
    Date created: 05/04/2018
    Date last modified: 22/04/2018
    Python Version: 2.7
"""

ps = PorterStemmer()

synonyms_switch = True

def get_synonyms(term):
    """
    This method returns the synonyms of a given term
    :param term: a single word
    :return: all synonyms of the term
    """
    term_list = term.split()
    if len(term_list) > 1:
        print "ERROR: Passing more than one word to get_synonyms"
        return -1

    # get synonyms
    syns_word = wordnet.synsets(term)
    synonyms = []
    for syn in syns_word:
        for l in syn.lemmas():
            if l.name() not in synonyms:
                synonyms.append(l.name())

    if synonyms_switch == True:
        return synonyms
    else:
        return []

def handle_synonyms_unigram(term_list, dictionary, fp_postings):
    all_synonyms = ''
    for i in term_list:
        synonyms = get_synonyms(i)
        synonyms = [ps.stem((re.sub(r'[^a-zA-Z0-9]', '', str(x))).lower()) for x in synonyms]
        new_term = ps.stem((re.sub(r'[^a-zA-Z0-9]', '', str(i))).lower())
        synonyms = [x for x in synonyms if x in dictionary]
        for syn in synonyms:
            if(syn == new_term):
                continue
            else:
                fp_postings.seek(dictionary[syn]['H'])
                postings_string = fp_postings.read(dictionary[syn]['T'] - dictionary[syn]['H'])
                all_synonyms += ' ' + postings_string
                break
    if synonyms_switch == True:
        return all_synonyms.strip()
    else:
        return ''
