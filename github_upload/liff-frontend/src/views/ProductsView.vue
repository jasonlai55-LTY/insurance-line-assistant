<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-800">商品專區 (DM / 銷售手冊)</h2>
      <span class="text-xs bg-gray-200 px-2 py-1 rounded text-gray-600">全部商品</span>
    </div>

    <!-- 搜尋欄 -->
    <div class="relative">
      <input v-model="searchQuery" type="text" placeholder="搜尋商品名稱或代號 (如 ACC01)..." class="w-full pl-9 pr-3 py-2 border rounded-xl text-sm bg-white outline-none focus:ring-2 focus:ring-line-green" />
      <span class="absolute left-3 top-2.5 text-gray-400 text-sm">🔍</span>
    </div>

    <!-- 素材列表 -->
    <div v-if="loading" class="text-center py-8 text-sm text-gray-500">載入中...</div>
    <div v-else-if="filteredAssets.length === 0" class="text-center py-8 text-sm text-gray-500">尚無相關商品素材</div>
    <div v-else class="space-y-3">
      <div v-for="asset in filteredAssets" :key="asset.id" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-2">
        <div class="flex items-start justify-between">
          <div>
            <span class="inline-block px-2 py-0.5 text-xs bg-emerald-100 text-emerald-800 font-bold rounded mb-1">
              {{ asset.product_code || '通用' }}
            </span>
            <h3 class="font-bold text-gray-800 text-sm">{{ asset.title || '商品資料' }}</h3>
          </div>
          <span v-if="asset.is_expired" class="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded font-bold">過期警示</span>
        </div>
        <p class="text-xs text-gray-500 line-clamp-2">{{ asset.description || '無詳細說明' }}</p>

        <div class="flex items-center justify-between pt-2 border-t text-xs">
          <span class="text-gray-400">發佈時間: {{ formatDate(asset.created_at) }}</span>
          <div class="flex gap-2">
            <a :href="asset.file_url" target="_blank" class="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">線上預覽</a>
            <button @click="shareAsset(asset)" class="px-3 py-1 bg-line-green text-white rounded-lg hover:bg-emerald-600 transition flex items-center gap-1">
              <span>轉發 LINE</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { API_BASE_URL } from '@/config'

const searchQuery = ref('')
const loading = ref(false)
const assets = ref<any[]>([])

const formatDate = (d: any) => {
  if (!d) return ''
  try {
    return new Date(d).toLocaleDateString()
  } catch {
    return String(d)
  }
}

const fetchAssets = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('agent_token')
    const headers: any = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(`${API_BASE_URL}/products/assets?type=product`, { headers })
    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data)) {
        assets.value = data
      }
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const filteredAssets = computed(() => {
  let list = assets.value || []
  if (!searchQuery.value) return list
  const q = searchQuery.value.toLowerCase()
  return list.filter(a =>
    (a.product_code && a.product_code.toLowerCase().includes(q)) ||
    (a.title && a.title.toLowerCase().includes(q))
  )
})

const shareAsset = (asset: any) => {
  alert(`【Share Target Picker 轉發】已準備轉發: ${asset.title}\n網址: ${asset.file_url}`)
}

onMounted(fetchAssets)
</script>
