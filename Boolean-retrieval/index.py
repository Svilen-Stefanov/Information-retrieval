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
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 08/03/2018
    Python Version: 2.7
"""

# dictionary with the terms as keys and postings as values
term_dict = dict()

"""
The dictionary that is going to be saved in dictionary.txt in JSON format.
Contain all terms as keys and their frequencies, heads and tails as values
for finding the right positions of the terms postings in the postings.txt file.
It also contains all postings with key "ALL" needed for NOT computation in the search file.
"""
term_count_dict = dict()

# a list with all encountered document IDs in the given training data set (in this case Reuters)
all_doc_ids = []

# nltk stemmer for stemming of the terms before inserting them in the dictionary
ps = PorterStemmer()


def read_files(input_dir):
    """
    Read from all the documents and build the term dictionary
    :param input_dir: the path of the directory containing the training data set
                        (the directory should contain all documents that should be part of the training)
    :return: None
    """
    for filename in os.listdir(input_dir):
        whole_filename = input_dir + filename
        filename_to_int = int(filename)
        all_doc_ids.append(filename_to_int)
        with open(whole_filename, 'r') as f:
            sentence = f.read().replace('\n', '')
            build_term_dict(filename_to_int, sentence)


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
                    if doc_id not in term_dict[term]:
                        term_dict[term].append(doc_id)
                else:
                    term_dict[term] = [doc_id]


def sort_term_lists():
    """
    Sort the list of documents for each term inside the dictionary.
    :return: None
    """
    for value in term_dict.values():
        value.sort()


def build_term_count_dict(term='', head=0, tail=0, freq=0):
    """
    Generate the dictionary with the frequency count of the terms in the right format for the dictionary file.
    :type term: the term to be inserted in the dictionary
    :return: None
    """
    term_count_dict[term] = {'h': head, 't': tail, 'f': freq}


def write_output():
    """
    Write the term dictionary and the posting lists to 2 distinct output files.
    :return: None
    """
    with open(output_file_postings, 'w') as out_postings:
        for key, val in term_dict.iteritems():
            head = out_postings.tell()
            freq = len(val)
            space = int(math.sqrt(freq))
            posting = []
            for i, doc_id in enumerate(val):
                # the last element does not have a skip pointer
                if space > 1 and i % space == 0 and i + space < freq:
                    posting.append(str(doc_id) + '-' + str(i+space))
                else:
                    posting.append(str(doc_id) + '-' + '0')
            posting_str = " ".join(str(doc_id) for doc_id in posting)
            out_postings.write(posting_str)
            out_postings.write(" ")
            tail = out_postings.tell()
            build_term_count_dict(key, head, tail, freq)

    with open(output_file_dictionary, 'w') as out_dict:
        all_doc_ids.sort()
        term_count_dict['ALL'] = {'f': len(all_doc_ids), 'a': all_doc_ids }
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
    sort_term_lists()
    write_output()
