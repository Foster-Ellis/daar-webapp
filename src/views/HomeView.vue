<template>
  <div
    class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-green-50 via-white to-green-100 text-center p-6"
  >
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-5xl font-extrabold text-green-800 tracking-tight mb-2">
        📚 DAAR Book Search
      </h1>
      <p class="text-gray-600 text-lg">
        Explore a digital library of over 1600+ books — search by <strong>keyword</strong> or
        <strong>RegEx</strong>.
      </p>
    </div>

    <!-- Search Bar -->
    <div class="flex flex-wrap justify-center gap-2">
      <input
        v-model="query"
        type="text"
        placeholder="Enter a keyword or regex..."
        class="border border-gray-300 focus:border-green-500 focus:ring-green-500 px-4 py-3 rounded-l-md w-80 outline-none text-gray-800 shadow-sm"
        @keyup.enter="search"
      />
      <button
        @click="search"
        class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-r-md font-semibold transition-colors shadow-sm"
      >
        Search
      </button>
    </div>

    <!-- Small footer / hint -->
    <div class="mt-10 text-gray-500 text-sm">
      <p>Try examples: <span class="font-mono">'Sargon'</span>, <span class="font-mono">'Saigon'</span>, or a regex like <span class="font-mono">'.*Empire.*'</span></p>
      <p class="mt-2 italic">Built for the DAAR webapp assignment (Sorbonne Université)</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const query = ref('')
const router = useRouter()

function search() {
  if (query.value.trim().length === 0) return
  router.push({ path: '/results', query: { q: query.value } })
}
</script>






