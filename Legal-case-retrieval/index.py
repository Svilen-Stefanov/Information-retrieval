import csv
import re
import sys
import getopt
import json
import math

import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

"""
    File name: index.py
    Authors: Svilen Stefanov, Arijit Pramanik, Wang Chin-Hao and Madhav Goel
    Date created: 05/04/2018
    Date last modified: 21/04/2018
    Python Version: 2.7
"""

reload(sys)
sys.setdefaultencoding('ISO-8859-1')

# dictionaries for words and metadata
positional_dict = {}
positional_count_dict = {}
meta_dict = {"title":{}, "date_posted":{}, "court":{}}

# cache for stemmer
stemmer_dict = {}

# thesaurus dictionary
thesaurus = {}
positional_list = []

all_doc_ids = []
ps = PorterStemmer()

# dictionaries for
doc_words = {}
doc_norm_words = {}
doc_matrix = []
SIM_BOUND = 8
THRESHOLD = 6

# list of stop words
stop = set(stopwords.words('english'))

# the size of the training data set
collection_size = 0

csv.field_size_limit(sys.maxsize)

# params:
# -i dataset.csv -d posdict.txt -p pospostings.txt
# -i output/ -d posdict.txt -p pospostings.txt

output_meta_dict = "tmpmetadict.txt"

def usage():
    print "usage: " + sys.argv[0] + " -i dataset_file -d postional-dictionary-file -p positional-postings-file"


dataset_file = output_pos_dict = output_pos_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # dataset directory
        dataset_file = a
    elif o == '-d':  # positional dictionary file
        output_pos_dict = a
    elif o == '-p':  # positional postings file
        output_pos_postings = a
    else:
        assert False, "unhandled option"

if dataset_file is None or output_pos_dict is None or output_pos_postings is None:
    usage()
    sys.exit(2)


def read_data_files_test(input_dir):
    """
    Read from all the documents and builds the term dictionary
    :param input_dir: the path of the directory containing the training data set
    :return: None
    """
    global collection_size
    count = 0
    with open(input_dir, 'rb') as csv_file:
        data_reader = csv.reader(csv_file, delimiter=',', )
        for index, row in enumerate(data_reader):
            if index == 0:
                continue
            if index >= 3:
                break
            doc_id = row[0]
            print count
            count = count + 1
            title = row[1]
            content = row[2]
            date_posted = row[3]
            court = row[4]
            build_positional_index_dict(doc_id, content)
            build_meta_dict(doc_id, title, content, date_posted, court)
            collection_size += 1


def read_data_files(input_dir):
    """
    Read from all the documents and builds the term dictionary
    :param input_dir: the path of the directory containing the training data set
    :return: None
    """
    global collection_size
    count = 0
    with open(input_dir, 'rb') as csv_file:
        data_reader = csv.reader(csv_file, delimiter=',', )
        for index, row in enumerate(data_reader):
            if index == 0:
                continue
            doc_id = row[0]
            print count
            count = count + 1
            title = row[1]
            content = row[2]
            date_posted = row[3]
            court = row[4]
            build_positional_index_dict(doc_id, content)
            build_meta_dict(doc_id, title, content, date_posted, court)
            collection_size += 1


def build_positional_index_dict(doc_id, doc_string):
    """
    Build a positional index with a single term as key and list of dictionaries with each element having doc ID as key, and the positions in the document as values
    Positions in documents start from 1
    :param doc_id: a document ID from the data set
    :param doc_string: the text of document corresponding to the given doc_id
    :return: None
    """
    global stemmer_dict

    count = 1
    sentences = sent_tokenize(doc_string)

    for sent in sentences:
        words = word_tokenize(sent)
        for word in words:
            term = re.sub(r'[^a-zA-Z0-9]', '', str(word))
            term = term.lower()
            
            # check if stem exists in the cache
            cache = stemmer_dict.get(term, None)
            if cache is not None:
                term = cache
            else:
                stem_res = ps.stem(term)
                stemmer_dict[term] = stem_res
                term = stem_res
            # make sure it's not empty word
            if len(term) != 0:
                if term in positional_dict:
                    if doc_id not in positional_dict[term]:
                        positional_dict[term][doc_id] = [count]
                    else:
                        positional_dict[term][doc_id].append(count)
                else:
                    positional_dict[term] = {}
                    positional_dict[term][doc_id] = [count]

                count += 1
    
                # used to normalization values calculation
                if doc_id in doc_words:
                    if term in doc_words[doc_id]:
                        doc_words[doc_id][term] += 1
                    else:
                        doc_words[doc_id][term] = 1
                else:
                    doc_words[doc_id] = {term : 1}

def transform():
    """
    Helper funcion for building the thesaurus
    """
    for term in positional_dict:
        positional_list.append(term)

def build_thesaurus():
    """
    Building the thesaurus for use in query expansion later on 
    """
    sum = [0.0] * len(doc_words)
    ctr = 0

    for doc_id in doc_words:
        
        doc_norm_words[doc_id] = {}
        for term in doc_words[doc_id]:
            sum[ctr] += doc_words[doc_id][term] ** 2

        for term in doc_words[doc_id]:
            doc_norm_words[doc_id][term] = doc_words[doc_id][term] / math.sqrt(sum[ctr])

        ctr += 1


    for doc_id in doc_norm_words:
        tmp = []
        for term in positional_dict:
            if term in doc_norm_words[doc_id]:
                tmp.append(doc_norm_words[doc_id][term])
            else:
                tmp.append(0.0)
        doc_matrix.append(tmp)

    doc_mat = np.matrix(doc_matrix)
    doc_mat_transpose = doc_mat.transpose()
    co_occurence_mat = np.matmul(doc_mat_transpose, doc_mat)

    for i in range(len(positional_dict)):
        sim_list = sorted(enumerate(co_occurence_mat[i].tolist()[0]), key = lambda x : -x[1])
        sim_terms = [positional_list[k[0]] for k in sim_list]
        sim_terms = [term for term in sim_terms if term not in stop]
        thesaurus[positional_list[i]] = sim_terms[1 : SIM_BOUND]

def write_thesaurus(thes_out_file):
    """
    dump the thesaurus to an output file here
    """
    with open(thes_out_file, 'w') as thes_out_dict:
        json.dump(thesaurus, thes_out_dict)

def build_meta_dict(doc_id, title, content, date_posted, court):
    """
    for each doc id dump the court name, date posted and
    title to the meta data dictionary
    """
    meta_dict['title'][doc_id] = title
    meta_dict['date_posted'][doc_id] = date_posted
    meta_dict['court'][doc_id] = court


def build_positional_index_count_dict(positional_count_dict ,term='', head=0, tail=0, freq=0):
    """
    Generate the positional index with the frequency count of the terms in the right format for the dictionary file.
    :type term: the term to be inserted in the dictionary
    :param head:
    :param tail:
    :param freq:
    :return: None
    """
    positional_count_dict[term] = {'H': head, 'T': tail, 'F': freq}


def write_positional_output(positional_dict, positional_count_dict, output_file_dictionary, output_file_postings):
    """
    Write the positional index to output files.
    :param positional_dict:
    :param positional_count_dict:
    :param output_file_dictionary:
    :param output_file_postings:
    :return: None
    """
    doc_norm = {}

    with open(output_file_postings, 'w') as out_postings:
        for term, doc_id_dict in positional_dict.iteritems():
            doc_id_list = doc_id_dict.keys()
            doc_id_list.sort()

            posting = []
            for doc_id in doc_id_list:
                out_str = str(doc_id) + '-'
                pos_list = doc_id_dict[doc_id]
                pos_list.sort()
                hold = 0
                for pos_val in pos_list:
                    if hold == 0:
                        out_str += str(pos_val)
                        hold = 1
                    else:
                        out_str += '-' + str(pos_val)
                posting.append(out_str)

                # compute document normalization values here
                if doc_id not in doc_norm:
                    values = [1 + math.log(i, 10) for i in doc_words[doc_id].values()]
                    norm_val = math.sqrt(sum(i ** 2 for i in values))
                    doc_norm[doc_id] = norm_val

            posting_str = " ".join(str(e) for e in posting) + " "

            # dump postings to output file
            head = out_postings.tell()
            out_postings.write(posting_str)
            freq = len(doc_id_list)
            tail = out_postings.tell()

            # build pisitionl index count dictionary
            build_positional_index_count_dict(positional_count_dict, term, head, tail, freq)

    with open(output_file_dictionary, 'w') as out_dict:
        # dump to the word dictionary file
        positional_count_dict['DOC_NORM'] = doc_norm #normalization values for documents
        positional_count_dict['N'] = collection_size # total number of documents
        json.dump(positional_count_dict, out_dict)


def write_meta_output(meta_dict, output_file_dictionary):
    """
    Dump the metadata to meta data dictiionary file:param positional_dict:
    :param meta_dict:
    :param output_file_dictionary:
    :return: None
    """
    with open(output_file_dictionary, 'w') as out_dict:
        json.dump(meta_dict, out_dict)


if __name__ == "__main__":
    read_data_files(dataset_file) # build the dictionaries
    write_positional_output(positional_dict, positional_count_dict, output_pos_dict, output_pos_postings) # output posiional dictionary and postings to files
    write_meta_output(meta_dict, output_meta_dict) # output metadat dictionary and postings to files
    transform()
    build_thesaurus() #generate the thesaurus
    write_thesaurus('thesaurus.txt') # dump thesaurus to output file
