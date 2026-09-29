<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-800">行政規範與表單下載</h2>
      <span class="text-xs bg-gray-200 px-2 py-1 rounded text-gray-600">規範庫</span>
    </div>

    <!-- 規範類別頁籤 -->
    <div class="flex gap-2 border-b overflow-x-auto pb-2 text-xs font-semibold text-gray-600">
      <button 
        v-for="cat in categories" 
        :key="cat" 
        @click="activeCat = cat" 
        class="px-3 py-1.5 rounded-lg whitespace-nowrap transition"
        :class="activeCat === cat ? 'bg-line-green text-white font-bold' : 'bg-white border text-gray-600 hover:bg-gray-50'"
      >
        {{ cat }}
      </button>
    </div>

    <!-- 素材與表單列表 -->
    <div v-if="loading" class="text-center py-8 text-sm text-gray-500">載入中...</div>
    <div v-else-if="filteredItems.length === 0" class="text-center py-8 text-sm text-gray-500">尚無相關行政規範或表單</div>
    <div v-else class="space-y-3">
      <div v-for="item in filteredItems" :key="item.id" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center justify-between gap-3">
        <div class="space-y-1">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-lg">📁</span>
            <span v-if="item.category_name" class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-medium">
              {{ item.category_name }}
            </span>
            <span v-if="item.is_internal_only" class="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded font-medium">
              🔒 內部限閱
            </span>
            <h3 class="font-bold text-gray-800 text-sm">{{ item.title }}</h3>
          </div>
          <p class="text-xs text-gray-500">{{ item.description || '無詳細說明' }}</p>
        </div>
        <a :href="item.file_url" target="_blank" class="px-3 py-1.5 bg-line-green text-white text-xs rounded-lg hover:bg-emerald-600 transition whitespace-nowrap font-medium flex-shrink-0">
          下載表單
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { API_BASE_URL } from '@/config'

const defaultCats = ['全部規範與表單', '投保規則', '保費規則', '保全規則', '理賠注意事項', '各式表單']
const categories = ref<string[]>(defaultCats)
const activeCat = ref('全部規範與表單')
const loading = ref(false)
const items = ref<any[]>([])

const fetchGuidelines = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('agent_token')
    const headers: any = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(`${API_BASE_URL}/products/assets?type=admin_rule`, { headers })
    if (res.ok) {
      items.value = await res.json()
      const extraCats = new Set<string>()
      items.value.forEach(item => {
        if (item.category_name && !defaultCats.includes(item.category_name)) {
          extraCats.add(item.category_name)
        }
      })
      categories.value = [...defaultCats, ...Array.from(extraCats)]
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const filteredItems = computed(() => {
  if (activeCat.value === '全部規範與表單') return items.value
  return items.value.filter(item => item.category_name === activeCat.value)
})

onMounted(fetchGuidelines)
</script>
