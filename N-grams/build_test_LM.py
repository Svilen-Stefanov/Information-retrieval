"""
    File name: build_test_LM.py
    Author: Svilen Stefanov
    Date created: 28/01/2018
    Date last modified: 07/02/2018
    Python Version: 2.7
"""

#!/usr/bin/python
import re
import math
from nltk.util import ngrams
import sys
import getopt

# count dictionaries - used to count the occurrence of a 4-gram in a specific language with add 1 smoothing
indonesian_token_tuple_count = dict()
malaysian_token_tuple_count = dict()
tamil_token_tuple_count = dict()
# count the number of all 4-gram only to be found in the corresponding language
count_words_distinct_dict = {"indonesian": 0, "malaysian": 0, "tamil": 0}
all_count_dict = [("indonesian", indonesian_token_tuple_count), ("malaysian", malaysian_token_tuple_count),
                  ("tamil", tamil_token_tuple_count)]

# words in the training data that I want to remove, because they are not part of the corresponding language
words_to_remove = ["skin", "success", "acne", "medication", "january", "february", "march", "april", "may", "june", "july", "august", "september",
                   "october", "november", "december", "times", "video", "gossipboy", "philip", "alexios",
                   "kaisar", "isaac", "windows", "mac", "os", "los", "angeles", "silicon", "valley", "saint", "lucy", "xp", "bangor", "city", "football", "league", "trophy",
                   "runner", "up", "icf", " helen", "clark", "google", "googol", "peter", "vista", "invite", "friends", "whatsapp", "menu",
                   "start", "america", "new", "zealand", "george", "tv", "milford", "sound", "roma", "roger", "douglas", "my", "computer", "recycle",
                   "anthony", "of", "the", "desert", "national", "bank", "greece", "black", "white", "head", "microsoft", "canada", "london", "sport", "university",
                   "phenoix", "stadion", "emirates", "cd", "blackberry", "messenger", "articles", "capitulation", "indianrailways", "vietnam", "korea",
                    "defender", "maxwell", "australia", "south", "north", "west", "east", "wales", "day", "night", "northland", "waiting", "outside", "Lines",
                   "chance", "early", "show", "love", "hurt", "toronto", "power", "youth", "womens", "liberation", "american", "indian", "movement",
                   "international", "socialist", "organization", "people", "paris", "ellen", "degeneres", "jimmy", "raising", "hope", "freedom",
                   "information", "act", "addon", "manager", "internet", "explorer", "search", "railway", "corporation", "limited", "pagerank", "china",
                   "bill", "gross", "seven", "fundamental", "principle", "red", "cross", "crescent", "install", "smartphone", "first", "united", "future",
                   "automatic", "updates", "gps", "video", "hardware", "software", "outlook", "express", "army", "greenpeace", "homebush"]


def fill_probability_dict():
    """
    This method calculates the probability of a 4-gram to occur in a sentence.
    It uses the unigram approach by dividing the number of occurrences of a 4-gram (+1 smoothing) by the total count of
    seen 4-grams + the number of 4-grams in the corresponding language.
    :return: a dictionary that contains the language model for the 3 languages
    """
    # probability dictionaries - contain the probability of occurrence of a given 4-tuple in a specific language
    indonesian_probability_of_tuples = dict()
    malaysian_probability_of_tuples = dict()
    tamil_probability_of_tuples = dict()
    all_prob_dict = {"indonesian": indonesian_probability_of_tuples, "malaysian": malaysian_probability_of_tuples,
                     "tamil": tamil_probability_of_tuples}
    for l, d in all_count_dict:
        for key in d:
            # approximately 14655 4-tuples in the generalised vocabulary (tuples from all 3 languages)
            # after removing uppercase, special characters and bad words
            all_prob_dict[l][key] = d[key] * 1.0 / (len(d) + count_words_distinct_dict[l])
    return all_prob_dict


def increment_dict_values(language, four_gram):
    """
    This method is used for the filling of the count dictionaries with all possible 4-grams.
    language - the language tag
    four_gram - the 4-gram to be inserted
    It implements the add 1 smoothing and inserts a 4-gram in all 3 languages, if a 4-gram is seen for the first time.
    Otherwise the number of occurrences only in right dictionary is incremented.
    """
    for l, d in all_count_dict:
        if language == l:
            if four_gram in d:
                count_words_distinct_dict[l] += 1
                d[four_gram] += 1
            else:
                count_words_distinct_dict[l] += 1
                # print count_words_distinct_dict[l]
                # Because of 1 smoothing, the initial value is 2 for the language
                d[four_gram] = 2
        else:
            # 1 smoothing
            # if the pair is already in the dict, it shouldn't increase,
            # because the sentence is from a different language
            if four_gram not in d:
                d[four_gram] = 1


def add_tuples_to_dict(sentence, language):
    """
    This method inserts all pairs of tokens into the 3 dictionaries.
    sentence - the sentence without the language tag in front
    language - the language tag
    The sentence is divided in all sequential 4-grams in the sentence, inclusive START and STOP keywords for the
    first/last tokens.
    """
    # insert START keywords
    for i in range(0, 3):
        start_tuple = (3 - i) * ["START"] + list(sentence[:i + 1])
        start_tuple = tuple(start_tuple)
        increment_dict_values(language, start_tuple)

    for i in range(0, len(sentence) - 3):
        four_gram = (sentence[i], sentence[i + 1], sentence[i + 2], sentence[i + 3])
        # go through all dictionaries to insert unknown character pairs
        increment_dict_values(language, four_gram)

    # insert STOP keywords
    for i in range(0, 3):
        stop_tuple = list(sentence[len(sentence) - 3 + i:]) + (i + 1) * ["STOP"]
        stop_tuple = tuple(stop_tuple)
        increment_dict_values(language, stop_tuple)


def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print 'building language models...'
    allowed_languages = ["indonesian", "malaysian", "tamil"]
    with open(in_file, 'r') as train:
        for line in train:
            split_sentence = line.split(' ', 1)
            language = split_sentence[0]
            sentence = split_sentence[1].lower()
            # remove numbers and some special characters
            sentence = re.sub(r"[^a-zA-Z']+", ' ', sentence)
            sentence = ' '.join([i for i in sentence.split(' ') if i not in words_to_remove])
            # make sure that the training data is only for the given 3 languages
            if language not in allowed_languages:
                print 'The training data is corrupted. There should be only 3 languages that form the training data.'
                sys.exit(2)
            add_tuples_to_dict(sentence, language)
        return fill_probability_dict()


def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print "testing language models..."
    with open(in_file, 'r') as test:
        predictions = []
        list_of_sentences = test.read().splitlines()
        for s in list_of_sentences:
            sentence = s.lower()
            sentence = re.sub(r"[^a-zA-Z']+", ' ', sentence)
            four_grams = list(ngrams(sentence, 4, pad_left=True, pad_right=True, left_pad_symbol='START',
                                     right_pad_symbol='STOP'))
            best_guess = None
            for key in LM.keys():
                # used to check the % of known (already seen) 4-grams in a sentence
                count_existing_grams = 0
                # stores the probabilities for all 4-grams in the sentence to multiply them at the end
                probabilities = []
                for t in four_grams:
                    if t in LM[key]:
                        count_existing_grams += 1
                        # log function and addition of the probabilities handle the underflow by multiplication
                        probabilities.append(math.log(LM[key][t], 2))
                # sum, because when applying the logarithmic function, the multiplication sign turns into a + sign
                probability = sum(probabilities)
                # if not enough existing 4-grams in the sentence, it should be another language
                # I selected the value of 50, because I find it reasonable not to give a prediction if you don't know
                # about more than 50% of the data
                if count_existing_grams * 1.0 / len(four_grams) < 0.50:
                    probability = 0
                if best_guess:
                    best_guess = (best_guess[0], best_guess[1]) if best_guess[1] > probability else (key, probability)
                else:
                    best_guess = (key, probability)
            if best_guess[1] == 0:
                predictions.append(("other", s))
            else:
                predictions.append((best_guess[0], s))

    with open(out_file, 'w') as out:
        out_str = str()
        for l, s in predictions:
            out_str += l + ' ' + s + '\n'
        out.write(out_str)


def usage():
    print "usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"

if input_file_b is None or input_file_t is None or output_file is None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
