import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { initLiffApp } from './store/liff'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Mount Vue IMMEDIATELY so the page never renders blank!
app.mount('#app')

// Run LIFF initialization asynchronously in background
initLiffApp().catch(err => {
  console.warn('Background LIFF init warning:', err)
})
