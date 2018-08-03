
# Language Detection

The aim ot this project is to implement a language detection module using 4-grams that can recognise sentences in Malaysian, Indonesian, and Tamil, but also to detect other languages and label them as unknown ("other").

## How to run

The python version used for the project is 2.7.12.

## Solution and results

I used the unigram model for 4-grams with add 1 smoothing. Only 4-grams that were seen in the training set are considered as part of the general vocabulary, but not all possible 4-grams of characters. The implementation of the approach can be found in build_test_LM.py file.

#### General overview of the approach:
```
1. The build_LM method reads from the input file.

2. For each line, it separates the label tag from the sentence, make everything lowercase, remove
special characters, removes bad words from the training data and calls add_tuples_to_dict method.
   
3. Add_tuples_to_dict finds all 4-grams in a sentence.  It also creates 4-grams for the start and end tokens (padding). The method also calls increment_dict_values multiple times.
   
4. For each 4-gram increment_dict_values is called, which implements the add 1 smoothing technique. 
It increments the number of occurrences for a 4-gram and insert/update it in the corresponding dictionary. 
For example if there is the tuple ('a', 'b', 'c', 'd'), which occures for the first time now as part of a sentence labeled as indonesian, it will be inserted in the indonesian dictionary with a value of 2 (1+1, because of the add 1 smoothing) and it will be inserted in the malaysian and tamil languages with a value of 1, because of the 1 smoothing.
All 3 dictionaries contain all existing 4-grams in the training data. 
If the above mentioned tuple was to be found with a value of 4 in the indonesian dictionary, it  will be updated to 5, because it's a new occurence. If the 4-gram is to be found in the other 2 dictionaries, they are not updated, because this 4-gram is not part of the training for them (and the one smoothing has already been done, because they are existing)

5. Afther the dictionaries with the number of occurrences of each 4-gram are build, I calculate the probability of each 4-gram to occur in a sentence in fill_probability_dict following the formula:
(occurences of 4-gram) / ( (number of 4-grams in vocabulary) + (number of 4-grams in that language
only) )
number of 4-grams in vocabulary corresponds to the number of elements of each dictionary
I compute the number of 4-grams in the specific language in seperate variables, all of which are 
stored in the list count_words_distinct_dict.

6. Finally, test_LM method opens a new file, label the sentences given there accordingly (explained later) and writes the concatinated label and the sentence in the specified output file.

I used the unigram model for 4-grams with add 1 smoothing and padding. Only 4-grams that were seen in the cleaned training set are considered as part of the general vocabulary, but not all possible 4-grams of characters. The implementation of the approach can be found in build_test_LM.py file.

Initially, I had 21290 distingt 4-grams in the language model and decided to remove numbers and special characters, which reduced this number to 17446 4-grams. I reduced it to 15364 after converting all letters to small ones. After analysing of the training data, I decided to remove the "bad words", which reduced the total number of 4-grams to 14655. I considered English words and names as "bad", as well as abbreviations. I didn't list all of them, but I tried to filter most of them from the training data, so that my model can recognise English sentences as "other" and not as "Malaysian", because it was often the case that they were more English words in a Malaysian sentence then Malaysian words.

Evaluation of test data:
When computing the similarity of a sentence, part of the test data, I also use the same techniques as above in order to be consistent and be able to evaluate them correctly (lowercase, remove special characters, but not removing any words considered as bad not to corrupt the training data). The formula I used initially for the computation was:
probabilty = probability_of_gram1 * probability_of_gram2 * ... * probability_of_gramN
If there is a 4-gram that doesn't exist in the model, I skip it, but keep track of the number of such not familiar 4-grams to my model.
Due to the small probabilities of most 4-grams and their multiplication, I used the sum of the logarithm of each 4-gram to cope with underflows.

I also set the following restraint for not familiar 4-grams: if 50% of the 4-grams or more in a new sentence are not to be found in the language model, then the model cannot make an accurate informed prediction. Thus it returns "other" in such cases.

Experiments:
I experimented on some random sentences from the internet and achieved good results on identifying "other" languages. It sometimes confuses malaysian and indonesian though, which was expected from the beginning.

I coded add_tuples_to_dict method to make sure I understand the underlying concepts and to know/practise how to write it. For the test data I used the nltk.util ngrams method and tested if it is compatible with mine (with paddings).
```
## Author
**Svilen Stefanov**
*Email: svilen.ks@gmail.com*
*National University of Singapore*






