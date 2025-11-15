<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const s = ref("")
const m = ref("basic")          // default
const r = ref("occurrences")    // default


function goSearch() {
  if (!s.value.trim()) return
  router.push({
    path: "/results",
    query: {
      s: s.value,
      m: m.value,
      r: r.value
    }
  })
}
</script>

<template>
  <div class="p-10 text-center space-y-6">
    <h1 class="text-4xl font-bold">DAAR Book Search</h1>

    <p class="text-gray-700">
      Search by keyword or regular expression across all indexed documents
    </p>

    <!-- Search bar -->
    <input
      v-model="s"
      @keyup.enter="goSearch"
      type="text"
      class="border px-3 py-2 rounded-md w-72"
      placeholder="Enter search term..."
    />

    <!-- Dropdowns -->
    <div class="flex justify-center gap-6 mt-4">

      <!-- Mode -->
      <div>
        <label class="block text-sm text-gray-700 mb-1">Mode</label>
        <select v-model="m" class="border px-3 py-2 rounded-md">
          <option value="basic">Keyword</option>
          <option value="regex">Regex</option>
        </select>
      </div>

      <!-- Ranking -->
      <div>
        <label class="block text-sm text-gray-700 mb-1">Ranking</label>
        <select v-model="r" class="border px-3 py-2 rounded-md">
          <option value="occurrences">Occurrences</option>
          <option value="closeness">Closeness</option>
        </select>
      </div>

    </div>

    <!-- Submit -->
    <button
      @click="goSearch"
      class="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700"
    >
      Search
    </button>
  </div>
</template>
