#!/usr/bin/python3

import re
import math
import nltk
import ast
import sys
from nltk.corpus import stopwords
from porterstemmer import PorterStemmer
from collections import OrderedDict

term_file = "TUAW-dataset/data/term.txt"
num_inlinks_file = "TUAW-dataset/data/num_inlinks.txt"
term_line_num_file = "TUAW-dataset/data/term_line_num.txt"

def parse_input():
    """Read input from the user."""
    if len(sys.argv) == 1 or len(sys.argv) > 3:
        print("""Usage: ./search.py "query" [k]
Returns the top k results of the search. The second argument is optional, by default k = 10.""")
        sys.exit(1)
    elif len(sys.argv) == 2:
        query_string = sys.argv[1]
        k = 10
    else:
        query_string = sys.argv[1]
        k = int(sys.argv[2])
        if k < 1 or k > 100000:
            print("Error! k must be between 1 and 100000, setting k = 10")
            k = 10
    return (query_string, k)

def get_posting_list(lines_to_get):
    """Return the posting lists corresponding to each element of @lines_to_get"""

    # type(posting list) == { term: [df, {doc_id: tf}] }
    posting_list = {}
    current_index = 0
    with open(term_file) as f:
        for i, line in enumerate(f):
            if i == lines_to_get[current_index]:
                term_length = line.find(":") # format = term: [df: {doc_id, tf}]
                term = line[0 : term_length]
                # safely parse (but not evaluate) the value, result -> valid python object
                value = ast.literal_eval(line[term_length + 1 : ])
                posting_list[term] = value
                current_index += 1
                if(current_index == len(lines_to_get)):
                    break
    
    return posting_list

def calc_weights(query_freq, posting_list, N):
    """Return the query weight vector @weight_query and the documents weight vectors @doc_dict."""
    
    # type(weight_query) == {term: tf-idf == ltc }
    weight_query = {}
    # type(doc_dict) == {doc_id: {term: tf-idf == lnc }}
    doc_dict = {}

    for term in query_freq.keys():
            # query = ltc
            query_tf = 1 + math.log( query_freq[term] )
            # print(query_tf)
            term_df = posting_list[term][0]
            # print(term_df)
            query_idf = math.log(N / term_df)
            # print(query_idf)
            weight_query[term] = query_tf * query_idf
            
            # document = lnc
            weight_doc = {}
            for doc_id in posting_list[term][1].keys():
                doc_tf = 1 + math.log( posting_list[term][1][doc_id] )
                doc_df = 1 # no
                weight_doc[term] = doc_tf * doc_df
                if doc_id in doc_dict:
                    doc_dict[doc_id][term] = weight_doc[term]
                else:
                    doc_dict[doc_id] = {}
                    doc_dict[doc_id][term] = weight_doc[term]

    # normalize query, c = euclidean
    divide_by = math.sqrt( sum([ x**2 for x in weight_query.values() ]) )
    for term, weight in weight_query.items():
        weight_query[term] = weight / divide_by
    # normalize docs, c = euclidean
    for doc_id, weight_doc in doc_dict.items():
        divide_by = math.sqrt( sum( [ x**2 for x in weight_doc.values() ] ) )
        for term, weight in weight_doc.items():
            doc_dict[doc_id][term] = weight / divide_by

    return (weight_query, doc_dict)

def get_top_k(weight_query, doc_dict, k):
    """Return doc_ids of the top @k documents that match the query based on cosine similarity \
between query vector and document vectors and number of inbounds links to the post"""
    
    # find fraction of all inlinks to doc_id
    total_num_inlinks = 0
    frac_inlinks = {}
    with open(num_inlinks_file) as f:
        doc_ids_set = doc_dict.keys()
        for i, line in enumerate(f):
            total_num_inlinks += int(line.strip())
            if i in doc_ids_set:
                frac_inlinks[i] = int(line.strip())
    

    for doc_id, frac in frac_inlinks.items():
        frac_inlinks[doc_id] = frac / total_num_inlinks

    # calculate score
    # score = alpha * frac_inlinks + (1 - alpha) * cosine similarity
    alpha = 0.5
    score = {}
    for doc_id, weight_doc in doc_dict.items():
        cosine_score = 0
        for term, weight in weight_doc.items():
            cosine_score += weight_doc[term] * weight_query[term]
        score[doc_id] = alpha * frac_inlinks[doc_id] + (1 - alpha) * cosine_score
    
    # sort based on score, high to low
    sorted_score = OrderedDict( sorted(score.items(), key=lambda t: t[1], reverse=True) )
    
    # type(top_k) == {doc_id: [score, "doc_text"]}
    # note top_k is not sorted based on score!
    top_k = {}
    num_results = 0
    for doc_id, score in sorted_score.items():
        num_results += 1
        top_k[doc_id] = [score, ""]
        if num_results == k:
            break
    return top_k

def normalize(string, stemmer, stopwords_set):
    """Return a list containg non-empty terms from @string after normalization using 
@stopwords_set and @stemmer."""

    # tokenize using punkt data
    dummy_list = nltk.word_tokenize(string)

    # remove stopwords
    dummy_list = [word for word in dummy_list if word not in stopwords_set]

    # split using special characters as delimiters
    # example "50,000" -> ["50", "000"]
    # example "." -> ["", ""]
    term_list = []
    for word in dummy_list:
        term_list += re.split(r"[^0-9A-Za-z]", word)
    
    # stemming using Porter Stemmer
    term_list = [stemmer.stem(word, 0, len(word) - 1) for word in term_list]

    # remove empty terms
    term_list = [word for word in term_list if len(word) > 0]

    return term_list

def search(query_string, k, line_num_dict, N):
    """Return top @k search results for @query_string from the corpus of @N documents using \
@line_num_dict as a lookup table."""
    stemmer = PorterStemmer()
    stopwords_set = set(stopwords.words("english"))

    # normalize the query
    term_list = normalize(query_string, stemmer, stopwords_set)
    
    query_freq = {} # num of occurences of every unique term
    for term in term_list:
        if term in query_freq:
            query_freq[term] = query_freq[term] + 1
        elif len(term) > 0: # add only term of non-zero length
            query_freq[term] = 1

    # retrieve only necessary posting lists in the order they appear in the file
    lines_to_get = []
    for term in query_freq.keys():
        lines_to_get += [line_num_dict[term]]
    lines_to_get.sort()

    # if no word in the quey occurs in the data, posting list will be empty
    if len(lines_to_get) == 0:
        print("No results found")
        sys.exit(0)

    posting_list = get_posting_list(lines_to_get)

    (weight_query, doc_dict) = calc_weights(query_freq, posting_list, N)
    
    top_k = get_top_k(weight_query, doc_dict, k)

    # result = doc_id + score + title + url
    title_file = "TUAW-dataset/data/title.txt"
    post_url_file = "TUAW-dataset/data/post_url.txt"

    # sort based on doc_id for efficient retrieval
    docs_to_get = []
    for doc_id in top_k.keys():
        docs_to_get += [doc_id]
    docs_to_get.sort()

    current_index = 0
    with open(title_file) as title_fd, open(post_url_file) as post_url_fd:
        lines = zip(title_fd, post_url_fd)
        for i, line in enumerate(lines):
            if i == docs_to_get[current_index]:
                title_string = "Title = " + line[0]
                post_url_string = "URL = " + line[1]
                top_k[i][1] = title_string + post_url_string
                current_index += 1
                if current_index == len(docs_to_get):
                    break

    # sort top_k based on score
    result = OrderedDict( sorted(top_k.items(), key=lambda t: t[1][0], reverse=True) )

    # print output
    num_results = 1
    for doc_id, [score, details] in result.items():
        print(str(num_results) + ". Doc_ID = " + str(doc_id) + " ; Score = " + str(result[doc_id][0]))
        print(result[doc_id][1])
        num_results += 1

def main():
    line_num_dict = {}
    N = 0
    dummy_list = []
    
    try:
        f = open(term_line_num_file)
        for line in f:
            dummy_list += [line]
        N = int(dummy_list[0])
        for line in dummy_list[1:]:
            temp = line.split(" ")
            term = temp[0].strip()
            line_num = int(temp[1].strip())
            line_num_dict[term] = line_num
    except:
        print("Error! Index not constructed. Execute build_index.py to search")
        sys.exit(1)
    else:
        f.close()
    (query_string, k) = parse_input()
    search(query_string, k, line_num_dict, N)

if __name__ == "__main__":
    main()