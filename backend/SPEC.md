# WISHLIST
* API
  - POST /term_search : (s: String) -> List[DocumentMeta]
    * Q: How does this handle multiple terms being given as the string? Project doc gives such examples, but the description of this functionality would imply that a single term is being searched for.

  - POST /regex_search : (s: RegexString) -> List[DocumentMeta]
    * Fast version attempts to match the regex against the index table rather than against all full-texts

  - GET /document/:id : (id: DocumentId) -> DocumentText
    * Get document text by document ID


* Backend functionaltiy
  - index: () -> SearchIndex
    * Re-index all files
    * Store on disk so that we don't need to re-index on server restart
    * Run when documents are added or removed. Since we don't have any kind of API for this, maybe can just check on start-up if documents list is the same as what we indexed on, and re-index if not.

  - search: (db: DocumentDB, index: SearchIndex, t: Term) -> SearchResult

  - search: (db: DocumentDB, index: SearchIndex, s: String) -> SearchResult
    * Search a composition of terms

  - search: (db: DocumentDB, index: SearchIndex, r: RegEx) -> SearchResult

  - rank: (index: SearchIndex, v: DocumentId) -> float
    * Can be closeness, betweenness, or page_rank (?)
    * Can start simply with occurrence count for MVP but need one of the above for final product
    * Could implement any number of strategies which use the same signature

  - some kind of recommendation feature


# TYPES

## Backend

DocumentDB = Dict[DocumentId, DocumentMeta]

SearchIndex = Dict[Term, List[DocumentTerm]] # serialize to JSON
Term = str # normalized: [a-zA-Z]
DocumentTerm = Struct { occurrences: int, document_id: DocumentId }

SearchResult = List[DocumentMeta]

DocumentId = int
DocumentMeta = Struct { title: str, id: DocumentId, cover: URL }
DocumentText = str


Q: I figure we can't use ElasticSearch for this?
Q: Should we use our RegEx implementation from project 1 for this?
