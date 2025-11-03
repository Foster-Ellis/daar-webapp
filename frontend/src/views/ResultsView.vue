<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">📚 Search Results</h1>

    <!-- CONTROL PANEL -->
    <div class="bg-gray-50 p-4 rounded-xl shadow-md flex flex-wrap gap-4 items-end">
      <!-- Search bar -->
      <div>
        <label class="block text-sm text-gray-700 mb-1">Search Query</label>
        <input
          v-model="query"
          type="text"
          class="border border-gray-300 px-3 py-2 rounded-md w-72"
          placeholder="Enter keyword or RegEx..."
        />
      </div>

      <!-- Search Mode -->
      <div>
        <label class="block text-sm text-gray-700 mb-1">Search Mode</label>
        <select
          v-model="mode"
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
          v-model="ranking"
          class="border border-gray-300 px-3 py-2 rounded-md bg-white"
        >
          <option value="occurrences">By occurrences (default)</option>
          <option value="pagerank">PageRank (Jaccard graph)</option>
          <option value="closeness">Closeness centrality</option>
          <option value="betweenness">Betweenness centrality</option>
        </select>
      </div>

      <!-- Recommendation -->
      <div class="flex items-center gap-2">
        <input id="rec" type="checkbox" v-model="recommendations" />
        <label for="rec" class="text-sm text-gray-700">Show Recommendations</label>
      </div>

      <!-- Run -->
      <button
        @click="runSearch"
        class="bg-green-600 text-white px-5 py-2 rounded-md hover:bg-green-700 transition"
      >
        Search
      </button>
    </div>

    <!-- RESULTS GRID -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="book in dummyResults"
        :key="book.title"
        class="p-4 bg-white rounded-xl shadow hover:shadow-lg transition"
      >
        <h3 class="font-semibold text-lg text-gray-800">{{ book.title }}</h3>
        <p class="text-gray-500 text-sm">{{ book.author }}</p>
        <p class="text-gray-600 text-sm mt-2">{{ book.snippet }}</p>
      </div>
    </div>

    <!-- RECOMMENDATION SECTION -->
    <div v-if="recommendations" class="mt-8">
      <h2 class="text-xl font-semibold mb-4">Recommended Documents</h2>
      <div class="flex flex-wrap gap-3">
        <span
          v-for="rec in dummyRecs"
          :key="rec"
          class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
        >
          {{ rec }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// Reactive state
const query = ref(route.query.q || '')
const mode = ref('keyword')
const ranking = ref('occurrences')
const recommendations = ref(true)

// Dummy placeholders for now
const dummyResults = ref([
  { title: 'The Epic of Sargon', author: 'Unknown', snippet: 'King Sargon of Akkad...' },
  { title: 'Saigon and the Stars', author: 'Lê Nguyễn', snippet: 'A traveler in old Saigon...' },
  { title: 'Babylon Rising', author: 'H. Wells', snippet: 'The rise and fall of empires...' },
])
const dummyRecs = ref(['Chronicles of Akkad', 'Epic Tales', 'Ancient Rulers'])

function runSearch() {
  console.log('Search run with:', {
    query: query.value,
    mode: mode.value,
    ranking: ranking.value,
    recommendations: recommendations.value,
  })
  // TODO: Replace with backend call later
}
</script>
