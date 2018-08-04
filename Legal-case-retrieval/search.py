import json
import sys
import getopt
import re
from datetime import datetime

import boolean_retrieval as br
import freetext_retrieval as fr

# params:
# -d posdict.txt -p pospostings.txt -q queries.txt -o output.txt

"""
    File name: search.py
    Authors: Svilen Stefanov, Arijit Pramanik, Wang Chin-Hao and Madhav Goel
    Date created: 05/04/2018
    Date last modified: 25/04/2018
    Python Version: 2.7
"""

term_dict = {}

# toggle the metadata usage on and off using this
zones_metadata_switch = False

# list of all courts and their corresponding relevance values
court_metadata = {"UK Military Court":0.5, 
                    "NSW Industrial Relations Commission":0.5,
                    "NSW Local Court":0.25, 
                    "UK House of Lords":1.0, 
                    "NSW Court of Criminal Appeal":0.75, 
                    "NSW Supreme Court":1.5,
                    "NSW Land and Environment Court":0.5,
                    "Industrial Relations Court of Australia":0.25,
                    "NSW Court of Appeal":0.6, 
                    "SG Family Court":0.5,
                    "SG Privy Council":0.2, 
                    "NSW District Court":0.5,
                    "NSW Administrative Decisions Tribunal (Trial)":0.2, 
                    "NSW Industrial Court":0.2, 
                    "High Court of Australia":0.8,
                    "Singapore International Commercial Court":0.7, 
                    "CA Supreme Court":1.0, 
                    "SG High Court": 0.75, 
                    "SG District Court":0.5, 
                    "NSW Children's Court":0.5, 
                    "UK Supreme Court": 1.5, 
                    "SG Magistrates' Court": 0.5,
                    "UK High Court": 0.75, 
                    "HK High Court": 0.75, 
                    "NSW Medical Tribunal": 0.25,
                    "Federal Court of Australia": 1.0,
                    "HK Court of First Instance": 0.5,
                    "UK Court of Appeal": 1.0,
                    "NSW Civil and Administrative Tribunal": 0.25,
                    "SG Court of Appeal": 0.8, 
                    "UK Crown Court": 0.7}


def get_date_factor(date_string):
    """
    This function gives a relevance value for a documents date-posted,
    assuming more recent documents are more relevant
    """
    split_string = date_string.split(" ")
    date = split_string[0]
    time = split_string[1]

    date = date.split("-")
    year = date[0]
    month = date[1]
    day = date[2]

    year = int(year)
    curr_year = int(datetime.now().year)

    # check how many years old the document is
    if(year >= curr_year - 5):
        return 1.5
    elif(year >= curr_year - 10):
        return 1.0
    elif(year >= curr_year - 20):
        return 0.65
    elif(year >= curr_year - 40):
        return 0.40
    else:
        return 0.20

def load_dict_file(dict_file):
    """
    function to load the word dictionary file
    """
    with open(dict_file, 'r') as dictionary_f:
        return json.load(dictionary_f)

def load_meta_dict_file(dict_file):
    """
    function to load the metadata dictionary file
    """
    with open(dict_file, 'r') as dictionary_f:
        return json.load(dictionary_f)

def load_thesaurus(dict_file):
    """
    function to load the thesaurus file
    """
    with open(dict_file, 'r') as thesau_f:
        return json.load(thesau_f)

def zones_metadata(doc_id_score_list, dictionary):
    """
    function to perform update of the scores of the documents and 
    thus reorder the output. It uses the court name and date posted metadata 
    to reassign the document scores.
    """
    res = []
    # relevance factor for court name and date posted
    court_name_factor = 0.6
    date_factor = 0.4
    for (doc_id, score) in doc_id_score_list:
        court_name = dictionary['court'][str(doc_id)]
        court_score = court_metadata.get(court_name, 0)

        date = dictionary['date_posted'][str(doc_id)]
        date_score = get_date_factor(date)

        final_score_factor = court_name_factor*court_score + date_factor*date_score

        res.append((doc_id, score*final_score_factor))
    res.sort(key=lambda x: x[1], reverse=True)
    return res

# taking command line parameters here
def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file is None or postings_file is None or file_of_queries is None or file_of_output is None :
    usage()
    sys.exit(2)


def main():
    # load and open dictionaries and postings here
    fp_postings = open(postings_file, 'r')
    term_dictionary = load_dict_file(dictionary_file)
    metadata_dictionary = load_meta_dict_file("metadict.txt")
    thesaurus = load_thesaurus('thesaurus.txt')
    
    with open(file_of_queries, 'r') as fp:
        query = fp.readlines()
        
        # for empty query files
        if len(query) == 0:
            res = []
        # handler for boolean queries
        elif "AND" in query[0] or "\"" in query[0][0].strip():
            # call boolean retrieval -> e.g boolRetriev(query.split('AND'))
            res = br.bool_retrieve(query[0].split("AND"), term_dictionary, fp_postings)
            query[0] = " ".join(query[0].split("AND"))

            separate_terms = re.findall(r'(?P<q_marks>\"(.*?)\")|(?P<s_word>\w+)', query[0])
            terms = []
            for b, q, s in separate_terms:
                if b:
                    terms.append(b.replace('"', ''))
                elif q:
                    terms.append(q)
                elif s:
                    terms.append(s)

            # in case the above query returns nothing, we make another attempt to retrieve only the phrasal part, 
            # since phrases are more important compared to freetext retrieval
            phrasal_term = []
            if len(res) == 0:
                for term in terms:
                    if ' ' in term:
                        phrasal_term.append(term)
                res = br.bool_retrieve(phrasal_term, term_dictionary, fp_postings)
            
            # convert completely to freetext
            final_term_list = []
            for ele in terms:
                if len(ele) > 1:
                    eles = ele.split()
                    final_term_list.extend(eles)

            # append output of fully freetext form of query to boolean output
            res1 = fr.freetext_retrieve(final_term_list, term_dictionary, thesaurus, fp_postings, True)
            res1 = [str(x[0]) for x in res1]

            # remove duplicates
            for x in res1:
                if x not in res:
                    res.append(x)

            # res.extend(res1)
            # if zones_metadata_switch == True:
            #     res1 = zones_metadata(res1, metadata_dictionary)

        else:
            # call freetext retrieval -> e.g freetextRetriev(query.split(' '))
            separate_terms = re.findall(r'(?P<q_marks>\"(.*?)\")|(?P<s_word>\w+)', query[0])
            terms = []
            for b, q, s in separate_terms:
                if b:
                    terms.append(b.replace('"', ''))
                elif q:
                    terms.append(q)
                elif s:
                    terms.append(s)

            # call handler of freetext queries here
            res = fr.freetext_retrieve(terms, term_dictionary, thesaurus, fp_postings, True)
            if zones_metadata_switch == True:
                res = zones_metadata(res, metadata_dictionary)
            res = [x[0] for x in res]

    # output the result to a file
    with open(file_of_output, 'w') as out:
        out_str = str()
        out_str += ' '.join(str(el) for el in res) + '\n'
        out.write(out_str[:-1])  # removes the last '\n'

if __name__ == "__main__":
    main()
