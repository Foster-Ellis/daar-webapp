<template>
  <div class="min-h-screen flex flex-col justify-center items-center bg-gray-50 text-center p-6">
    <h1 class="text-4xl font-bold mb-4 text-green-800">📚 DAAR Book Search</h1>
    <p class="text-gray-600 mb-6">Search by keyword or regex across all indexed documents</p>

    <!-- Search bar -->
    <div class="flex gap-2 mb-4">
      <input
        v-model="query"
        type="text"
        placeholder="Enter keyword or regex..."
        class="border border-gray-300 px-4 py-2 rounded-md w-96 shadow-sm focus:ring-2 focus:ring-green-400 outline-none"
        @keyup.enter="search"
      />
      <button
        @click="search"
        class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
      >
        Search
      </button>
    </div>

    <!-- Search Options -->
    <div class="flex flex-wrap justify-center gap-4 mb-6">
      <div>
        <label class="block text-gray-700 text-sm mb-1">Mode</label>
        <select v-model="mode" class="border border-gray-300 rounded-md px-3 py-2">
          <option value="keyword">Keyword</option>
          <option value="regex">RegEx</option>
        </select>
      </div>

      <div>
        <label class="block text-gray-700 text-sm mb-1">Ranking</label>
        <select v-model="ranking" class="border border-gray-300 rounded-md px-3 py-2">
          <option value="occurrences">Occurrences</option>
          <option value="pagerank">PageRank</option>
          <option value="closeness">Closeness</option>
          <option value="betweenness">Betweenness</option>
        </select>
      </div>

      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const query = ref('')
const mode = ref('keyword')
const ranking = ref('occurrences')

const router = useRouter()


function search() {
  if (!query.value.trim()) return
  router.push({
    path: '/results',
    query: {
      q: query.value,
      mode: mode.value,
      ranking: ranking.value,
    }
  })
}
</script>







