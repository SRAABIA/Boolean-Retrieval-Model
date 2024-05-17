# Boolean Information Retrieval Model

_K214553 Syeda Rabia Hashmi_
## Introduction
This project presents a robust Information Retrieval system, employing a Boolean Model to efficiently retrieve queries from a collection of 20 research papers. It utilizes Python, NLTK, and Tkinter to preprocess documents, create indexes, process queries, and provide a user-friendly interface.

## Tools and Libraries
-	Python 3.x
-	NLTK (Natural Language Toolkit)
-	Tkinter (for GUI)

## Dataset
The dataset consists of 20 research papers in English language extracted from PDFs.

## Procedure
The solution involves the following steps:
-	Preprocessing: Removal of special characters, tokenization, and stemming.
-	Tokenizing: Splitting text into individual words or tokens.
-	Stemming: Reducing tokens to their root form using Porter Stemmer.
-	Inverted Index Creation: Inserting stemmed tokens into the inverted index.
-	Query Processing: Implementing Boolean query processing.
-	Positional Index Creation: Creating positional inverted index for proximity queries.
-	Proximity Query Processing: Retrieving documents with terms at specified proximity.
-	GUI Implementation: Creating a user-friendly interface using Tkinter.


## Data Structures
The primary data structures used in this project are dictionaries and sets. The dictionaries are used to create both the inverted and positional indexes, with terms as keys and document IDs as values. Sets are used to store the positions of terms in each document.


## Creating Inverted Index
The inverted index is created by iterating over each term in the unique terms list. For each term, the documents containing the term are identified and stored in a list. This list is then sorted and stored in the inverted index dictionary against the corresponding term.

## Processing Boolean Query
The Boolean query is processed by breaking it down into individual terms and operators. The documents corresponding to each term are retrieved from the inverted index. These document lists are then combined based on the Boolean operators to produce the final result. It utilizes stack-based evaluation to process AND, OR, and NOT operations efficiently.

## Creating Positional Index
The positional index is created by iterating over each term in the document. For each term, the positions where it occurs are identified and stored in a set. This set is then stored in the positional index dictionary against the corresponding term and document.

## Processing Proximity Query
The positional index query is processed by breaking it down into individual terms and proximity operators. The positions of each term in the documents are retrieved from the positional index. These position sets are then compared based on the proximity operators to produce the final result.

## GUI Implementation
The GUI for this project is created using Tkinter. It provides a user-friendly interface for inputting queries and viewing the results.


## How to Test It
- Test Case 1:&nbsp; Boolean query: cancer AND learning 
- Test Case 2:&nbsp;Boolean query:  feature AND selection AND redundency
- Test Case 3:&nbsp; Boolean query: NOT model 
- Test Case 4:&nbsp; Boolean query: feature AND selection AND classification
- Test Case 5:&nbsp; Boolean query:NOT classification  AND NOT feature 
- Test Case 6:&nbsp; Proximity query: artificial / intelligence (proximity 1)
- Test Case 7:&nbsp; Proximity query:  overview / historical (proximity 2)
- Test Case 8:&nbsp; Proximity query: abstract / number (proximity 3)
<br>(don't forget to add / )

## Output

![Boolean Query](/img/p1.png)
![Proximity Query](/img/p2.png)
