
# TF-IDF for freetext retrieval

The aim ot this project is to implement indexing and searching techniques for freetext retrieval using TF-IDF.

## How to run

The python version used for the project is 2.7.12.

## Solution and results

### Indexing phase:

First I read from all documents in the Reuters training data set and build the term dictionary after processing all encountered tokens.
During the tokenization I first use sentence and word tokenize functions, then remove any non-alphanumeric characters in the sentence and apply porter stemming.

After that, I sort all postings. Lastly, the result of the indexing phase are saved in dictionary.txt and postings.txt as described below:

**dictionary.txt**
In this file the dictionary is saved in JSON format to find terms and their frequency easier during the search phase. 
All terms are saved as keys and each of them has 3 fields - document frequency (f), head (h) and tail (t). 
The tail and the head are used to find the byte location to read the posting for the term in postings.txt since we will not load all postings in memory and need to know where we can find the posting for a given term during the search phase. 
There is an entry in the dictionary with key 'DOC_NORM' which consists of document-normalized_length pairs 
that are going to be used for faster computation of the normalized document vectors during the search phase. 
I also save the size of the training data set in the dictionary with key 'N' that will be needed for the idf computation in the second phase as well.

**postings.txt**
In this file all postings with term frequencies for the given term are saved in one row since we can determine the exact byte location for the postings of a term using the head and tail from the dictionary. 
The term frequencies are stored in a dash-based format after each document ID.

### Search phase:
In the search phase, we first load the dictionary in memory and open the query document.
Each query is handles as follows: 
First the given query is preprocessed in the same way as in the indexing phase (remove non-alphanumeric characters and stemming).
For each of the unique terms in the query, the corresponding dimension value for the query and for the documents that contain the term is computed. 
After building the query vector, the generation of the document vectors is completed by filling the missing dimensions with 0s. 
All of the document vectors are then sorted according to their docID so that we can guarantee later that documents with the same similarity value will be sorted in increasing order of their document IDs. 
Then all the vectors are normalized and the product of each of the relevant document vectors is computed with the query vector and their similarity is saved in an answer list. 
This list is then sorted based on the similarity and the best 10 results (if existing) are written to the output file in the same order as the queries.

Other decisions: 
I submit the version where I remove all punctuation because it can handle queries that contain words like U.S.A better. 
It won't influence the queries and documents that don't have punctuation, but it would influence the retrieved queries 
since not encountered terms like U.S.A during the indexing phase won't be recognized as part of the dictionary although 
they might be relevant.

Attempts for optimizations: 
1) not normalizing the query vector:
For some reason removing the normalization of the query vector takes me more time on average. 
I tested both the normalized and not normalized version (not normalized version would be removing lines 185 and 186 
in search.py and substituting q_vec_norm with q_vec in line 192) with the same timeit function, which resulted in the normalization version being 0.02 seconds faster. 
That is why I didn't integrate this optimization.
2) choosing only documents that have at least 3/4 of the terms in the query that are part of the dictionary:
This optimization didn't work quite well for me either, in fact it looks like it slows down the search phase almost 4 times. 
In the method compute_norm_doc I tried to select and normalize only the documents that contain 3/4 of the relevant query terms, but I didn't get any performance benefits. 
My explaination for this are:
- For selecting 3/4 of the relevant terms, there are a lot of list merges that need to be done, which slows down the computation drastically. 
I could have tried to improve that again with pointers, but for our data set (and based on the experience from Boolean retrieval) 
I assumed that pointers aren't the biggest problem here.
- A more reasonable approach would have been to change the indexing phase and store tuples or triples of words in another document which would cost more time, 
but would save a lot of merging time.

## Description of the files

**index.py**<br />
Generate the dictionary and the postings files from the Reuters training data set.

**search.py**<br />
Load the dictionary, read and evaluate all queries and write their results to the output file.

**dictionary.txt**<br />
The dictionary with terms and their head, tail and document frequency.

**postings.txt**<br />
The postings for all terms in the dictionary and their term frequency in the respective document.

**README.txt**<br />
The description of our approach and other important notes.

**Questions/**<br />
* answers.txt <br />

Answers to the questions for assignment 3.

## Author
**Svilen Stefanov** <br />
*Email: svilen.ks@gmail.com* <br />
*National University of Singapore*

## References
https://www.comp.nus.edu.sg/~zhaojin/cs3245_2018/hw3-vsm.html - definition of the assignment 






