<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const s = ref("")
const m = ref("basic")
const r = ref("occurrences")

function goSearch() {
  if (!s.value.trim()) return
  router.push({
    path: "/results",
    query: { s: s.value, m: m.value, r: r.value }
  })
}
</script>

<template>
  <div class="home-container">

    <!-- TITLE -->
    <h1 class="title">DAAR Book Search</h1>
    <p class="subtitle">
      Search by keyword or regular expression across all indexed documents
    </p>

    <!-- SEARCH PANEL (same visual language as results page) -->
    <div class="control-panel">

      <!-- Query -->
      <div class="field wide">
        <label>Query</label>
        <input
          v-model="s"
          @keyup.enter="goSearch"
          placeholder="Enter search term…"
        />
      </div>

      <!-- Mode -->
      <div class="field">
        <label>Mode</label>
        <select v-model="m">
          <option value="basic">Keyword</option>
          <option value="regex">Regex</option>
        </select>
      </div>

      <!-- Ranking -->
      <div class="field">
        <label>Ranking</label>
        <select v-model="r">
          <option value="occurrences">Occurrences</option>
          <option value="closeness">Closeness</option>
        </select>
      </div>

      <!-- Button -->
      <div class="field button-field">
        <label class="invisible">Search</label>
        <button @click="goSearch">Search</button>
      </div>

    </div>

  </div>
</template>

<style>
/* Container */
.home-container {
  max-width: 900px;
  margin: auto;
  padding: 40px 20px;
  text-align: center;
}

/* Title + subtitle */
.title {
  font-size: 3rem;
  font-weight: 700;
}

.subtitle {
  font-size: 1.1rem;
  margin-top: 8px;
  color: #555;
}

/* Control panel box (same styling as ResultsView) */
.control-panel {
  margin-top: 35px;
  background: #f8f8f8;
  padding: 25px;
  border-radius: 14px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.1);

  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  justify-items: center;
}

/* Input fields */
.field {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.field.wide {
  grid-column: span 2;
}

label {
  font-size: 0.85rem;
  margin-bottom: 4px;
  text-align: left;
}

input, select {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 8px;
  font-size: 0.95rem;
  width: 100%;
}

.button-field {
  display: flex;
  flex-direction: column;
  align-items: center;
}

button {
  width: 100%;
  padding: 12px 16px;
  background: #38a169;
  color: white;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  font-size: 1rem;
}

button:hover {
  background: #2f855a;
}

.invisible {
  visibility: hidden;
}
</style>
