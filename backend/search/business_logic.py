import os
import re

from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Dict, Generator, TextIO

Term = str # normalized: [a-zA-Z]
DocumentId = int

SearchIndex = Dict[Term, Dict[DocumentId, int]] # term => document id => occurrence count


@dataclass
class DocumentMeta:
    title: str
    document_id: DocumentId
    cover: URL

DocumentDB = Dict[DocumentId, DocumentMeta]
SearchScore = int
SearchHits = Dict[DocumentId, SearchScore]
SearchResult = List[Tuple[DocumentMeta]]

def _document_id_from_filename(fn: str) -> int:
    [doc_id, _] = fn.split(".")
    return int(doc_id)


def _term_generator(f: TextIO) -> Generator[Term]:
    for line in f:
        for term in _str_term_generator(line):
            yield term


def _str_term_generator(s: str) -> Generator[Term]:
    # Normalize line by turning to lowercase, and removing any punctuation
    formatted_line = re.sub(r'[^a-z0-9 ]', '', line.lower())
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


def index(documents_root: Path) -> SearchIndex:
    index: SearchIndex = dict()

    for fn in os.listdir(documents_root):
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
    query_terms = list(_str_term_generator(query))
    term_hits = [term_search(db, index, term) for term in query_terms]
    return _merge_all_hits(term_hits)


def regex_search(db: DocumentDB, index: SearchIndex, regex: str) -> SearchHits:
    r = re.compile(regex)
    regex_hits = [term_search(db, index, term) for term in index.keys() if r.match(term)]
    return _merge_all_hits(regex_hits)


def to_result(db: DocumentDB, hits: SearchHits) -> SearchResult:
    sorted_hits = sorted(hits.items(), key=lambda item: -item[1])
    return [(db[document_id], score) for (document_id, score) in sorted_hits]


if __name__ == "__main__":
    from itertools import islice

    def take(n, iterable):
        """Return the first n items of the iterable as a list."""
        return list(islice(iterable, n))

    ind = index(Path("/Users/graham.preston/fac_src/DAAR/project3/documents"))
    n_items = take(5, ind.items())
    print(n_items)
