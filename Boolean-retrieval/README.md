
# Boolean retrieval

The aim ot this project is to implement indexing and searching techniques for Boolean retrieval.

## How to run

The python version used for the project is 2.7.12.

Check the param_config.txt in Analysis_and_Setup directory to see how to run the index.py and search.py files.

## Solution and results

### Indexing phase:
First we read from all documents in the Reuters training data set and build the term dictionary after processing all encountered tokens.
During the tokenization we first remove any non-alphanumeric characters in the sentence then use sentence and word tokenize functions and apply porter stemming as the homework description suggests.

After that, we sort all postings so that the document IDs can be compared efficiently during the search phase. Lastly, we save the result of indexing in dictionary.txt and postings.txt as described below:

dictionary.txt
In this file we save the dictionary in JSON format to find terms and their frequency easier in the search phase. 
All terms are saved as keys and each of them has 3 fields - document frequency (f), head (h) and tail (t). 
The tail and the head are used to find the byte location to read the posting for the term in postings.txt since we will only load the whole dictionary in memory for the search phase. 
We also save a list of all encountered document IDs as part of the dictionary with the key "ALL" so that we can calculate the NOT operation during the query evaluation.

postings.txt
In this file we save all postings with their pointers in one row since we can determine the exact byte location for the postings of a term using the head and tail from the dictionary. 
We write the skip pointers in a dash-based format after each document ID. The document IDs that don’t have a skip pointer are assigned with value 0. 
Document IDs that point to another document ID have a skip pointer value representing the index of the document ID they point to. 
The index here refers to the index of a posting list constructed in the search phase. For instance, 1-2 2-0 3-4 4-0 5-0 represents a posting of document IDs 1,2,3,4,5 where 1 points to 3 (index 2) and 3 points to 5 (index 4).
The pointers are evenly spaced starting from the first document ID and skip at least one element (meaning there are no pointers for postings of length 1, 2 or 3 since in these cases skip pointer doesn't make operations faster).

### Search phase:
In the search phase, we first load the dictionary in memory and open the query document.
Each query is handles as follows: 
First the given boolean expression is preprocessed so that we can compute the answer of the query faster. 
The preprocess phase first separate the query in terms and operators and formats the terms in the same way as in the indexing phase (remove non-alphanumeric characters and steming). 
After that multiple NOTs are removed to simplify the boolean expression. 
Subsequently, for each part of query in CNF, we place the term with the smalles posting list size from that CNF at the end of it so that this smallest list can be merged first during the computation of the postinfix notation. 
At the end, we convert each expression of the type NOT A AND B to B AND NOT A, so that we can make use of the faster AND NOT opearation (compared to negating A and then merging it with B). 
This will not harm the previous size arrangement but could improve the spead even more. 
After the rearrangement of the boolean expression, we convert the infix notation to postfix and compute it accordingly. 
For the computation we provide methods for each operand since they need different types of merging (AND, OR, NOT, AND NOT). 
After the merges, the list of all related postings for the query is retrieved and saved in the list with answers. '
We don't write the answer directly to the output file, so that we can open the file only once and save time by writing only once on the disk.
After the answers to all queries are computed, they are written to the output file in the same order as the queries.

### Description of the files

**index.py** <br />
Generate the dictionary and the postings files from the Reuters training data set.

**search.py** <br />
Load the dictionary, read and evaluate all queries and write their results to the output file.

**preprocess.py** <br />
Change the order of the query elements so that the query can be processed optimally.

**reverse_polish_notation.py** <br />
Implement and evaluate the Shunting-yard algorithm and method for getting the postings for a specific term.

**list_operations.py** <br />
Incorporate all list operations for the operators AND, OR, NOT and AND NOT.

```
test_list_operations.py 
test_preprocess.py 
test_reverse_polish_notation.py
test_search.py
```
Unit tests created to test our code extensively.

**Essay_Questions/** <br />
* dictionary_with_numbers.txt <br />
* dictionary_without_numbers.txt <br />
* postings_with_numbers.txt <br />
* postings_without_numbers.txt <br />

Files created to answer the essay quesitons. <br />

* essay.txt <br />

Answers to the essay questions.

## Authors
**Svilen Stefanov and Wang Chin-Hao** <br />
*Email: svilen.ks@gmail.com* <br />
*National University of Singapore*

## References
https://www.comp.nus.edu.sg/~zhaojin/cs3245_2018/hw2-bool.html - definition of the assignment 
<br />
https://regex101.com/ - used for checking the regular expressions <br />
https://stackoverflow.com/ - used for some python related questions. <br />
https://docs.python.org/2.7/ - (official Python documentation) - used for other python related questions





