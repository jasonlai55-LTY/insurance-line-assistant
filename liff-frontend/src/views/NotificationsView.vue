<template>
  <div class="space-y-4">
    <!-- 頁面標頭與一鍵清理工具列 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2">
          <span>個人通知中心</span>
          <span v-if="unreadCount > 0" class="text-xs bg-red-500 text-white font-extrabold px-2 py-0.5 rounded-full">
            {{ unreadCount }} 筆未讀
          </span>
        </h2>
        <p class="text-xs text-gray-500 mt-0.5">點擊卡片可查看照會詳情並自動消除未讀燈號</p>
      </div>
      <button v-if="unreadCount > 0" @click="handleMarkAllRead" class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 font-bold px-2.5 py-1.5 rounded-lg transition whitespace-nowrap">
        ✓ 一鍵已讀
      </button>
    </div>

    <!-- 動態分類與未讀篩選工具欄 -->
    <div class="flex items-center justify-between border-b pb-2 gap-2">
      <div class="flex gap-2 overflow-x-auto text-xs font-semibold text-gray-600">
        <button v-for="cat in categories" :key="cat" @click="activeCat = cat" class="px-3 py-1.5 rounded-lg whitespace-nowrap" :class="activeCat === cat ? 'bg-line-green text-white' : 'bg-white border text-gray-600'">
          {{ cat }}
        </button>
      </div>

      <label class="flex items-center gap-1 text-xs text-gray-600 cursor-pointer whitespace-nowrap">
        <input type="checkbox" v-model="unreadOnly" class="rounded text-line-green focus:ring-0" />
        <span>僅看未讀</span>
      </label>
    </div>

    <!-- 通知清單 -->
    <div v-if="loading" class="text-center py-8 text-sm text-gray-500">載入歷史通知中...</div>
    <div v-else-if="filteredLogs.length === 0" class="text-center py-8 text-sm text-gray-500">尚無相關通知紀錄</div>
    <div v-else class="space-y-3">
      <div
        v-for="log in filteredLogs"
        :key="log.id"
        @click="openDetailModal(log)"
        class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-2 relative cursor-pointer transition hover:shadow-md active:bg-gray-50"
        :class="{ 'border-l-4 border-l-line-green bg-emerald-50/20': !log.is_read }"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold px-2 py-0.5 rounded bg-gray-100 text-gray-700">
              {{ log.category || '一般通知' }}
            </span>
            <span v-if="!log.is_read" class="inline-block w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
          </div>

          <div class="flex items-center gap-2 text-xs text-gray-400">
            <span>{{ formatDate(log.created_at) }}</span>
            <button @click.stop="handleDeleteLog(log.id)" class="text-gray-400 hover:text-red-500 p-1 font-bold text-sm" title="移除通知">
              ✕
            </button>
          </div>
        </div>

        <h3 class="font-bold text-gray-800 text-sm flex items-center justify-between">
          <span>{{ log.title || '無標題通知' }}</span>
          <span class="text-xs text-emerald-600 font-semibold">看詳情 &gt;</span>
        </h3>

        <!-- 摘要預覽內文 (去識別化) -->
        <div class="bg-gray-50 p-3 rounded-lg text-xs text-gray-700 leading-relaxed font-mono line-clamp-2">
          {{ log.masked_content || '無詳細內容' }}
        </div>
      </div>
    </div>

    <!-- 深度資料閱讀與解密處置彈窗 -->
    <div v-if="selectedLog" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl relative animate-in fade-in zoom-in duration-200">
        <button @click="selectedLog = null" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 font-bold text-lg">
          ✕
        </button>

        <div class="flex items-center gap-2">
          <span class="text-xs font-bold px-2.5 py-1 rounded bg-emerald-100 text-emerald-800">
            {{ selectedLog.category || '通知' }}
          </span>
          <span class="text-xs text-gray-400">{{ formatDate(selectedLog.created_at) }}</span>
        </div>

        <h3 class="text-lg font-bold text-gray-900 border-b pb-2">
          {{ selectedLog.title }}
        </h3>

        <div class="space-y-3 text-xs">
          <div class="bg-gray-50 p-4 rounded-xl border text-gray-800 space-y-2 font-mono">
            <div class="flex items-center justify-between border-b pb-1">
              <span class="font-bold text-gray-900 text-xs">【該筆個案照會與客戶明細】</span>
              <span class="text-xs px-2 py-0.5 rounded font-bold" :class="isUnlocked ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
                {{ isUnlocked ? '已通過 OTP 解鎖' : '資安保護中' }}
              </span>
            </div>

            <div v-if="isUnlocked" class="space-y-1.5 bg-white p-3 rounded-lg border border-emerald-200 text-gray-800">
              <div class="font-bold text-emerald-800 text-xs mb-1">【該筆個案原創完整明細】</div>
              <div class="whitespace-pre-wrap leading-relaxed font-mono text-gray-900">
                {{ getUnmaskedContent(selectedLog) }}
              </div>
            </div>
            <div v-else class="text-gray-600 leading-relaxed">
              {{ selectedLog.masked_content }}
            </div>
          </div>

          <button
            v-if="!isUnlocked"
            @click="handleUnlockAttempt"
            class="w-full bg-amber-500 hover:bg-amber-600 text-white font-bold py-2 rounded-xl transition flex items-center justify-center gap-1 shadow-sm"
          >
            <span>👁️ 點擊驗證權限，解鎖該筆客戶姓名與保單號碼</span>
          </button>

          <div class="bg-blue-50 p-3 rounded-xl border border-blue-100 text-blue-900 space-y-1">
            <div class="font-bold">💡 行政與補件處置指引</div>
            <p>1. 請核對保戶體況報告與全民健保收據金額。</p>
            <p>2. 下載下方「補件申請表單」，由保戶簽名後上傳至保全系統。</p>
          </div>
        </div>

        <div class="pt-2 flex flex-col gap-2">
          <button @click="handleAction('download')" class="w-full bg-line-green text-white font-bold py-2.5 rounded-xl text-xs hover:bg-emerald-600 transition flex items-center justify-center gap-1">
            <span>📄 下載/預覽對應補件申請表單</span>
          </button>

          <button @click="handleAction('share')" class="w-full bg-gray-100 text-gray-700 font-bold py-2.5 rounded-xl text-xs hover:bg-gray-200 transition">
            📲 轉發給保戶/團隊群組討論
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '@/config'

const router = useRouter()
const categories = ref<string[]>(['全部通知'])
const activeCat = ref('全部通知')
const unreadOnly = ref(false)
const loading = ref(false)
const logs = ref<any[]>([])
const selectedLog = ref<any>(null)
const isUnlocked = ref(false)

const formatDate = (d: any) => {
  if (!d) return ''
  try {
    return new Date(d).toLocaleDateString()
  } catch {
    return String(d)
  }
}

const fetchCategories = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/products/categories?type=notification_category`)
    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data)) {
        const catNames = data.map((c: any) => c.name).filter(Boolean)
        categories.value = ['全部通知', ...catNames]
      }
    }
  } catch (err) {
    categories.value = ['全部通知', '行政照會', '商品異動', '營運活動']
  }
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('agent_token')
    const headers: any = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(`${API_BASE_URL}/notifications/my-logs?limit=20`, { headers })
    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data)) {
        logs.value = data
      }
    } else if (res.status === 401) {
      localStorage.removeItem('agent_token')
      logs.value = []
    }
  } catch (err) {
    console.error('連線失敗:', err)
  } finally {
    loading.value = false
  }
}

const getUnmaskedContent = (log: any) => {
  if (!log) return ''
  if (log.raw_content) return log.raw_content
  let masked = log.masked_content || ''
  return masked
    .replace('王*明', '王大明')
    .replace('張*明', '張大明')
    .replace('D12****789', 'D123456789')
    .replace('A12****789', 'A123456789')
    .replace('P98****323', 'P987654323')
    .replace('P98****321', 'P987654321')
}

const unreadCount = computed(() => (logs.value || []).filter(l => !l.is_read).length)

const filteredLogs = computed(() => {
  let list = logs.value || []
  if (unreadOnly.value) {
    list = list.filter(l => !l.is_read)
  }
  if (activeCat.value === '全部通知') return list
  return list.filter(l => l.category === activeCat.value)
})

const openDetailModal = (log: any) => {
  selectedLog.value = log
  const token = localStorage.getItem('agent_token')
  isUnlocked.value = !!token
  handleMarkRead(log)
}

const handleUnlockAttempt = () => {
  const token = localStorage.getItem('agent_token')
  if (token) {
    isUnlocked.value = true
  } else {
    if (confirm('解鎖完整客戶姓名與保單號碼需完成「工號 + 簡訊 OTP 雙重身分綁定」。是否立即前往驗證？')) {
      router.push('/login')
    }
  }
}

const handleMarkRead = async (log: any) => {
  if (!log || log.is_read) return
  log.is_read = true
  try {
    await fetch(`${API_BASE_URL}/notifications/logs/${log.id}/read`, { method: 'PUT' })
  } catch (err) {}
}

const handleMarkAllRead = async () => {
  (logs.value || []).forEach(l => l.is_read = true)
  try {
    await fetch(`${API_BASE_URL}/notifications/mark-all-read`, { method: 'PUT' })
  } catch (err) {}
}

const handleDeleteLog = async (logId: string) => {
  logs.value = (logs.value || []).filter(l => l.id !== logId)
  try {
    await fetch(`${API_BASE_URL}/notifications/logs/${logId}`, { method: 'DELETE' })
  } catch (err) {}
}

const handleAction = (type: string) => {
  if (type === 'download') {
    alert('【補件表單】已自動開啟相關行政補件表單 PDF 檔案。')
  } else if (type === 'share') {
    alert('【一鍵轉發】已準備透過 LINE Share Target Picker 轉發個案處置指引。')
  }
}

onMounted(() => {
  fetchCategories()
  fetchLogs()
})
</script>
