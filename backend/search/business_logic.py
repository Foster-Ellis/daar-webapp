import os
import re
import json

from enum import Enum
from dataclasses import dataclass
from functools import reduce, cache
from typing import Dict, List, Iterable, Generator, TextIO, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
from pathlib import Path
import glob

Term = str # normalized: [a-zA-Z]
DocumentId = int

SearchIndex = Dict[Term, Dict[DocumentId, int]] # term => document id => occurrence count


@dataclass
class DocumentMeta:
    title: str
    document_id: DocumentId
    cover: str # URL

DocumentDB = Dict[DocumentId, DocumentMeta]
SearchScore = int
SearchHits = Dict[DocumentId, SearchScore]
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
def get_tfidf_df() -> pd.DataFrame:
    # text_files = glob.glob(f"{DOCUMENTS_ROOT}/*.txt")
    # text_titles = [Path(text).stem for text in text_files]

    # tfidf_vectorizer = TfidfVectorizer(input='filename', stop_words='english')
    # tfidf_vector = tfidf_vectorizer.fit_transform(text_files)
    # tfidf_df = pd.DataFrame(tfidf_vector.toarray(), index=text_titles, columns=tfidf_vectorizer.get_feature_names_out())
    # return tfidf_df
    return pd.DataFrame()


def index(documents_root: str) -> Tuple[SearchIndex, pd.DataFrame]:
    # Old index
    index: SearchIndex = dict()

    for i, fn in enumerate(os.listdir(documents_root)):
        print("Indexing file number", i)
        document_id = _document_id_from_filename(fn)

        with open(os.path.join(documents_root, fn), encoding="utf-8") as f:
            for term in _term_generator(f):
                if _indexable(term):
                    _increment_term_for_document(index, term, document_id)

    # TFIDF DataFrame
    tfidf_df = get_tfidf_df()

    return (index, tfidf_df)


def term_search(index: SearchIndex, term: Term) -> SearchHits:
    return index[term]


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


def basic_search(index: SearchIndex, query: str) -> SearchHits:
    # Like term search, but make value total of all occurrences of terms
    print("Starting basic search")
    query_terms = list(_str_term_generator(query))
    print("query terms:", query_terms)
    term_hits = [term_search(index, term) for term in query_terms]
    print("term hits:", term_hits)
    merged = _merge_all_hits(term_hits)
    print("merged hits:", merged)
    return merged


def regex_search(index: SearchIndex, regex: str) -> SearchHits:
    r = re.compile(regex)
    regex_hits = [term_search(index, term) for term in index.keys() if r.match(term)]
    return _merge_all_hits(regex_hits)


def to_result(db: DocumentDB, tfidf_df: pd.DataFrame, hits: SearchHits, ranking: SearchRanking) -> SearchResult:
    print("Converting to result with ranking", ranking, "and hits", hits)
    if ranking == SearchRanking.OCCURRENCES:
        sorted_hits = [(score, doc_id) for doc_id, score in sorted(hits.items(), key=lambda item: -item[1])]
    elif ranking == SearchRanking.CLOSENESS:
        sorted_hits: List[Tuple[float, DocumentId]] = closeness_centrality_ranking(tfidf_df, hits)

    print("Got sorted hits", sorted_hits)
    result: SearchResult = []
    for _, doc_id in sorted_hits:
        result.append(db[doc_id])
    print("Final result", result)
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
def read_search_index() -> Tuple[SearchIndex, pd.DataFrame]:
    print("Reading search index...")
    if os.path.exists(SEARCH_INDEX_PATH):
        print("Loading index...")
        with open(SEARCH_INDEX_PATH, encoding="utf-8") as fp:
            search_index = json.load(fp)
        # tfidf_df = pd.read_csv(DATAFRAME_PATH)
        print("Loading dataframe...")
        tfidf_df = get_tfidf_df()
        print("Done loading")
        return (search_index, tfidf_df)
    else:
        print("Indexing...")
        search_index, tfidf_df = index(DOCUMENTS_ROOT)
        print("Finished indexing, opening and writing...")
        with open(SEARCH_INDEX_PATH, "w", encoding="utf-8") as fp:
            json.dump(search_index, fp)
        tfidf_df.to_csv(DATAFRAME_PATH, encoding="utf-8")
        return (search_index, tfidf_df)


def execute_search(query: str, type: SearchType, ranking: SearchRanking) -> SearchResult:
    db = read_search_db()
    index, tfidf_df = read_search_index()

    print("Executing search...")
    if type == SearchType.BASIC:
        hits = basic_search(index, query)
    elif type == SearchType.REGEX:
        hits = regex_search(index, query)

    result = to_result(db, tfidf_df, hits, ranking)
    print("finalized result:", result)
    return result


def fetch_document(doc_id: DocumentId) -> str:
    with open(os.path.join(DOCUMENTS_ROOT, f"{doc_id}.txt"), encoding="utf-8") as f:
        return f.read()


def cosine_similarity(vec1: pd.DataFrame, vec2: pd.DataFrame) -> np.float64:
    """
    https://melaniewalsh.github.io/Intro-Cultural-Analytics/05-Text-Analysis/03-TF-IDF-Scikit-Learn.html
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
    """
    # print("Running closeness centrality ranking on hits", hits)

    # TODO: Do as a dataframe to hopefully parallelize
    distance_matrix: Dict[DocumentId, List[float]] = dict()
    for doc_id_1 in hits:
        distance_matrix[doc_id_1] = []

        for doc_id_2 in hits:
            # print("Doing for doc1 and doc2", doc_id_1, doc_id_2)
            distance_matrix[doc_id_1].append(cosine_similarity(tfidf_df.loc[str(doc_id_1)], tfidf_df.loc[str(doc_id_2)]))

    # print("Got distance matrix", distance_matrix)
    distance_df = pd.DataFrame.from_dict(data=distance_matrix, orient="index")
    # print("Got distance df", distance_df)
    ranking = sorted([(np.sum(distance_df.loc[doc_id]), doc_id) for doc_id in hits])
    # print("Got ranking", ranking)

    return ranking
