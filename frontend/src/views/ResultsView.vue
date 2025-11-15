<script setup lang="ts">
import { ref, onMounted, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

// Controlled fields
const s = ref(String(route.query.s || ""))
const m = ref(String(route.query.m || "regex"))
const r = ref(String(route.query.r || "occurrences"))

const loading = ref(false)
const results = ref<any[]>([])
const recommendations = ref<any[]>([])

async function runSearch() {
  if (!s.value.trim()) return

  loading.value = true
  results.value = []
  recommendations.value = []

  // SEARCH
  const resp = await fetch("http://localhost:8000/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: s.value,
      type: m.value,
      ranking: r.value
    })
  })
  results.value = await resp.json()

  // RECOMMEND
  const rec = await fetch("http://localhost:8000/api/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: s.value
    })
  })
  recommendations.value = await rec.json()

  loading.value = false
}

function updateURLandSearch() {
  router.replace({
    path: "/results",
    query: { s: s.value, m: m.value, r: r.value }
  })
  runSearch()
}

onMounted(runSearch)

watch(() => route.query, () => {
  s.value = String(route.query.s || "")
  m.value = String(route.query.m || "regex")
  r.value = String(route.query.r || "occurrences")
  runSearch()
})
</script>

<template>
  <div class="page-container">

    <!-- CONTROL PANEL -->
    <div class="control-panel">

      <div class="field wide">
        <label>Query</label>
        <input
          v-model="s"
          @keyup.enter="updateURLandSearch"
          placeholder="Enter search term…"
        />
      </div>

      <div class="field">
        <label>Mode</label>
        <select v-model="m">
          <option value="basic">Keyword</option>
          <option value="regex">Regex</option>
        </select>
      </div>

      <div class="field">
        <label>Ranking</label>
        <select v-model="r">
          <option value="occurrences">Occurrences</option>
          <option value="closeness">Closeness</option>
        </select>
      </div>

      <div class="field button-field">
        <label class="invisible">Search</label>
        <button @click="updateURLandSearch">Search</button>
      </div>

    </div>

    <!-- LOADING -->
    <div v-if="loading" class="loading">Loading…</div>

    <!-- RESULTS -->
    <div v-if="!loading" class="section">
      <h2 class="section-title">Results</h2>

      <div class="book-row">
        <div
          class="book-card"
          v-for="doc in results"
          :key="doc.document_id"
        >
          <img
            :src="doc.cover || '/default-cover.png'"
            @error="(e:any)=> e.target.src='/default-cover.png'"
            class="book-cover"
          />
          <h3 class="book-title">{{ doc.title }}</h3>
        </div>
      </div>
    </div>

    <!-- RECOMMENDATIONS -->
    <div v-if="!loading && recommendations.length" class="section">
      <h2 class="section-title">Recommended for You</h2>

      <div class="book-row-single">
        <div
          class="book-card"
          v-for="doc in recommendations"
          :key="doc.document_id"
        >
          <img
            :src="doc.cover || '/default-cover.png'"
            @error="(e:any)=> e.target.src='/default-cover.png'"
            class="book-cover"
          />
          <h3 class="book-title">{{ doc.title }}</h3>
        </div>
      </div>
    </div>

  </div>
</template>

<style>
/* PAGE CONTAINER */
.page-container {
  max-width: 1200px;
  margin: auto;
  padding: 20px;
}

/* CONTROL PANEL */
.control-panel {
  background: #f8f8f8;
  padding: 20px;
  border-radius: 14px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.1);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
}

.field.wide {
  grid-column: span 2;
}

label {
  font-size: 0.85rem;
  margin-bottom: 4px;
}

input, select {
  border: 1px solid #ccc;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.9rem;
}

button {
  padding: 10px 16px;
  background: #38a169;
  color: white;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

button:hover {
  background: #2f855a;
}

.section {
  margin-top: 40px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 15px;
}

/* BOOK CARDS */
.book-row {
  display: grid;
  grid-auto-flow: column;
  grid-template-rows: repeat(2, 1fr);
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.book-row-single {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.book-card {
  width: 120px;
  background: white;
  border-radius: 10px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  scroll-snap-align: start;
}

.book-cover {
  width: 100%;
  height: 170px;
  object-fit: cover;
  border-radius: 6px;
}

.book-title {
  margin-top: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 2.3rem;
}
</style>

