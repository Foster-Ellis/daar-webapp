import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

export interface DocumentMeta {
  id?: number
  title: string
  author?: string
  snippet?: string
  score?: number
}

export interface SearchResponse {
  results?: DocumentMeta[]
  recommendations?: DocumentMeta[]
  recs?: DocumentMeta[]
}

export type SearchPayload = SearchResponse | DocumentMeta[]

// Keyword or regex search, depending on mode
export async function search(s: string, m: string, r: string): Promise<SearchPayload> {
  const endpoint = m === 'regex' ? 'regex_search' : 'basic_search'

  console.log(`📡 Calling ${endpoint} with:`, { s, m, r })

  const response = await axios.post<SearchPayload>(`${API_BASE}/${endpoint}`, { s, r })
  return response.data
}

// Retrieve full document text by id
export async function getDocumentText(id: number) {
  const response = await axios.get(`${API_BASE}/document_text/${id}`)
  return response.data
}
