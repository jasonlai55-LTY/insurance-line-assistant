<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-800">通知與推播發送中心</h1>
      <p class="text-xs text-gray-500 mt-1">支援 Excel 個案照會匯入與全體/職級/督導區/通訊處分眾標籤廣播卡片推播。</p>
    </div>

    <!-- 業務員 LINE 身分綁定動態狀態檢視卡片 -->
    <el-card shadow="never" class="bg-slate-50 border-slate-200 space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm font-bold text-gray-700">
            👤 業務員 {{ agentStatus.agent_code || 'A001' }}
            ({{ agentStatus.name || '張大明' }} / {{ agentStatus.phone || '0912345678' }} / {{ agentStatus.district || '台北督導區' }} / {{ agentStatus.branch_office || '台北一處' }} / <span class="text-emerald-700 font-extrabold">{{ agentStatus.job_title || '區主任 (TS)' }}</span>) 綁定狀態：
          </span>
          <el-tag :type="agentStatus.is_bound_real_line ? 'success' : 'warning'" size="large">
            {{ agentStatus.is_bound_real_line ? '🟢 已成功綁定真實 LINE 帳號 (' + agentStatus.line_user_id + ')' : '🟡 尚未綁定 LINE (模擬推播模式)' }}
          </el-tag>
        </div>
        <div class="flex items-center gap-2">
          <el-button size="small" type="primary" plain @click="fetchAgentStatus">刷新最新主檔狀態</el-button>
        </div>
      </div>

      <div class="pt-2 border-t border-slate-200 flex items-center gap-3">
        <span class="text-xs text-gray-600 font-medium">手動貼上 LINE User ID 綁定測試：</span>
        <el-input v-model="customLineId" placeholder="例如: U1234567890abcdef1234567890abcdef" style="width: 340px" size="small" />
        <el-button type="success" size="small" @click="handleManualBind">手動綁定 LINE ID</el-button>
      </div>
    </el-card>

    <!-- 推播模式頁籤 -->
    <el-tabs type="border-card">
      <!-- 頁籤 1: Excel 批次個案通知 -->
      <el-tab-pane label="📊 Excel 批次個案照會匯入">
        <div class="space-y-4 pt-2">
          <p class="text-xs text-gray-500">上傳 Excel (必須欄位：工號、通知類別、通知標題、原始內文；選填：督導區、通訊處、職級)。自動執行個資脫敏與身份預覽。</p>

          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <div class="flex items-center gap-4">
              <input type="file" ref="fileInput" accept=".xlsx, .xls" class="text-sm" />
              <el-button type="primary" @click="handleUploadAndValidate">解析並執行分眾標籤校驗</el-button>
            </div>
            <a href="https://insurance-line-assistant.onrender.com/api/v1/admin/templates/push" download target="_blank">
              <el-button size="small" type="info" plain>📄 下載照會範本檔 (.xlsx)</el-button>
            </a>
          </div>

          <!-- 防呆校驗與解析預覽 -->
          <div v-if="parsedData" class="space-y-4 pt-2">
            <div class="flex items-center gap-4">
              <el-tag type="success" size="large">合法資料：{{ parsedData.valid_count }} 筆</el-tag>
              <el-tag type="danger" size="large" v-if="parsedData.error_count > 0">異常欄位：{{ parsedData.error_count }} 筆</el-tag>
              <el-button type="success" size="large" @click="executePush" :disabled="parsedData.valid_count === 0">發送 LINE 個案推播卡片</el-button>
            </div>

            <!-- 錯誤提醒 Alert -->
            <el-alert v-for="(err, idx) in parsedData.errors" :key="idx" :title="err" type="error" show-icon class="mb-2" />

            <!-- 脫敏預覽表格 -->
            <el-card shadow="never" header="預覽即將發送之分眾標籤與脫敏內容 (Data Masking & Tag Preview)">
              <el-table :data="parsedData.valid_items" style="width: 100%">
                <el-table-column prop="row_num" label="行號" width="70" />
                <el-table-column prop="agent_code" label="工號" width="100" />
                <el-table-column prop="district_tag" label="督導區標籤" width="130">
                  <template #default="{ row }">
                    <el-tag size="small" type="primary" v-if="row.district_tag">{{ row.district_tag }}</el-tag>
                    <span v-else class="text-gray-400 text-xs">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="branch_tag" label="通訊處標籤" width="130">
                  <template #default="{ row }">
                    <el-tag size="small" type="success" v-if="row.branch_tag">{{ row.branch_tag }}</el-tag>
                    <span v-else class="text-gray-400 text-xs">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="job_tag" label="職級標籤" width="110">
                  <template #default="{ row }">
                    <el-tag size="small" type="warning" v-if="row.job_tag">{{ row.job_tag }}</el-tag>
                    <span v-else class="text-gray-400 text-xs">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="category" label="類別" width="110" />
                <el-table-column prop="title" label="標題" width="180" />
                <el-table-column prop="masked_content" label="資安脫敏後發送內文 (去識別化)" min-width="240" />
              </el-table>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- 頁籤 2: 依職級 / 督導區 / 通訊處 分眾廣播推播 (支援複選) -->
      <el-tab-pane label="📢 依職級 / 督導區 / 通訊處 分眾標籤廣播">
        <div class="max-w-3xl space-y-5 pt-2">
          <el-alert title="支援通路 >> 督導區 >> 通訊處 >> 職級 四階層多選標籤廣播！" type="info" show-icon :closable="false" />

          <el-form :model="broadcastForm" label-width="120px">
            <el-form-item label="廣播目標範圍">
              <el-radio-group v-model="broadcastForm.target_type" @change="onTargetTypeChange">
                <el-radio label="job_title">依職級廣播 (可複選)</el-radio>
                <el-radio label="district">依督導區廣播 (可複選)</el-radio>
                <el-radio label="branch">依通訊處廣播 (可複選)</el-radio>
                <el-radio label="all">全體在職業務員廣播</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="目標標籤選取" v-if="broadcastForm.target_type !== 'all'">
              <el-select
                v-model="broadcastForm.target_values"
                multiple
                collapse-tags
                collapse-tags-tooltip
                class="w-full"
                placeholder="請選擇一至多個分眾標籤 (可複選)"
              >
                <el-option v-for="opt in currentTagOptions" :key="opt" :label="opt" :value="opt" />
              </el-select>
            </el-form-item>

            <el-form-item label="通知類別">
              <el-select v-model="broadcastForm.category" class="w-full">
                <el-option label="行政照會" value="行政照會" />
                <el-option label="商品異動" value="商品異動" />
                <el-option label="營運活動" value="營運活動" />
              </el-select>
            </el-form-item>

            <el-form-item label="通知標題">
              <el-input v-model="broadcastForm.title" placeholder="例如：【重要通知】台北督導區業務主管廣播通知" />
            </el-form-item>

            <el-form-item label="原始通知內文">
              <el-input v-model="broadcastForm.raw_content" type="textarea" :rows="4" placeholder="輸入要發送給業務員的通知內文（若內文含身分證字號或手機號碼，系統將自動進行資安脫敏掩碼處理）" @input="updateMaskingPreview" />
            </el-form-item>

            <el-form-item label="資安脫敏預覽" v-if="maskedPreview">
              <div class="p-3 bg-emerald-50 text-emerald-900 rounded border border-emerald-200 text-xs font-mono w-full whitespace-pre-wrap">
                🔒 系統脫敏掩碼後內容：<br>{{ maskedPreview }}
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="large" @click="handleExecuteBroadcast" :loading="broadcastLoading">
                🚀 發送 LINE 分眾複選廣播通知卡片
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const fileInput = ref<HTMLInputElement | null>(null)
const parsedData = ref<any>(null)
const agentStatus = ref<any>({ is_bound_real_line: false, line_user_id: '', name: '', agent_code: '', district: '', branch_office: '', job_title: '', phone: '' })
const customLineId = ref('')

const broadcastLoading = ref(false)
const maskedPreview = ref('')

const jobTitleOptions = ref<string[]>([
  '區主任 (TS)',
  '區經理 (UM)',
  '處經理 (AM)',
  '財務顧問 (FSA)',
  '業務員 (Sales)',
  '業務主任',
  '業務總監'
])

const districtOptions = ref<string[]>([
  '台北督導區',
  '台中區部',
  '高雄區部',
  '新竹區部'
])

const branchOptions = ref<string[]>([
  '台北一處',
  '台北二處',
  '台中分公司',
  '高雄分公司',
  '飛昂通訊處'
])

const broadcastForm = reactive({
  target_type: 'job_title',
  target_values: ['區主任 (TS)'] as string[],
  category: '行政照會',
  title: '',
  raw_content: ''
})

const currentTagOptions = computed(() => {
  if (broadcastForm.target_type === 'job_title') return jobTitleOptions.value
  if (broadcastForm.target_type === 'district') return districtOptions.value
  if (broadcastForm.target_type === 'branch') return branchOptions.value
  return []
})

const onTargetTypeChange = () => {
  if (broadcastForm.target_type === 'job_title') {
    broadcastForm.target_values = jobTitleOptions.value.length ? [jobTitleOptions.value[0]] : []
  } else if (broadcastForm.target_type === 'district') {
    broadcastForm.target_values = districtOptions.value.length ? [districtOptions.value[0]] : []
  } else if (broadcastForm.target_type === 'branch') {
    broadcastForm.target_values = branchOptions.value.length ? [branchOptions.value[0]] : []
  } else {
    broadcastForm.target_values = ['all']
  }
}

const updateMaskingPreview = () => {
  if (!broadcastForm.raw_content) {
    maskedPreview.value = ''
    return
  }
  let text = broadcastForm.raw_content
  text = text.replace(/([A-Z][12])\d{5}(\d{3})/g, '$1*****$2')
  text = text.replace(/(09\d{2})\d{4}(\d{3})/g, '$1****$2')
  maskedPreview.value = text
}

const fetchAgentStatus = async () => {
  try {
    const res = await fetch('https://insurance-line-assistant.onrender.com/api/v1/admin/notifications/agents')
    if (res.ok) {
      const agents = await res.json()
      const a001 = agents.find((a: any) => a.agent_code === 'A001')
      if (a001) agentStatus.value = a001
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchTags = async () => {
  try {
    const res = await fetch('https://insurance-line-assistant.onrender.com/api/v1/admin/tags')
    if (res.ok) {
      const tagsData = await res.json()
      tagsData.forEach((t: any) => {
        if (t.tag_category === 'job_title' && !jobTitleOptions.value.includes(t.tag_name)) {
          jobTitleOptions.value.push(t.tag_name)
        }
        if (t.tag_category === 'district' && !districtOptions.value.includes(t.tag_name)) {
          districtOptions.value.push(t.tag_name)
        }
        if (t.tag_category === 'branch' && !branchOptions.value.includes(t.tag_name)) {
          branchOptions.value.push(t.tag_name)
        }
      })
    }
  } catch (e) {}
}

const handleManualBind = async () => {
  if (!customLineId.value.trim()) {
    ElMessage.warning('請輸入 LINE User ID！')
    return
  }
  try {
    const res = await fetch('https://insurance-line-assistant.onrender.com/api/v1/admin/notifications/bind-line-id', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_code: 'A001', line_user_id: customLineId.value.trim() })
    })
    if (res.ok) {
      ElMessage.success('成功手動綁定 LINE User ID！')
      await fetchAgentStatus()
      customLineId.value = ''
    } else {
      ElMessage.error('綁定失敗')
    }
  } catch (e) {
    ElMessage.error('網路連線失敗')
  }
}

const handleUploadAndValidate = async () => {
  if (!fileInput.value?.files?.length) {
    ElMessage.warning('請先選擇 Excel 檔案！')
    return
  }
  const file = fileInput.value.files[0]
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await fetch('https://insurance-line-assistant.onrender.com/api/v1/admin/notifications/parse-excel', {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      parsedData.value = await res.json()
      ElMessage.success('Excel 解析與分眾標籤防呆檢核完成！')
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '解析失敗')
    }
  } catch (err) {
    ElMessage.error('伺服器連線失敗')
  }
}

const executePush = async () => {
  if (!parsedData.value || !parsedData.value.valid_items.length) return

  try {
    const res = await fetch('https://insurance-line-assistant.onrender.com/api/v1/admin/notifications/execute-batch-push', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        push_title: `分眾批次推播 ${new Date().toLocaleDateString()}`,
        items: parsedData.value.valid_items
      })
    })
    if (res.ok) {
      const result = await res.json()
      ElMessage.success(result.message)
      parsedData.value = null
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '推播失敗')
    }
  } catch (err: any) {
    ElMessage.error('推播執行失敗：' + (err.message || '連線失敗'))
  }
}

const handleExecuteBroadcast = async () => {
  if (!broadcastForm.title || !broadcastForm.raw_content) {
    ElMessage.warning('請完整輸入通知標題與內容！')
    return
  }

  if (broadcastForm.target_type !== 'all' && (!broadcastForm.target_values || !broadcastForm.target_values.length)) {
    ElMessage.warning('請至少選擇一個分眾標籤！')
    return
  }

  const targetsText = broadcastForm.target_type === 'all'
    ? '全體在職業務員'
    : broadcastForm.target_values.join(', ')

  try {
    await ElMessageBox.confirm(
      `確定要向標籤「${targetsText}」發送廣播卡片通知嗎？`,
      '廣播推播確認',
      { type: 'warning' }
    )

    broadcastLoading.value = true
    const res = await fetch('https://insurance-line-assistant.onrender.com/api/v1/admin/notifications/execute-broadcast-push', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(broadcastForm)
    })

    if (res.ok) {
      const result = await res.json()
      ElMessage.success(result.message)
      broadcastForm.title = ''
      broadcastForm.raw_content = ''
      maskedPreview.value = ''
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '廣播發送失敗')
    }
  } catch (err) {
  } finally {
    broadcastLoading.value = false
  }
}

onMounted(() => {
  fetchAgentStatus()
  fetchTags()
})
</script>
