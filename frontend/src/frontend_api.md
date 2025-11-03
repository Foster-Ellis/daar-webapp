


# FRONTEND API SPECIFICATION

* Vue Frontend interacts with backend REST API via **Axios**.
* All endpoints return **JSON**.
* Base URL: `http://127.0.0.1:8000/api`
* Parameters used by the frontend:
  - `s` : str — Search string (keyword or regex)
  - `m` : str — Mode (`keyword` or `regex`)
  - `r` : str — Ranking (`occurrences`, `pagerank`, `closeness`, `betweenness`)
* Recommendation feature is **always enabled** implicitly (no user toggle).


# API

* POST /api/basic_search : (s: str, r: str) -> List[DocumentMeta]
  * Normal search mode using keyword matching.
  * Triggered when `m=keyword`.
  * Example request:
    ```json
    { "s": "sargon" }
    ```
  * Example response:
    ```json
    TODO: fill in later with discussed format of reutrned data
    ```

* POST /api/regex_search : (s: RegEx, r: str) -> List[DocumentMeta]
  * Advanced search mode using RegEx pattern matching.
  * Triggered when `m=regex`.
  * Example request:
    ```json
    { "s": ".*Empire.*" }
    ```
  * Example response:
    ```json
    TODO: fill in later with discussed format of reutrned data
    ```

* GET /api/document_text/:id : (id: DocumentId) -> DocumentText
  * Retrieves the full text of a document.
  * Example request: `/api/document_text/5`
  


# FRONTEND FUNCTIONALITY

* Search workflow:
  - User enters query into search bar (`s`).
  - User selects mode (`m`: keyword / regex).
  - User selects ranking method (`r`).
  - Frontend builds URL:
    ```
    /results?s=<term>&m=<mode>&r=<ranking>
    ```
  - Vue router navigates to `/results`.
  - Axios POST request sent to corresponding backend endpoint:
    - `/api/basic_search` if `m=keyword`
    - `/api/regex_search` if `m=regex`
  - Response is displayed as ranked list of `DocumentMeta` objects.

* Result display:
  - Each result card shows:
    - Title
    - Optional cover image
    - Ranking score (if provided)
  - Clicking a result may trigger `/api/document_text/:id` to show full text.

* Parameters (`s`, `m`, `r`) are logged in console for debugging (F12).

* Example console output:
🚀 Search triggered with parameters: { s: 'empire', m: 'regex', r: 'pagerank' }
➡️ Navigating to /results with params: { s: 'empire', m: 'regex', r: 'pagerank' }


# TYPES

## Frontend


DocumentId = int

DocumentMeta = Struct { title: str, id: DocumentId, cover: URL }

DocumentText = str

---

# NOTES

* CORS must allow origin `http://localhost:5173`
* Frontend implemented in Vue 3 + TypeScript + TailwindCSS
* All HTTP requests use Axios
* Recommendation feature not exposed as toggle on frontend
* Ranking selection (`r`) always sent as query param, handled by backend
* Mode selection (`m`) determines which endpoint to call

---

