import axios from "axios";

const API_BASE = 'http://127.0.0.1:8000/api'

// Keyword or regex search, depending on mode
export async function search(search_term: string, method: string, ranking: string) {
  const endpoint = method === 'regex' ? 'regex_search' : 'basic_search'
  
  console.log(`📡 Calling ${endpoint} with:`, { search_term, method, ranking })

  const response = await axios.post(`${API_BASE}/${endpoint}`, { search_term })
  return response.data // Expecting List[DocumentMeta]
}

// Retrieve full document text by id
export async function getDocumentText(id: number) {
  const response = await axios.get(`${API_BASE}/document_text/${id}`)
  return response.data
}