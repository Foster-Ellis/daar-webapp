import os
import re
import json

from enum import Enum
from dataclasses import dataclass
from functools import cache
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
from pathlib import Path
import glob

Term = str # normalized: [a-zA-Z]
DocumentId = int

# SearchIndex = Dict[Term, Dict[DocumentId, int]] # term => document id => occurrence count
SearchIndex = pd.DataFrame # row = document id, col = term

@dataclass
class DocumentMeta:
    title: str
    document_id: DocumentId
    cover: str # URL

DocumentDB = Dict[str, DocumentMeta] # should be DocumentId => DocumentMeta, but documents_meta.json stores ids as strings by accident
SearchScore = np.float64
# SearchHits = Dict[DocumentId, SearchScore]
SearchHits = pd.DataFrame # row = document id, col = term, limited rows
SearchResult = List[DocumentMeta]

SEARCH_INDEX_PATH = "search/search_index.json"
DATAFRAME_PATH = "search/tfidf_df.csv"
DOCUMENT_DB_PATH = "webscraper/documents_meta.json"
DOCUMENTS_ROOT = "webscraper/documents/"

MAX_RESULTS = 50

DOC_TOKENS = {}


class SearchType(Enum):
    BASIC = "basic"
    REGEX = "regex"


class SearchRanking(Enum):
    OCCURRENCES = "occurrences"
    CLOSENESS = "closeness"


@cache
def index(documents_dir: str) -> SearchIndex:
    print("Indexing...")
    text_files = glob.glob(f"{documents_dir}/*.txt")
    text_titles = [Path(text).stem for text in text_files]

    print("Building TF-IDF matrix...")
    tfidf_vectorizer = TfidfVectorizer(input='filename', stop_words='english', max_features=100_000)
    tfidf_vector = tfidf_vectorizer.fit_transform(text_files)
    tfidf_df = pd.DataFrame(tfidf_vector.toarray(), index=text_titles, columns=tfidf_vectorizer.get_feature_names_out())
    return tfidf_df

tfidf_df = index(DOCUMENTS_ROOT)


def term_search(index: SearchIndex, terms: List[Term]) -> SearchHits:
    print("Doing term search with terms", terms)
    # Cap results
    hits = index.nlargest(MAX_RESULTS, terms)
    # Only return rows for which there was actually a hit
    return hits[hits[terms].T.any()]


def basic_search(index: SearchIndex, query: str) -> SearchHits:
    print("Starting basic search")
    vectorizer = CountVectorizer(stop_words="english")
    analyze = vectorizer.build_analyzer()
    query_terms = analyze(query)
    return term_search(index, query_terms)


def regex_search(index: SearchIndex, regex: str) -> SearchHits:
    r = re.compile(regex)
    matching_terms = [term for term in index.columns if r.match(term)]
    return term_search(index, matching_terms)


def to_result(db: DocumentDB, hits: SearchHits, ranking: SearchRanking) -> SearchResult:
    # IDEA:
    # - Iterate through hits and take only those with at least some kind of hit on a term (since we take 100 no matter what)
    # - End up with the term vector for each of those hits
    # - Run ranking algorithm on those hits
    #   * IF occurrences: rank by TFIDF total for query terms
    #   * IF closeness: run closeness algorithm on remaining term vectors
    # - Get metadata for sorted results and return
    result: SearchResult = []

    print("Converting to result with ranking", ranking, "and hits", hits)
    if ranking == SearchRanking.OCCURRENCES:
        for doc_id, _series in hits.iterrows():
            result.append(db[doc_id])
    elif ranking == SearchRanking.CLOSENESS:
        sorted_hits: List[Tuple[float, DocumentId]] = closeness_centrality_ranking(hits)
        for _, doc_id in sorted_hits:
            result.append(db[doc_id])

    # print("Final result", result)
    return result


@cache
def read_search_db() -> DocumentDB:
    print("Reading search db...")
    with open(DOCUMENT_DB_PATH, encoding="utf-8") as fp:
        documents_meta = json.load(fp)

    print("Converting to dict...")
    db: DocumentDB = dict()
    for meta in documents_meta:
        doc_id = meta.pop("id")
        db[doc_id] = meta
    print("finished reading search db")
    return db
read_search_db()

@cache
def load_doc_tokens():
    """
    Preload and cache token-sets for all document .txt files.

    IDEA:
    - Use CountVectorizer's analyzer to create a consistent tokenizer
      shared by both indexing and query-recommendation logic.
    - For each document in DOCUMENTS_ROOT:
        * Read the raw text
        * Tokenize it into a set of unique tokens
        * Store it in global DOC_TOKENS under its document ID
    - Cache the whole mapping so that repeated calls are effectively free.

    Notes:
    - Token data is stable unless the documents change on disk.
    - Using @cache ensures the expensive I/O + tokenization only runs once.
    """
    global DOC_TOKENS
    
    print("Loading document tokens...")
    vectorizer = CountVectorizer(stop_words="english")
    analyze = vectorizer.build_analyzer()

    print("Analyzing documents...")
    txt_files = glob.glob(f"{DOCUMENTS_ROOT}/*.txt")
    for path in txt_files:
        doc_id = Path(path).stem
        with open(path, encoding="utf-8") as f:
            text = f.read()
        DOC_TOKENS[doc_id] = set(analyze(text))
    print("Done loading document tokens")
    return DOC_TOKENS


# initialize cache of doc tokens for later use by calling method directly during module import
# otherwise, we would have to call it every time hence using @cahce is important
load_doc_tokens() 



def execute_search(query: str, type: SearchType, ranking: SearchRanking) -> SearchResult:
    db = read_search_db()
    

    print("Executing search...")
    if type == SearchType.BASIC:
        hits = basic_search(tfidf_df, query)
    elif type == SearchType.REGEX:
        hits = regex_search(tfidf_df, query)

    result = to_result(db, hits, ranking)
    # print("finalized result:", result)
    return result


def fetch_document(doc_id: DocumentId) -> str:
    with open(os.path.join(DOCUMENTS_ROOT, f"{doc_id}.txt"), encoding="utf-8") as f:
        return f.read()


def cosine_similarity(vec1: pd.Series, vec2: pd.Series) -> np.float64:
    """
    https://medium.com/@whyamit404/what-is-cosine-similarity-and-why-use-numpy-62d409f0661f
    """
    dot_product = np.dot(vec1, vec2)
    magnitude1 = np.linalg.norm(vec1)
    magnitude2 = np.linalg.norm(vec2)
    return dot_product / (magnitude1 * magnitude2)


def closeness_centrality_ranking(hits: SearchHits) ->  List[Tuple[float, DocumentId]]:
    """
    A closeness centrality orders the results by minimial total distance to
    all other nodes.

    IDEA:
    - calculate term vector for each result
    - term vector is term index => TFIDF for each term
      * means we need a central authority mapping term to vector index
      * seems we can do this with TFIDFVectorizor
    - Compute distance between each pair of vectors (pandas should let us do this easy)
    - Return ordered by min average distance

    Note: This doesn't actually take the query into account, funny enough.

    https://melaniewalsh.github.io/Intro-Cultural-Analytics/05-Text-Analysis/03-TF-IDF-Scikit-Learn.html
    """
    print("Running closeness centrality ranking on", len(hits), f"hits ({len(hits)**2} combinations)")

    distance_matrix: Dict[DocumentId, List[float]] = dict()
    for doc_id_1, series_1 in hits.iterrows():
        distance_matrix[doc_id_1] = []

        for _doc_id_2, series_2 in hits.iterrows():
            distance_matrix[doc_id_1].append(cosine_similarity(series_1, series_2))

    print("Got distance matrix")
    distance_df = pd.DataFrame.from_dict(data=distance_matrix, orient="index")
    print("Got distance df")
    ranking = sorted([(-np.sum(distance_series), doc_id) for doc_id, distance_series in distance_df.iterrows()])
    print("Got ranking (top 10)", ranking[:10])

    return ranking



def get_recommendations_for_query(query: str):
    """
    Compute simple Jaccard-based recommendations for a given query.

    IDEA:
    - Tokenize the input query using a standard analyzer (CountVectorizer)
    - Compare the query token-set with each document's token-set
    - Use Jaccard similarity:  |A ∩ B| / |A ∪ B|
    - Keep only documents with non-zero similarity
    - Return the top N highest-scoring docs
    
    """
    load_doc_tokens()  # ensure DOC_TOKENS is populated

    vectorizer = CountVectorizer(stop_words="english")
    analyze = vectorizer.build_analyzer()
    
    query_tokens = set(analyze(query))

    scores = []
    for doc_id, tokens in DOC_TOKENS.items():
        inter = len(query_tokens & tokens)
        union = len(query_tokens | tokens)
        if union == 0:
            continue
        
        j = inter / union
        if j > 0:
            scores.append((doc_id, j))

    scores.sort(key=lambda x: x[1], reverse=True)
    top = [doc_id for doc_id, _ in scores[:8]]

    db = read_search_db()
    recommendations = [ db[doc_id] for doc_id in top ]

    return recommendations
