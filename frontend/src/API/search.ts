import axios from "axios";
import mockData from '../mock_data/fake_search.json'

// Backend base URL
const API_BASE = 'http://127.0.0.1:8000/api'

// Toggle between backend and mock mode
const useMock = false // set to false when backend is ready



// Keyword or regex search, depending on mode
export async function search(search_term: string, method: string, ranking: string) {
  console.log('📡 API call started with:', { search_term, method, ranking })

  if (useMock) {
    console.log('📄 Using mock data (fake_search.json)')

    await new Promise((resolve) => setTimeout(resolve, 250))
    return mockData
  }

  try {
    const search_type = method === 'regex' ? 'regex' : 'basic'
    const response = await axios.post(`${API_BASE}/search`, {
      query: search_term,
      type: search_type,
      ranking: ranking
    })

    console.log('✅ Received response from backend:', response.data)

    return response.data // Should be in { results, recommendations } format
  } catch (error) {
    console.error('❌ API search error:', error)
    throw error
  }
}

// Retrieve full document text by id
export async function getDocumentText(id: number) {
  const response = await axios.get(`${API_BASE}/document_text/${id}`)
  return response.data
}
