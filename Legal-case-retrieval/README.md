
# Legal case retrieval

The aim ot this project is to develop a small project on real-world data (documents and queries) for legal case retrieval. 
Due to the stuctured nature of the documents, our team  experimented with different retrieval approaches and built a search engine for the provided dataset (due to information privacy, the actual data will not be uploaded).

## How to run

The python version used for the project is 2.7.12.

## Solution and results

### Index phase:

-> We build a positional dictionary and its postings.<br />
-> In addition, we also create a metadata dictionary and a thesaurus, which are both used in the search phase.<br />
-> In the positional dictionary, we store the term and it’s document frequency and also the head and tail byte for the location of its postings list in the postings file.<br />
-> The dictionary also stores the document normalization values to be used for cosine normalization of each document. We also store the total number of documents N in the dictionary.<br />
-> In the postings list, for each term we store it’s postings list in the form for example “docId1-pos11-pos12 docId2-pos21-pos22-pos23 docId3-pos31-pos32”. <br />
-> The metadata dictionary stores the title of case, name of court and date posted for each document.

### Search phase:

A) Boolean retrieval:<br />
-> For phrases, we use positional dictionary to retrieve only documents that contain the exact phrase. This is done by intersecting the positions of each term in the phrase and taking into account the relative adjacent positions in the documents.<br />
-> For a singular freetext term, we just fetch it’s entire postings.<br />
-> We perform the AND operation between phrases and/or singular freetext terms using the AND merging algorithm for postings.<br />
-> As an additional step, we then convert the entire query into freetext and append the output obtained from that to the result as well. For example  “Good Morning” AND “New York” is converted to the fully freetext form ‘Good Morning New York’ to compute it’s output.<br />
-> Additionally, before the freetext conversion step, we check if there are any phrases in the query, and also put the retrieved doc IDs containing them in the result set, before the freetext query results. This is done if original boolean query using positional indices gives no result.

B) Freetext retrieval:<br />
-> We ranked documents by cosine similarity based on tf×idf. We implemented the lnc.ltc ranking scheme (i.e., log tf and idf with cosine normalization for queries documents, and log tf, cosine normalization but no idf for documents) 

### Zones and fields

-> We use the zone and field data like court name and date posted of the document to tweak the cosine similarity scores for the documents.<br />
-> We defined a dictionary where we assign a relevance factor to each court name, with higher values (say 1.5) courts like “UK Supreme Court” and “SG Court of Appeal", intermediate values like 0.75 to courts like “SG High Court” and "UK High Court" and finally low values like 0.25 to courts like "SG Privy Council" and "NSW Local Court". This is based on the idea the rulings on a matter by supreme court are more relevant than high court, which are more relevant that other lower courts.<br />
-> Similarly we assign a relevance factor to based on date posted of the document, which is to say that if document is from last 5 years we assign it value 1.5, if from last 5-10 years then value 1.0 and so on if more than 40 years old, then relevance factor of 0.2. This is based on the idea that more recent rulings/verdicts are more relevant.<br />
-> We assigned a weightage to each of the date posted based relevance factor(0.4) and to the court name based relevance factor(0.6). This was because we thought the court which offers the ruling is more important that the date of the document.<br />
-> The metadata zones based ranking can be turned on by setting the variable zones_metadata_switch to True in search.py file

### Query expansion techniques

We have a provided a detailed analysis of using these query expansion techniques on results in bonus.txt

1) Synonyms : WordNet-Query expansions:<br />
-> In case any term in the query isn’t in the dictionary, we find a single synonym for it from the WordNet synonyms list which is in our dictionary and use that to replace that term in the query.

2) Synonyms : Thesaurus<br />
-> The index phase also generates a thesaurus from the words in the corpus, and gives us a list of all terms in corpus, which are similar to a given term. This can be used to either expand the query with additional related terms, which increases recall, or substitute terms. This helps us change the query vector for retrieving more relevant documents. 

3) Pseudo Relevance Feedback : Rocchio formula<br />
-> For freetext retrieval, we do a round of pseudo relevance feedback assuming the top 1% of the initially retrieved documents are relevant. We then use Rocchio's formula to generate the expanded query, and then perform another round of cosine similarity computation with this new expanded query to generate the final list of ranked retrieval documents.

-> We used the following values of the constants in the rocchio formula <br />
alpha = 1<br />
beta = 0.75<br />
gamma = 0.15<br />

### Optimizations:
-> Stemming optimization<br />
We observed that indexing was taking too long (about 1 hour or so). We discovered that stemming was the bottleneck for slowing down the indexing phase. Because we don’t have control over the library operations for stemming, we decided to do local caching of stem words for speed up. For each new word that we get, we store the original word as key and its stemmed value as value in a locally cached dictionary. So next time, before we attempt to stem a word, we first check if the word already has its stem present in the cache before calling the library stem function. This halved the indexing time for us, and we were able to index in about 25~28 minutes now.
 
### Other experiments:

-> We tried to create a bigram and trigram dictionary that turned out to be too large and went beyond 4GB of memory, which is the reason we are currently using positional indexing.

-> We tried with converting boolean queries to complete freetext queries and get their output. Even though this was giving a higher recall which means some of the relevant documents didn’t contain the exact phrase as they weren’t being retrieved by the positional index based system , it also gave a lower precision since more documents were being retrieved now and the relevant documents were lower up in the ranking order. So while this was useful, we couldn’t just use this. So we first output the result of phrase search using positional and then the output of fully freetext query.

-> W tried using phrases for freetext queries as well, forming bigrams and trigrams out of that, but it decreased our precision. 

-> Sometimes, the using the positional index, the query results we obtain is empty. In that case, if there are any phrases in the query, we try to retrieve all documents which contain those phrases, and then we append the results of the entire query converted to freetext to this.

-> Using the postional intersection, we tried to do the proximity search, which implies that even if a document doesn't contain the phrase, but the words appear within a window of 10, then we put those doc IDs into our result set

-> We examined some documents and found that there were 16 documents in the datatset.csv which had duplicate document Id's. 
The two copies of the documents with these document id's had the same content but different court names in most cases. This duplication of data while not a major roadblock, was affecting our term freqeuncy and document normlization calculations by a small value.

### Original ideas
-> In dealing with boolean queries, we used the unique idea of first printing the output of the boolean query as we did in HW2 and then converting the entire query to fully freetext and then outputting it's output. This helped to significantly improve our score on the leaderboard.

-> For using positional indices with phrases, we used strict conjunction of words in phrases, i.e., they should appear as exactly in phrase. 

-> We also try to output the result set for any phrases in boolean queries over freetext, if the original boolean query returns an empty result set.

-> We used several query expansion ideas like metadata, rocchio, thesaurus and wordnet for synonyms.

-> We used the stemming optimization to remedy the bottleneck and speed up indexing.

## Description of the files

**index.py**<br />
Generate the dictionary and the postings files from the Intellex training data set.

**search.py**<br />
Load the dictionary, read and evaluate all queries and write their results to the output file.

**boolean_retrieval.py**<br />
Handle boolean queries that are composed of either single terms or phrases of max. length 3 (a phrase in written in quotes)

**freetext_retrieval.py**<br />
Handle free text queries that using tf-idf as in assignment 3.

**retrieve_postings.py**<br />
This module contains the methods for handling synonyms and retrieving the postings for a given term or its synonyms.

**synonyms.py**<br />
This module uses wordnet to return synonyms and their postings for a given term.

**thesaurus.py**<br />
This module builds a co-occurrence matrix out from the term document matrix, which is built during index itself, based
on the terms from the corpus, and for any given term, it gives us the list of the most similar terms in the corpus
(using the term document similarity weights).

**dictionary.txt**<br />
The dictionary with terms and their head, tail and document frequency.

**postings.txt**<br />
The positional postings for all terms in the dictionary. It includes their positions in the respective document.

## Authors
**Svilen Stefanov** <br />
**Arijit Pramanik** <br />
**Wang Chin-Hao** <br />
**Madhav Goel** <br />
*National University of Singapore*

## References
https://www.comp.nus.edu.sg/~zhaojin/cs3245_2018/hw4-intelllex.html - definition of the assignment <br />
https://stackoverflow.com/ - used for some python related questions.<br />
https://docs.python.org/2.7/ - (official Python documentation) - used for other python related questions






