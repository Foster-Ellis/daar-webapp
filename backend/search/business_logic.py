import os
import re

from pathlib import Path
from typing import Dict, Generator, TextIO

Term = str # normalized: [a-zA-Z]
DocumentId = int

SearchIndex = Dict[Term, Dict[DocumentId, int]] # term => document id => occurrence count


def _document_id_from_filename(fn: str) -> int:
    [doc_id, _] = fn.split(".")
    return int(doc_id)


def _term_generator(f: TextIO) -> Generator[Term]:
    for line in f:
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


if __name__ == "__main__":
    from itertools import islice

    def take(n, iterable):
        """Return the first n items of the iterable as a list."""
        return list(islice(iterable, n))

    ind = index(Path("/Users/graham.preston/fac_src/DAAR/project3/documents"))
    n_items = take(5, ind.items())
    print(n_items)
