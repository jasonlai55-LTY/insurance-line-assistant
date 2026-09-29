import { createRouter, createWebHistory } from 'vue-router'
import AssetManagementView from '../views/AssetManagementView.vue'
import BatchPushView from '../views/BatchPushView.vue'
import TagManagementView from '../views/TagManagementView.vue'
import AgentManagementView from '../views/AgentManagementView.vue'
import LoginView from '../views/LoginView.vue'

const routes = [
  { path: '/', redirect: '/assets' },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/assets', name: 'assets', component: AssetManagementView },
  { path: '/batch-push', name: 'batch-push', component: BatchPushView },
  { path: '/tags', name: 'tags', component: TagManagementView },
  { path: '/agents', name: 'agents', component: AgentManagementView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
