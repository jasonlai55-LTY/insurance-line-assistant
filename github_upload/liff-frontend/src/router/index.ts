import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ProductsView from '../views/ProductsView.vue'
import GuidelinesView from '../views/GuidelinesView.vue'
import NotificationsView from '../views/NotificationsView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/products', name: 'products', component: ProductsView },
  { path: '/guidelines', name: 'guidelines', component: GuidelinesView },
  { path: '/notifications', name: 'notifications', component: NotificationsView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auto handle LINE LIFF liff.state parameters (e.g. ?liff.state=%2Fnotifications)
router.beforeEach((to, _from, next) => {
  const urlParams = new URLSearchParams(window.location.search)
  const liffState = urlParams.get('liff.state')
  if (liffState && to.path === '/') {
    const targetPath = decodeURIComponent(liffState)
    if (targetPath && targetPath !== '/') {
      return next(targetPath)
    }
  }
  next()
})

export default router
