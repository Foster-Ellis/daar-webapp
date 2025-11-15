import os
import re
import json

from enum import Enum
from dataclasses import dataclass
from functools import reduce, cache
from typing import Dict, List, Iterable, Generator, TextIO, Tuple

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

DocumentDB = Dict[DocumentId, DocumentMeta]
SearchScore = np.float64
# SearchHits = Dict[DocumentId, SearchScore]
SearchHits = pd.DataFrame # row = document id, col = term, limited rows
SearchResult = List[DocumentMeta]

SEARCH_INDEX_PATH = "search/search_index.json"
DATAFRAME_PATH = "search/tfidf_df.csv"
DOCUMENT_DB_PATH = "webscraper/documents_meta.json"
DOCUMENTS_ROOT = "webscraper/documents/"

class SearchType(Enum):
    BASIC = "basic"
    REGEX = "regex"


class SearchRanking(Enum):
    OCCURRENCES = "occurrences"
    CLOSENESS = "closeness"


def _document_id_from_filename(fn: str) -> int:
    [doc_id, _] = fn.split(".")
    return int(doc_id)


def _term_generator(f: TextIO) -> Generator[Term]:
    for line in f:
        for term in _str_term_generator(line):
            yield term


def _str_term_generator(s: str) -> Generator[Term]:
    # Normalize line by turning to lowercase, and removing any punctuation
    formatted_line = re.sub(r'[^a-z0-9 ]', '', s.lower())
    for word in formatted_line.split():
        yield word


# TODO: Implement
def _indexable(term: str) -> bool:
    return True


def _increment_term_for_document(index: SearchIndex, term: Term, document_id: DocumentId) -> None:
    if term not in index:
        index[term] = dict()
    if document_id not in index[term]:
        index[term][document_id] = 0
    index[term][document_id] += 1


@cache
def index(documents_dir: str) -> Tuple[TfidfVectorizer, SearchIndex]:
    # This gives a matrix that maps doc id to vector of term TFIDF, which can maybe also be accessed by label for convenience
    # What I want:
    # - matrix to look up term,

    text_files = glob.glob(f"{documents_dir}/*.txt")
    text_titles = [Path(text).stem for text in text_files]

    tfidf_vectorizer = TfidfVectorizer(input='filename', stop_words='english', max_features=100_000)
    tfidf_vector = tfidf_vectorizer.fit_transform(text_files)
    tfidf_df = pd.DataFrame(tfidf_vector.toarray(), index=text_titles, columns=tfidf_vectorizer.get_feature_names_out())
    return tfidf_vectorizer, tfidf_df
    # return pd.DataFrame()


def term_search(index: SearchIndex, terms: List[Term]) -> SearchHits:
    # Get at most 100 results
    return index.nlargest(100, terms)


def _merge_hits(r1: SearchHits, r2: SearchHits) -> SearchHits:
    merged = dict(r1)
    for key, score in r2.items():
        if key not in merged:
            merged[key] = score
        else:
            merged[key] += score
    return merged


def _merge_all_hits(hits: Iterable[SearchHits]) -> SearchHits:
    return reduce(lambda agg, hit: _merge_hits(agg, hit), hits)


def basic_search(vectorizer: TfidfVectorizer, index: SearchIndex, query: str) -> SearchHits:
    # Like term search, but make value total of all occurrences of terms
    print("Starting basic search")
    analyze = vectorizer.build_analyzer()
    query_terms = analyze(query)
    return term_search(index, query_terms)


def regex_search(index: SearchIndex, regex: str) -> SearchHits:
    r = re.compile(regex)
    matching_terms = [term for term in index.columns if r.match(term)]
    return term_search(index, matching_terms)


def to_result(db: DocumentDB, tfidf_df: SearchIndex, hits: SearchHits, ranking: SearchRanking, query) -> SearchResult:
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
            result.append(db[int(doc_id)])

        sorted_hits = [(score, doc_id) for doc_id, score in sorted(hits.items(), key=lambda item: -item[1])]
    elif ranking == SearchRanking.CLOSENESS:
        sorted_hits: List[Tuple[float, DocumentId]] = closeness_centrality_ranking(tfidf_df, hits)

    # print("Got sorted hits", sorted_hits)

    for _, doc_id in sorted_hits:
        result.append(db[doc_id])
    # print("Final result", result)
    return result


@cache
def read_search_db() -> DocumentDB:
    print("Reading search db...")
    with open(DOCUMENT_DB_PATH, encoding="utf-8") as fp:
        documents_meta = json.load(fp)

    db: DocumentDB = dict()
    for meta in documents_meta:
        doc_id = meta.pop("id")
        db[doc_id] = meta
    return db


@cache
def read_search_index() -> Tuple[TfidfVectorizer, SearchIndex]:
    print("Indexing...")
    # if os.path.exists(SEARCH_INDEX_PATH):
    #     print("Loading index...")
    #     with open(SEARCH_INDEX_PATH, encoding="utf-8") as fp:
    #         search_index = json.load(fp)
    #     # tfidf_df = pd.read_csv(DATAFRAME_PATH)
    #     print("Loading dataframe...")
    #     tfidf_df = get_tfidf_df()
    #     print("Done loading")
    #     return (search_index, tfidf_df)
    # else:
    #     print("Indexing...")
    #     search_index, tfidf_df = index(DOCUMENTS_ROOT)
    #     print("Finished indexing, opening and writing...")
    #     with open(SEARCH_INDEX_PATH, "w", encoding="utf-8") as fp:
    #         json.dump(search_index, fp)
    #     tfidf_df.to_csv(DATAFRAME_PATH, encoding="utf-8")
    #     return (search_index, tfidf_df)
    return index(DOCUMENTS_ROOT)


def execute_search(query: str, type: SearchType, ranking: SearchRanking) -> SearchResult:
    db = read_search_db()
    vectorizer, tfidf_df = read_search_index()

    print("Executing search...")
    if type == SearchType.BASIC:
        hits = basic_search(vectorizer, tfidf_df, query)
    elif type == SearchType.REGEX:
        hits = regex_search(tfidf_df, query)

    result = to_result(db, tfidf_df, hits, ranking)
    # print("finalized result:", result)
    return result


def fetch_document(doc_id: DocumentId) -> str:
    with open(os.path.join(DOCUMENTS_ROOT, f"{doc_id}.txt"), encoding="utf-8") as f:
        return f.read()


def cosine_similarity(vec1: pd.DataFrame, vec2: pd.DataFrame) -> np.float64:
    """
    https://medium.com/@whyamit404/what-is-cosine-similarity-and-why-use-numpy-62d409f0661f
    """
    dot_product = np.dot(vec1, vec2)
    magnitude1 = np.linalg.norm(vec1)
    magnitude2 = np.linalg.norm(vec2)
    return dot_product / (magnitude1 * magnitude2)


def closeness_centrality_ranking(tfidf_df: pd.DataFrame, hits: SearchHits) ->  List[Tuple[float, DocumentId]]:
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

    # TODO: Do as a dataframe to hopefully parallelize
    distance_matrix: Dict[DocumentId, List[float]] = dict()
    for i, doc_id_1 in enumerate(hits):
        print("Calculating array number", i)
        distance_matrix[doc_id_1] = []

        for doc_id_2 in hits:
            distance_matrix[doc_id_1].append(cosine_similarity(tfidf_df.loc[str(doc_id_1)], tfidf_df.loc[str(doc_id_2)]))

    print("Got distance matrix")
    distance_df = pd.DataFrame.from_dict(data=distance_matrix, orient="index")
    print("Got distance df")
    ranking = sorted([(-np.sum(distance_df.loc[doc_id]), doc_id) for doc_id in hits])
    print("Got ranking (top 10)", ranking[:10])

    return ranking
