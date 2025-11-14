import os
import re
import json

from enum import Enum
from dataclasses import dataclass
from functools import reduce
from typing import Dict, List, Iterable, Generator, TextIO

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
DOCUMENT_DB_PATH = "webscraper/documents_meta.json"
DOCUMENTS_ROOT = "webscraper/documents/"

class SearchType(Enum):
    BASIC = "basic"
    REGEX = "regex"


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


def index(documents_root: str) -> SearchIndex:
    index: SearchIndex = dict()

    for i, fn in enumerate(os.listdir(documents_root)):
        print("Indexing file number", i)
        document_id = _document_id_from_filename(fn)

        with open(os.path.join(documents_root, fn)) as f:
            for term in _term_generator(f):
                if _indexable(term):
                    _increment_term_for_document(index, term, document_id)


    return index


def term_search(db: DocumentDB, index: SearchIndex, term: Term) -> SearchHits:
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


def basic_search(db: DocumentDB, index: SearchIndex, query: str) -> SearchHits:
    # Like term search, but make value total of all occurrences of terms
    print("Starting basic search")
    query_terms = list(_str_term_generator(query))
    print("query terms:", query_terms)
    term_hits = [term_search(db, index, term) for term in query_terms]
    print("term hits:", term_hits)
    merged = _merge_all_hits(term_hits)
    print("merged hits:", merged)
    return merged


def regex_search(db: DocumentDB, index: SearchIndex, regex: str) -> SearchHits:
    r = re.compile(regex)
    regex_hits = [term_search(db, index, term) for term in index.keys() if r.match(term)]
    return _merge_all_hits(regex_hits)


def to_result(db: DocumentDB, hits: SearchHits) -> SearchResult:
    sorted_hits = sorted(hits.items(), key=lambda item: -item[1])
    result: SearchResult = []
    for doc_id, _ in sorted_hits:
        result.append(db[doc_id])
    return result


# TODO: Cache
def read_search_db() -> DocumentDB:
    print("Reading search db...")
    with open(DOCUMENT_DB_PATH, encoding="utf-8") as fp:
        documents_meta = json.load(fp)

    db: DocumentDB = dict()
    for meta in documents_meta:
        doc_id = meta.pop("id")
        db[doc_id] = meta
    return db


# TODO: Cache
def read_search_index() -> SearchIndex:
    print("Reading search index...")
    if os.path.exists(SEARCH_INDEX_PATH):
        with open(SEARCH_INDEX_PATH) as fp:
            return json.load(fp)
    else:
        print("Indexing...")
        search_index = index(DOCUMENTS_ROOT)
        print("Finished indexing, opening and writing...")
        with open(SEARCH_INDEX_PATH, "w") as fp:
            json.dump(search_index, fp)
        return search_index


def execute_search(query: str, type: SearchType) -> SearchResult:
    db = read_search_db()
    index = read_search_index()

    print("Executing search...")
    if type == SearchType.BASIC:
        hits = basic_search(db, index, query)
        result = to_result(db, hits)
        print("finalized result:", result)
        return result
    if type == SearchType.REGEX:
        hits = regex_search(db, index, query)
        return to_result(db, hits)
    return []


def fetch_document(doc_id: DocumentId) -> str:
    with open(os.path.join(DOCUMENTS_ROOT, f"{doc_id}.txt")) as f:
        return f.read()
