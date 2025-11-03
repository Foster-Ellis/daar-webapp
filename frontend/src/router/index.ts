// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

// Import your pages
import HomeView from '../views/HomeView.vue'
import ResultsView from '../views/ResultsView.vue'
import AboutView from '../views/AboutView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/results', name: 'results', component: ResultsView },
  { path: '/about', name: 'about', component: AboutView }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router