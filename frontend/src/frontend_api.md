## DAAR Project 3 — Frontend API Specification

This document defines how the Vue frontend communicates with the backend API.

---

## Base URL
http://127.0.0.1:8000/api (it works on my machine joke)

All endpoints return **JSON**.


## POST `/api/basic_search`

**Purpose:** Search for documents containing the given keyword.  
**Used in:** Normal search mode.


## POST `/api/regex_search`

**Purpose:** Search 