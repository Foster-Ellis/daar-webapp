<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">📚 Search Results</h1>

    <!-- CONTROL PANEL -->
    <div class="bg-gray-50 p-4 rounded-xl shadow-md flex flex-wrap gap-4 items-end">
      <!-- Search bar -->
      <div>
        <label class="block text-sm text-gray-700 mb-1">Search Query</label>
        <input
          v-model="s"
          type="text"
          class="border border-gray-300 px-3 py-2 rounded-md w-72"
          placeholder="Enter keyword or RegEx..."
        />
      </div>

      <!-- Search Mode -->
      <div>
        <label class="block text-sm text-gray-700 mb-1">Search Mode</label>
        <select
          v-model="m"
          class="border border-gray-300 px-3 py-2 rounded-md bg-white"
        >
          <option value="keyword">Keyword</option>
          <option value="regex">RegEx</option>
        </select>
      </div>

      <!-- Ranking -->
      <div>
        <label class="block text-sm text-gray-700 mb-1">Ranking Method</label>
        <select
          v-model="r"
          class="border border-gray-300 px-3 py-2 rounded-md bg-white"
        >
          <option value="occurrences">By occurrences (default)</option>
          <option value="pagerank">PageRank (Jaccard graph)</option>
          <option value="closeness">Closeness centrality</option>
          <option value="betweenness">Betweenness centrality</option>
        </select>
      </div>

      <!-- Run Search -->
      <button
        @click="runSearch"
        class="bg-green-600 text-white px-5 py-2 rounded-md hover:bg-green-700 transition"
      >
        Search
      </button>
    </div>

    <!-- RESULTS GRID -->
    <div>
      <h2 class="text-xl font-semibold text-gray-800 mb-2">Results</h2>

      <div
        v-if="results.length > 0"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <div
          v-for="book in results"
          :key="book.id"
          class="p-4 bg-white rounded-xl shadow hover:shadow-lg transition"
        >
          <h3 class="font-semibold text-lg text-gray-800">{{ book.title }}</h3>
          <p v-if="book.author" class="text-gray-500 text-sm">{{ book.author }}</p>
          <p v-if="book.snippet" class="text-gray-600 text-sm mt-2">{{ book.snippet }}</p>
          <p v-if="book.score" class="text-gray-400 text-xs mt-1">
            Relevance: {{ (book.score * 100).toFixed(1) }}%
          </p>
        </div>
      </div>

      <p v-else class="text-gray-500 italic mt-3">No results found.</p>
    </div>

    <!-- RECOMMENDATION SECTION -->
    <div v-if="recs.length > 0" class="mt-8">
      <h2 class="text-xl font-semibold mb-4">Recommended Documents</h2>
      <div class="flex flex-wrap gap-3">
        <span
          v-for="rec in recs"
          :key="rec.id || rec"
          class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
        >
          {{ rec.title || rec }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// Query parameters synced with backend spec
const s = ref(route.query.s || '')
const m = ref(route.query.m || 'keyword')
const r = ref(route.query.r || 'occurrences')

// Results + Recommendations
const results = ref<any[]>([])
const recs = ref<any[]>([])

// Dummy placeholders (for now)
const dummyResults = [
  { id: 1, title: 'The Epic of Sargon', author: 'Unknown', snippet: 'King Sargon of Akkad...' },
  { id: 2, title: 'Saigon and the Stars', author: 'Lê Nguyễn', snippet: 'A traveler in old Saigon...' },
  { id: 3, title: 'Babylon Rising', author: 'H. Wells', snippet: 'The rise and fall of empires...' },
]

const dummyRecs = [
  { title: 'Chronicles of Akkad' },
  { title: 'Epic Tales' },
  { title: 'Ancient Rulers' },
]

function runSearch() {
  if (!String(s.value).trim()) {
  console.warn('⚠️ Empty search — aborted')
  return
  }


  console.log('🚀 Search triggered with:', {
    s: s.value,
    m: m.value,
    r: r.value,
  })

  // TODO: Replace with Axios backend call later
  // e.g.:
  // const endpoint = m.value === 'regex' ? '/api/regex_search' : '/api/basic_search'
  // const res = await axios.post(`http://127.0.0.1:8000${endpoint}`, { s: s.value })
  // results.value = res.data.results || []
  // recs.value = res.data.recommendations || []

  // For now: simulate results
  results.value = dummyResults
  recs.value = dummyRecs

  console.log('✅ Results updated with', results.value.length, 'entries')
}

onMounted(() => {
  if (s.value) runSearch()
})
</script>

