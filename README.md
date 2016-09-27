#IR class project - ranked retrieval using vector space model

* Author: Hariram S
* Date: 2016-09-27
* Version: 1.0.0
* Dataset: TUAW - Social Computing Data Repository
* Data source: http://socialcomputing.asu.edu/datasets/TUAW

##Requirements

Tested using:
* python v3.5.2
* porterstemmer.py source: https://tartarus.org/martin/PorterStemmer/
* nltk v3.2.1
* nltk data:
    * punkt (Punkt Tokenizer Models)
    * stopwords (Stopwords Corpus)

##Usage

1. Run `2to3 porterstemmer.py` to make the stemmer compatible with 
   python 3 (if not done already)
2. Run `build_index.py` to construct an inverted index from the data.
3. Run `search.py "your query" [ k ]` to get top `k` results (default `k = 10`).