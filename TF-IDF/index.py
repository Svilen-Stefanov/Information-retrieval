#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import getopt
import json
import os
import math
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer

"""
    File name: index.py
    Authors: Svilen Stefanov
    Date created: 12/02/2018
    Date last modified: 24/03/2018
    Python Version: 2.7
"""

doc_words = dict()

# dictionary with the terms as keys and postings as values
term_dict = dict()

"""
The dictionary that is going to be saved in dictionary.txt in JSON format.
Contain all terms as keys and their frequencies, heads and tails as values
for finding the right positions of the terms postings in the postings.txt file.
It also contains the collection size with key "N" needed for the idf computation in the search file.
"""
term_count_dict = dict()

# nltk stemmer for stemming of the terms before inserting them in the dictionary
ps = PorterStemmer()

# the size of the training data set
collection_size = 0

test = True


def read_files(input_dir):
    """
    Read from all the documents and build the term dictionary
    :param input_dir: the path of the directory containing the training data set
                        (the directory should contain all documents that should be part of the training)
    :return: None
    """
    global collection_size
    for filename in os.listdir(input_dir):
        whole_filename = input_dir + filename
        filename_to_int = int(filename)
        with open(whole_filename, 'r') as f:
            sentence = f.read().replace('\n', ' ')
            build_term_dict(filename_to_int, sentence)
        collection_size += 1


def build_term_dict(doc_id, doc_string):
    """
    Tokenize the doc string into multiple terms, build the term dictionary with terms as keys
    and list of distinct doc IDs as values.
    :param doc_id: a document ID from the Reuters training data set
    :param doc_string: the text of document with the given doc_id
    :return: None
    """
    sentences = sent_tokenize(doc_string)
    for sent in sentences:
        words = word_tokenize(sent)
        for word in words:
            term = re.sub(r'[^a-zA-Z0-9]', '', str(word))
            term = ps.stem(term.lower())
            if len(term) != 0:
                if term in term_dict:
                    if doc_id in term_dict[term]:
                        term_dict[term][doc_id] += 1
                    else:
                        term_dict[term][doc_id] = 1
                else:
                    # saves the term with the docID and an initial term frequency for the document
                    term_dict[term] = {doc_id: 1}
                if doc_id in doc_words:
                    if term in doc_words[doc_id]:
                        doc_words[doc_id][term] += 1
                    else:
                        doc_words[doc_id][term] = 1
                else:
                    doc_words[doc_id] = {term: 1}



def change_dict_representation():
    """
    Change the term_dict data structure in the form of 'term': [(docID_1, tf_1), ..., (docID_N, tf_N)]
    :return: dictionary with the terms as keys and postings with term frequencies as values
    """
    new_term_dict = dict()
    for key in term_dict.keys():
        new_term_dict[key] = sorted(term_dict[key].items(), key=lambda x: x[0])
    return new_term_dict


def write_output():
    """
    Write the term dictionary and the posting lists to 2 distinct output files.
    :return: None
    """
    with open(output_file_postings, 'w') as out_postings:
        doc_norm = dict()
        for key, val in term_dict.iteritems():
            head = out_postings.tell()
            freq = len(val)
            posting = str()
            for t in val:
                values = [1 + math.log(i, 10) for i in doc_words[t[0]].values()]
                norm_val = math.sqrt(sum(i ** 2 for i in values))
                doc_norm[t[0]] = norm_val
                posting += str(t[0]) + '-' + str(t[1]) + ' '
            out_postings.write(posting)
            tail = out_postings.tell()
            term_count_dict[key] = {'h': head, 't': tail, 'f': freq}

    with open(output_file_dictionary, 'w') as out_dict:
        term_count_dict['N'] = collection_size
        term_count_dict['DOC_NORM'] = doc_norm
        json.dump(term_count_dict, out_dict)


def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # input directory
        input_directory = a
    elif o == '-d':  # dictionary file
        output_file_dictionary = a
    elif o == '-p':  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory is None or output_file_postings is None or output_file_dictionary is None:
    usage()
    sys.exit(2)


if __name__ == "__main__":
    read_files(input_directory)
    term_dict = change_dict_representation()
    write_output()
