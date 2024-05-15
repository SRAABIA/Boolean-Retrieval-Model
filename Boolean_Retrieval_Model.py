import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import re
import os
import nltk
import string
from nltk.stem import PorterStemmer
from nltk.tokenize import WordPunctTokenizer 
string.punctuation

stop_words = ['a', 'is', 'the', 'of', 'all', 'and', 'to', 'can', 'be', 'as', 'once', 'for',
             'at', 'am', 'are', 'has', 'have', 'had', 'up', 'his', 'her', 'in', 'on', 'no', 'we', 'do']

def perform_boolean_search(query):
    inverted_index = {}

    if os.path.exists('indexes.txt'):
            # print("FILE EXISTS")
            with open('indexes.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split(' -> ')
                    if len(parts) == 2:
                        number_term, documents = parts
                        number, term = number_term.split(' - ')
                        documents_list = [doc.strip() for doc in documents.split(',')]
                        inverted_index[term] = documents_list
            
    else:
        inverted_index , positional_index = maketokens()

    result_set = boolean_query_processing(query, inverted_index)
    return result_set

def proximity_query_processing(proximity_query, proximity_value, positional_index):
    porter = PorterStemmer()
    query_terms = proximity_query.split(" / ")
    token1, token2 = query_terms
    
    # getting positions for the tokens
    positions_token1 = positional_index.get(porter.stem(token1), {})
    positions_token2 = positional_index.get(porter.stem(token2), {})
    
    # Initialize list to store matching documents
    matching_documents = []
    
    # Iterate over the documents where both tokens appear
    for doc_id in set(positions_token1.keys()) & set(positions_token2.keys()):
        # Get positions of token1 and token2 in the current document
        positions1 = positions_token1[doc_id]
        positions2 = positions_token2[doc_id]
        
        # Check distance for each pair of positions
        for pos1 in positions1:
            for pos2 in positions2:
                # Calculate absolute difference between positions
                distance = abs(pos1 - pos2)
                # Check if absolute difference is within proximity distance
                if distance <= proximity_value:
                    matching_documents.append(doc_id)
                    break  # Exit inner loop once a match is found
            else:
                continue  # Continue to next position1 if no match is found
            break  # Exit outer loop once a match is found for the document
    
    return matching_documents

def perform_proximity_search(proximity_query, proximity_value):
    positional_index = {}
    file_path = 'positional_index.txt'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(' -> ')
                if len(parts) == 2:
                    token, positions_info = parts
                    positions_info = positions_info.split('| ')
                    positions = {}
                    for pos_info in positions_info:
                        file_name, file_positions = pos_info.split(': ')
                        # Remove square brackets from the positions string before splitting
                        file_positions = file_positions.strip('[]')
                        positions[file_name] = [int(pos) for pos in file_positions.split(',')]
                    positional_index[token] = positions
    else:
        inverted_index , positional_index = maketokens()
    
    result_set = proximity_query_processing(proximity_query, proximity_value, positional_index)
    return result_set

def search_button_clicked():
    boolean_query = boolean_entry.get()
    proximity_query = proximity_entry.get()
    proximity_value = proximity_value_entry.get()

    # Check if the boolean query is not empty
    if boolean_query.strip():
        # Perform boolean search
        boolean_result = perform_boolean_search(boolean_query)

        # Display boolean search result in the GUI
        result_text.delete(1.0, tk.END)
        boolean_result_str = f"Boolean Search Results:\n{', '.join(map(str, boolean_result))}\n\n"
        result_text.insert(tk.END, boolean_result_str)

    # Check if the proximity query is not empty
    if proximity_query.strip() and proximity_value.strip():
        # Perform proximity search
        proximity_result = perform_proximity_search(proximity_query, int(proximity_value))

        # Display proximity search result in the GUI
        proximity_result_str = f"Proximity Search Results:\n{proximity_result}\n"
        result_text.insert(tk.END, proximity_result_str)

#defining the function to remove punctuation
def lower_the_tokens(words):
    lower = [word.lower() for word in words]
    return lower

def remove_punctuation(text):
    # Remove punctuation
    punctuation_free = ''.join([char for char in text if char not in string.punctuation])
    # Check for characters not in English
    english_characters = set(string.ascii_letters + string.digits + ' ')  # English letters, digits, and space
    filtered_text = ''.join([char if char in english_characters else ' ' for char in punctuation_free])
    return filtered_text

def remove_stopwords(list_of_words):
    proper_text = [word for word in list_of_words if word.lower() not in stop_words]
    return proper_text

def remove_numbers_from_token(token):
    result = re.sub(r'\d', '', token) #remove numbers
    return result

def remove_single_alphabets_from_token(token):
    result = re.sub(r'\b[a-zA-Z]\b', '', token) #remove singlesingle alphabets
    return result

def tokenize(text):
    # Create a reference variable for Class WordPunctTokenizer
    tk = WordPunctTokenizer()
    # Use tokenize method
    tokenlist = tk.tokenize(text)
    cleaned_tokens = [remove_numbers_from_token(token) for token in tokenlist]
    cleaned_tokens = [remove_single_alphabets_from_token(token) for token in cleaned_tokens]

    cleaned_tokens = list(filter(lambda x: x != '',cleaned_tokens ))

    cleaned_tokens = [token for token in cleaned_tokens if token.isalnum()]
    return cleaned_tokens

def porter_stemming(words):
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in words ]
    return stemmed_words

def preprocessing(content):
    content = remove_punctuation(content)
    # current_tokens = nltk.word_tokenize(content)
    current_tokens = tokenize(content)
    current_tokens = lower_the_tokens(current_tokens)
    current_tokens = remove_stopwords(current_tokens)
    current_tokens = porter_stemming(current_tokens)
    return current_tokens

def query_preprocessing(query):
    wordList = query.lower().split()
    wordList = porter_stemming(wordList)
    return wordList

def positional_preprocessing(content):
    content = remove_punctuation(content)
    current_tokens = tokenize(content)
    current_tokens = lower_the_tokens(current_tokens)
    current_tokens = porter_stemming(current_tokens)
    return current_tokens

def maketokens():
    # Initialize DocID
    DocID = 0  
    tokens_in_each_doc = []
    filenames = []
    inverted_index = {}
    positional_index = {}

    # Read files to make tokens
    for root, dirs, files in os.walk('ResearchPapers/'):
        for file_name in files:  # Document in Corpus
  
            filenames.append(file_name)
  
            with open(os.path.join(root, file_name), 'r') as file:  # Extracting sentences in a document
                content = file.read()
                current_tokens = preprocessing(content)
                tokens_in_each_doc.append(current_tokens)           # Append the tokens for the current document to the list
                position_tokens = positional_preprocessing(content)

            # Update positional index

                for position, token in sorted(enumerate(position_tokens)):
                    if token not in positional_index:
                        positional_index[token] = {file_name: set([position])}
                    else:
                        if file_name not in positional_index[token]:
                            positional_index[token][file_name] = set([position])
                        else:
                            positional_index[token][file_name].add(position)
                    print(positional_index[token][file_name],end='\n')
            DocID += 1

    all_tokens_set = set()
    for i in range(DocID):
        all_tokens_set.update(tokens_in_each_doc[i])
    unique_terms_list = list(all_tokens_set)

    # Update inverted index

    for term in unique_terms_list:
        documents = []
        for i in range(DocID):
            if term in tokens_in_each_doc[i]:
                root, _ = os.path.splitext(filenames[i])
                documents.append(int(root))
        
        # Sort the documents for each term
        documents.sort()
        str_documents = [str(doc) for doc in documents]
        inverted_index[term] = str_documents
        print(inverted_index[term])
    # Write inverted index into a file
    if not os.path.exists('indexes.txt'):
        with open('indexes.txt', 'w') as file:
            i = 0
            for term, documents in inverted_index.items():
                print(i+1, ' - ', term, "->", ", ".join(documents))
                file.write(f"{i+1} - {term} -> {', '.join(documents)}\n")
                i += 1
    # else:
    #     print("file for inverted index exists.")
    
    # Write positional index into a file
    output_file_path = 'positional_index.txt'
    if not os.path.exists(output_file_path):
        with open(output_file_path, 'w') as file:
            for token, positions in positional_index.items():
                file.write(f"{token} -> {'| '.join([f'{file_name}: {sorted(positions[file_name])}' for file_name in positions])}\n")
                print(f"{token} -> {'| '.join([f'{file_name}: {sorted(positions[file_name])}' for file_name in positions])}")

    # else:
    #     print("file for positional index exists.")

    return inverted_index, positional_index

def boolean_query_processing(query, inverted_index):
    files = [1, 2, 3, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23,24,25,26]

    terms = query_preprocessing(query)

    bools = ['and', 'or', 'not']
    
    golden_index = []

    for i,t in enumerate(terms):
        # print('t is ',t)

        if t not in bools:

            term_inverted_index = set(inverted_index.get(t, []))
            
            # Append a tuple containing the term and its inverted index size
            
            golden_index.append((t,len(term_inverted_index),frozenset(term_inverted_index) ))
            
            # print(golden_index)

    # Sort golden_index in descending order based on the size of inverted indexes
            
    golden_index.sort(key=lambda x: x[1])  
    # print(golden_index)
    notime=0
    if len(terms) == 1:
        if golden_index:
            result_set = golden_index[0][2] 
        else:
            result_set = []

    elif bools[1] in terms:
        i = 0
        while i < len(terms):
            t = terms[i]

            if t == 'or':
                x = 0
                y = 1
                set1 = golden_index[x][2]
                set2 = golden_index[y][2]
                set1 = set(map(int, set1))
                set2 = set(map(int, set2))
                result_set = set1.union(set2)
                golden_index[x] = ('', len(result_set), frozenset(result_set))
                del golden_index[y]
                # print("INSIDE OR  ",result_set)
                result_set = sorted(result_set)

            i += 1

        # if i == len(terms):
        #     return result_set

    else: 
        while notime < len(terms):
            if not golden_index:
                break

            if terms[notime] == bools[2]:

                set1 = set(files)

                set2 = golden_index[0][2]

                del golden_index[0]

                set2 = set(map(int, set2))
                
                result_set = set1.difference(set2)
                
                result_set = sorted(result_set)

                # golden_index[0] = ('',len(result_set), frozenset(result_set))


                # print("Result in NOT ",result_set)

            elif terms[notime] == bools[0]:
                i = 0
                while i < len(terms):
                    t = terms[i]

                    if t == 'and' :
                        if terms[i+1] != 'not':
                            x = 0
                            y = 1
                            set1 = golden_index[x][2]
                            # print("188: ",golden_index)
                            set2 = golden_index[y][2]
                        
                            set1 = set(map(int, set1))
                        
                            set2 = set(map(int, set2))
                            
                            # print('set1,2:  ', set1,set2)

                            result_set = set1.intersection(set2)
                            
                            result_set = sorted(result_set)

                            golden_index[x] = ('',len(result_set), frozenset(result_set))

                            del golden_index[y]

                            # print('golden index after delete ',golden_index)
                        
                        elif terms[i+1] == 'not':
                                                                # Solve not part then AND it with prev
                            set1 = set(files)

                            set2 = golden_index[0][2]

                            del golden_index[0]

                            set2 = set(map(int, set2))

                            result_set1 = set1.difference(set2)

                            result_set1 = sorted(result_set1)

                            set1 = set(result_set)

                            set2 = set(result_set1)

                            result_set = set1.intersection(set2)

                            # print('result after and NOT ',result_set)
                        
                    i+=1
                if i == len(terms):
                    break
            notime += 1
        
    # print('resultset  ',result_set)
    
    return result_set

def clear_entry(event):
    event.widget.delete(0, tk.END)

if __name__ == '__main__':
    
    # FOR CMD 
    # while 1:
    #     # str = input("Enter QUery: ")
    #     # boolean_query_processing(str, inverted_index)
    #     q = input("Enter Query " )
    #     p = int(input('distance: '))
    #     print(perform_proximity_search(q,p))

    # For GUI
    root = tk.Tk()
    root.title("Search Application")

    # Search Bar Section
    search_frame = ttk.Frame(root, padding="10")
    search_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    boolean_label = ttk.Label(search_frame, text="Boolean Query:")
    boolean_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)

    boolean_entry = ttk.Entry(search_frame, width=30)
    boolean_entry.insert(0, "Boolean Search (AND OR NOT)")
    boolean_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

    search_button = ttk.Button(search_frame, text="Search 🔎", command=search_button_clicked)
    search_button.grid(column=2, row=0, padx=5, pady=5, sticky=tk.E)

    # Proximity Search Section
    proximity_frame = ttk.Frame(root, padding="10")
    proximity_frame.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    proximity_label = ttk.Label(proximity_frame, text="Proximity Search:")
    proximity_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)

    proximity_entry = ttk.Entry(proximity_frame, width=30)
    proximity_entry.insert(0, "Information / Retrieval")
    proximity_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

    proximity_value_label = ttk.Label(proximity_frame, text="Distance (k):")
    proximity_value_label.grid(column=2, row=0, padx=5, pady=5, sticky=tk.W)

    proximity_value_entry = ttk.Entry(proximity_frame, width=15)
    proximity_value_entry.insert(0, "(3)")
    proximity_value_entry.grid(column=3, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

    # Display Results Section
    result_text = ScrolledText(root, wrap=tk.WORD, width=60, height=15)
    result_text.grid(column=0, row=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    boolean_entry.bind("<FocusIn>", clear_entry)
    proximity_entry.bind("<FocusIn>", clear_entry)
    proximity_value_entry.bind("<FocusIn>", clear_entry)

    # Run the Tkinter event loop
    root.mainloop()