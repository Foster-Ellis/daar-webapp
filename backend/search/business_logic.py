import os

from pathlib import Path
from typing import Dict, Generator, TextIO

Term = str # normalized: [a-zA-Z]
DocumentId = int

SearchIndex = Dict[Term, Dict[DocumentId, int]] # term => document id => occurrence count


def _document_id_from_filename(fn: str) -> int:
    [doc_id, _] = fn.split(".")
    return int(doc_id)


# TODO: Implement
def _term_generator(f: TextIO) -> Generator[Term]:
    i = 0
    while i < 10:
        yield "hi"


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

        with open(fn) as f:
            for term in _term_generator(f):
                if _indexable(term):
                    _increment_term_for_document(index, term, document_id)


    return index
