import { defineStore } from 'pinia'

export const useResultsStore = defineStore('results', {
  state: () => ({
    results: [] as any[],
  }),

  actions: {
    setResults(data: any[]) {
      this.results = data
    },
    clearResults() {
      this.results = []
    }
  }
})

