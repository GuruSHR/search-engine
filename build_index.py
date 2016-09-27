#!/usr/bin/python3

import time
import re
import html
import nltk
from nltk.corpus import stopwords
from porterstemmer import PorterStemmer
from collections import OrderedDict

def parse_backward(line, next_delimiter, delimiter=","):
    """Return the column text and its left delimiter by reading the delimiter from the end of line."""
    elem_end = next_delimiter
    elem_start = line.rfind(delimiter, 0, elem_end) + 1
    elem = line[elem_start : elem_end].strip()
    return (elem, elem_start - 1)

def parse_forward(line, prev_delimiter, delimiter=","):
    """Return the column text and its right delimiter by reading the delimiter from the start of line."""
    elem_start = prev_delimiter + 1
    elem_end = line.find(delimiter, elem_start)
    elem = line[elem_start : elem_end].strip()
    return (elem, elem_end)

def write_to_file(filename, listname):
    """Write each element of the list to a single line in the file."""
    with open(filename, mode="w", encoding="utf-8") as f:
        for elem in listname:
            f.write(elem + "\n")

def parse_html_entities():
    """Remove / convert to utf-8 all SGML special characters."""
    raw_file = "TUAW-dataset/data/posts.csv"
    decode = ""
    print("Parsing HTML entities...", end=" ")

    with open(raw_file, "r", encoding="latin-1") as f:
        s = f.read()
        s = re.sub(r"and[A-Za-z]+?;", "", s)
        s = re.sub(r"and#([0-9]{0,4})?;", "", s)
        decode = html.unescape(s)

    decoded_file = "TUAW-dataset/data/clean_posts.csv"

    with open(decoded_file, mode="w", encoding="utf-8") as f:
        f.write(decode)

    print("Done")

def parse_csv():
    """Separate each column to its own file, one line per post."""

    # input file
    data_file = "TUAW-dataset/data/clean_posts.csv"

    # 1 output file per attribute
    # to retrieve i-th post, read i-th line of each file
    title_file = "TUAW-dataset/data/title.txt"
    date_file = "TUAW-dataset/data/date.txt"
    author_file = "TUAW-dataset/data/author.txt"
    category_file = "TUAW-dataset/data/category.txt"
    post_text_file = "TUAW-dataset/data/post_text.txt"
    post_length_file = "TUAW-dataset/data/post_length.txt"
    num_inlinks_file = "TUAW-dataset/data/num_inlinks.txt"
    num_outlinks_file = "TUAW-dataset/data/num_outlinks.txt"
    num_comments_file = "TUAW-dataset/data/num_comments.txt"
    comments_url_file = "TUAW-dataset/data/comments_url.txt"
    # assert(comments_url_file[i] == post_url_file[i] + "#comments") == True) (checked)
    post_url_file = "TUAW-dataset/data/post_url.txt"

    month_pattern = re.compile("Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec")

    print("Parsing the columns...")

    title_list = []
    date_list = []
    author_list = []
    category_list = []
    post_text_list = []
    post_length_list = []
    num_inlinks_list = []
    num_outlinks_list = []
    num_comments_list = []
    comments_url_list = []
    post_url_list = []

    with open(data_file, encoding="utf-8") as f:
        line_num = 0
        for line in f:
            line_num = line_num + 1
            
            # search for start of date
            date_start = month_pattern.search(line).start()
            
            # end - start = length of column
            # column = line[start, end)

            # add title
            title_start = 0
            title_end = date_start - 1
            title = line[title_start : title_end].strip()
            title_list.append(title)
            
            # search for next comma = end of date
            prev_comma = date_start - 1
            (date, prev_comma) = parse_forward(line, prev_comma)
            date_list.append(date)
            
            # search for next comma = end of author
            (author, prev_comma) = parse_forward(line, prev_comma)
            author_list.append(author)

            # search for next comma = end of category
            (category, prev_comma) = parse_forward(line, prev_comma)
            category_list.append(category)

            post_text_start = prev_comma + 1        
            # posts can contain comma, so parse columns from end
            
            # reverse search first comma = start of post_url
            next_comma = len(line) - 2 # end of line == ",\n" (checked)
            (post_url, next_comma) = parse_backward(line, next_comma)
            post_url_list.append(post_url)
            
            # reverse search first comma = start of comments_url
            (comments_url, next_comma) = parse_backward(line, next_comma)
            comments_url_list.append(comments_url)
            
            # url assertion checked
            
            # reverse search first comma = start of num_comments
            (num_comments, next_comma) = parse_backward(line, next_comma)
            num_comments_list.append(num_comments)
            
            # reverse search first comma = start of num_inlinks
            (num_inlinks, next_comma) = parse_backward(line, next_comma)
            num_inlinks_list.append(num_inlinks)
            
            # reverse search first comma = start of num_outlinks
            (num_outlinks, next_comma) = parse_backward(line, next_comma)
            num_outlinks_list.append(num_outlinks)
            
            # reverse search first comma = start of post_length
            (post_length, next_comma) = parse_backward(line, next_comma)
            post_length_list.append(post_length)
            
            # remaining is post_text
            post_text_end = next_comma
            post_text = line[post_text_start : post_text_end]
            post_text_list.append(post_text)

    # end processing of file

    # write output`
    write_to_file(title_file, title_list)
    print("Finished parsing column title")
    write_to_file(date_file, date_list)
    print("Finished parsing column date")
    write_to_file(author_file, author_list)
    print("Finished parsing column author")
    write_to_file(category_file, category_list)
    print("Finished parsing column category")
    write_to_file(post_url_file, post_url_list)
    print("Finished parsing column post_url")
    write_to_file(comments_url_file, comments_url_list)
    print("Finished parsing column comments_url")
    write_to_file(num_comments_file, num_comments_list)
    print("Finished parsing column num_comments")
    write_to_file(num_outlinks_file, num_outlinks_list)
    print("Finished parsing column num_inlinks")
    write_to_file(num_inlinks_file, num_inlinks_list)
    print("Finished parsing column num_outlinks")
    write_to_file(post_length_file, post_length_list)
    print("Finished parsing column post_length")
    write_to_file(post_text_file, post_text_list)
    print("Finished parsing column post_text")

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

def add_tokens():
    """Return a posting list of all unique words in the collection."""

    # consider only title, data, author, category and post_text columns
    # reason: the url columns contain redundant information (title) & other columns are
    # numbers not useful to the vector space model

    title_file = "TUAW-dataset/data/title.txt"
    date_file = "TUAW-dataset/data/date.txt"
    author_file = "TUAW-dataset/data/author.txt"
    category_file = "TUAW-dataset/data/category.txt"
    post_text_file = "TUAW-dataset/data/post_text.txt"

    posting_list = {}
    stemmer = PorterStemmer()
    stopwords_set = set(stopwords.words("english"))

    doc_id = -1
    total_num_docs = 0

    # read the same line of the files together
    # open(date_file) as date_fd, \
    with open(title_file) as title_fd, \
        open(author_file) as author_fd, \
        open(category_file) as category_fd, \
        open(post_text_file) as post_text_fd:
        lines = zip(title_fd, author_fd, category_fd, post_text_fd)
        for line in lines:
            total_num_docs += 1
            doc_id += 1 # == line_num
            if doc_id % 1000 == 999:
            	print("Processed " + str(doc_id + 1) + " posts")
            
            # title + author + category + post_text
            line_string = line[0].strip() + " " + line[1].strip() + " " + line[2].strip() + " " + line[3].strip()
            
            # normalize the terms in the line == post
            term_list = normalize(line_string, stemmer, stopwords_set) 
            
            # add every word to posting list
            for word in term_list:
                # type(posting list) == { term: [df, {doc_id: tf}] }
                if word in posting_list:
                    doc_dict = posting_list[word][1]
                    if doc_id in doc_dict:
                        doc_dict[doc_id] = doc_dict[doc_id] + 1
                    else:
                        posting_list[word][0] += 1
                        doc_dict[doc_id] = 1
                elif len(word) > 0: # add only words of non-zero length, check again
                    temp_dict = {}
                    temp_dict[doc_id] = 1
                    posting_list[word] = [1, temp_dict]
    
    return (total_num_docs, posting_list)

def create_index():
    """Create an inverted index from raw data and save it to disk."""

    print("Normalizing columns title, !date, author, category and post_text...")
    (total_num_docs, posting_list) = add_tokens()
    print("Done")

    # sort based on key values == terms
    sorted_posting_list = OrderedDict( sorted(posting_list.items(), key=lambda t: t[0]) )

    # computed average length of posting list = 27.17
    # sum_length = 0
    # n = 0
    # for term, df_tf_list in sorted_posting_list.items():
    #   sum_length += len(df_tf_list[1])
    #   if df_tf_list[0] != sum(df_tf_list[1].values()):
    #       print(str(n+1))
    #       break
    #   n +=1
    # print(sum_length / n)

    # posting_list_file
    term_file = "TUAW-dataset/data/term.txt"

    print("Generating inverted index...", end=" ")

    # for lookup during query processing
    # map: term -> line in term_file, the posting list for the term can be retrieved
    # by reading the corresponding line
    term_line_num_file = "TUAW-dataset/data/term_line_num.txt"
    line_num_dict = {}
    current_line = 0

    # store posting_list
    with open(term_file, mode="w", encoding="utf-8") as f:
        for key, value in sorted_posting_list.items():
            line_num_dict[key] = current_line
            f.write(str(key) + ":" + str(value) + "\n")
            current_line += 1

    # store line number lookup
    with open(term_line_num_file, mode="w", encoding="utf-8") as f:
        f.write(str(total_num_docs) + "\n")
        for term, line_num in line_num_dict.items():
            f.write(str(term) + " " + str(line_num) + "\n")

    print("Done")

def main():
    start = time.clock()
    parse_html_entities()
    parse_csv()
    create_index()
    end = time.clock()
    print("Index constructed in " + str(end - start) + " seconds. Ready to search.")
    print("Search using: ./search.py \"query\" [k]")

if __name__ == "__main__":
    main()