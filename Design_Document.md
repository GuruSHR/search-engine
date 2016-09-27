##Data

The files produced by running the program are shown below.

    TUAW-dataset/
      data/
          * input file *
          posts.csv         :   Original data file

          * output files, created by building index *
          clean_posts.csv   :   Original data file with SGML special characters 
                                removed / replaced with utf-8 equivalents

          * each line corresponds to one post = one document, we take doc_id = line number *
          author.txt        :   blogger name (author of post)
          category.txt      :   categories of post
          comments_url.txt  :   url of comments of post
          date.txt          :   date and time of posting post
          num_comments.txt  :   number of comments for post
          num_inlinks.txt   :   number of inbound links to post
          num_outlinks.txt  :   number of outbound links from post
          post_length.txt   :   length of post body (before encoding in utf-8)
          post_text.txt     :   body of post (after encoding in utf-8)
          post_url.txt      :   url of post
          title.txt         :   title of post

          term.txt          :   posting list of unique terms occuring in the collection
          term_line_num.txt :   1st line = number of documents in collection, the rest 
                                are a mapping from unique term to the line number in term.txt

##Index construction

We consider each post to be a document and each word to be a token. We use the title, category, post body and author of the post for index construction. Reasons:

1. URL data is subset of date + title.
2. The number of comments, inlinks, outlinks and post_length are metadata not known to a user.
3. A user typically specifies date range separately.

###Procedure

1. Convert `posts.csv` to `clean_posts.csv`.
2. Split `clean_posts.csv` into 11 files: 1 for each attribute.
3. Get unique terms after tokenization, stopword removal & stemming.
4. For every unique term, find the posting list.
5. The data Structure of posting list is `{ term (str) : [df (int) , { doc_id (int) : tf (int) } ] }` i.e., a dictionary with the unique terms as its keys and its values as a pair of
    * document frequency of the term (`df`) &
    * a dictionary containing, all the `doc_ids` of the documents containing the term as keys, with the term frequency (`tf`) of the term in each document as values.
    * `doc_id` of a document is the same as the line number of its post in `posts.csv`
6. This is stored in the file `term.txt`.
7. When we search for a term in the query, we retrieve only the posting list of that term from disk. Therefore, we also save to disk the pair `{ term (str) , line number in "term.txt" (int) }` in the file `term_line_num.txt` so that we may retrieve the corresponding line as required.

##Procedure for Ranking

1. We use two parameters to calculate the score of a document
    1. fraction of inlinks to the document,
    2. cosine similarity of the document vector with the query vector (`ddd.qqq = lnc.ltc`).
2. The relative importance of these two weights is controlled by a parameter `alpha` which is by default set to 0.5.
    
        final score = alpha * fraction of inlinks + (1 - alpha) * cosine similarity

##Procedure for Searching

1. Get search query & number of results to display (`k`) from user.
2. Apply tokenization, stopword removal & stemming to the query.
3. Retrieve the posting list of the query terms from `term.txt` using the line numbers stored in the file `term_line_num.txt`.
4. Find the score for each document and rank them in non-decreasing order.
5. Display the top `k` results.

###Recall

All documents containing the term in the query are retrieved even though only the top k entries are displayed.
Therefore recall = 1

###Precision

The relevance of documents to the query is unknown as there is no ground truth in this dataset (i.e., it is 
unlabeled). Therefore precision cannot be calculated.