<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">業務員主資料與異動管理 (MDM)</h1>
        <p class="text-xs text-gray-500 mt-1">支援 通路 >> 督導區/區部 >> 通訊處/單位 >> 職級 四階層架構與彈性非必填欄位維護。</p>
      </div>
      <div class="flex items-center gap-3">
        <a href="http://localhost:8000/api/v1/admin/templates/agents" download target="_blank">
          <el-button size="small" type="info" plain>📄 下載空白範本檔 (.xlsx)</el-button>
        </a>
        <el-button type="success" @click="excelImportDialogVisible = true">📥 Excel 批次匯入業務員</el-button>
        <el-button type="primary" @click="openCreateDialog">+ 新增業務員</el-button>
      </div>
    </div>

    <!-- 搜尋與篩選工具列 -->
    <el-card shadow="never">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <el-input v-model="searchQuery" placeholder="搜尋工號、姓名、督導區、單位或職級..." style="width: 300px" clearable @clear="fetchAgents" @keyup.enter="fetchAgents" />
          <el-select v-model="statusFilter" placeholder="狀態篩選" style="width: 130px" clearable @change="fetchAgents">
            <el-option label="全體" value="" />
            <el-option label="在職 (active)" value="active" />
            <el-option label="離職 (resigned)" value="resigned" />
            <el-option label="停權 (suspended)" value="suspended" />
          </el-select>
          <el-button type="primary" plain @click="fetchAgents">搜尋</el-button>
        </div>

        <div class="flex items-center gap-2">
          <el-button size="small" @click="fetchAgents">刷新列表</el-button>
        </div>
      </div>
    </el-card>

    <!-- 業務員主列表 -->
    <el-card shadow="never">
      <el-table :data="agents" style="width: 100%" v-loading="loading">
        <el-table-column prop="agent_code" label="工號" width="95">
          <template #default="{ row }">
            <span class="font-bold text-gray-800">{{ row.agent_code }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="姓名" width="100" />

        <el-table-column prop="phone" label="手機號碼" width="125" />

        <el-table-column prop="channel" label="通路" width="95">
          <template #default="{ row }">
            <span class="text-xs text-gray-600">{{ row.channel || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="district" label="督導區/區部" min-width="120">
          <template #default="{ row }">
            <el-tag size="small" type="primary" v-if="row.district && row.district !== '-'">{{ row.district }}</el-tag>
            <span v-else class="text-gray-400 text-xs">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="branch_office" label="通訊處/單位" min-width="130">
          <template #default="{ row }">
            <el-tag size="small" type="success" v-if="row.branch_office && row.branch_office !== '-'">{{ row.branch_office }}</el-tag>
            <span v-else class="text-gray-400 text-xs">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="job_title" label="職級" width="110">
          <template #default="{ row }">
            <el-tag size="small" type="warning" v-if="row.job_title && row.job_title !== '-'">{{ row.job_title }}</el-tag>
            <span v-else class="text-gray-400 text-xs">-</span>
          </template>
        </el-table-column>

        <el-table-column label="LINE 身分綁定" width="150">
          <template #default="{ row }">
            <el-tag :type="row.is_bound_real_line ? 'success' : 'info'" size="small">
              {{ row.is_bound_real_line ? '🟢 已綁定 LINE' : '⚪ 未綁定' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="帳號狀態" width="105">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作與異動" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openEditDialog(row)">編輯/轉調</el-button>
            <el-dropdown trigger="click">
              <el-button size="small">更多 ▾</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="row.is_verified" @click="handleUnbind(row)">解綁 LINE 身分</el-dropdown-item>
                  <el-dropdown-item v-if="row.status === 'active'" class="text-orange-600 font-bold" @click="handleOffboard(row)">
                    🚫 辦理離職 (鎖定權限)
                  </el-dropdown-item>
                  <el-dropdown-item class="text-red-600 font-bold" @click="handleDeleteAgent(row)">
                    🗑️ 刪除主檔紀錄
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增 / 編輯業務員對話框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '編輯業務員異動資料' : '新增業務員主資料'" width="540px">
      <el-form :model="agentForm" label-width="120px">
        <el-form-item label="業務員工號" v-if="!editingId">
          <el-input v-model="agentForm.agent_code" placeholder="例如：A002" />
        </el-form-item>

        <el-form-item label="姓名">
          <el-input v-model="agentForm.name" placeholder="輸入業務員姓名" />
        </el-form-item>

        <el-form-item label="手機號碼">
          <el-input v-model="agentForm.phone" placeholder="例如：0912345678" />
        </el-form-item>

        <el-form-item label="銷售通路">
          <el-select v-model="agentForm.channel" class="w-full" filterable allow-create clearable default-first-option placeholder="請選擇或輸入銷售通路 (非必填)">
            <el-option v-for="opt in channelOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </el-form-item>

        <el-form-item label="督導區/區部">
          <el-select v-model="agentForm.district" class="w-full" filterable allow-create clearable default-first-option placeholder="請選擇或輸入督導區/區部 (非必填)">
            <el-option v-for="opt in districtOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </el-form-item>

        <el-form-item label="通訊處/單位">
          <el-select v-model="agentForm.branch_office" class="w-full" filterable allow-create clearable default-first-option placeholder="請選擇或輸入通訊處/單位 (非必填)">
            <el-option v-for="opt in branchOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </el-form-item>

        <el-form-item label="職級">
          <el-select v-model="agentForm.job_title" class="w-full" filterable allow-create clearable default-first-option placeholder="請選擇或輸入職級 (非必填)">
            <el-option v-for="opt in jobTitleOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </el-form-item>

        <el-form-item label="帳號狀態" v-if="editingId">
          <el-select v-model="agentForm.status" class="w-full">
            <el-option label="在職 (active)" value="active" />
            <el-option label="離職 (resigned)" value="resigned" />
            <el-option label="停權 (suspended)" value="suspended" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAgent">確認儲存</el-button>
      </template>
    </el-dialog>

    <!-- Excel 批次匯入業務員對話框 -->
    <el-dialog v-model="excelImportDialogVisible" title="Excel 批次匯入與更新業務員主資料" width="520px">
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <p class="text-xs text-gray-500 leading-relaxed">
            標頭包含：<b>工號</b>、<b>姓名</b>、<b>手機號碼</b>（必填）；選填：銷售通路、督導區、通訊處、職級、帳號狀態。若工號已存在則會自動更新。
          </p>
          <a href="http://localhost:8000/api/v1/admin/templates/agents" download target="_blank">
            <el-button size="small" type="primary" link>下載空白範本 (.xlsx)</el-button>
          </a>
        </div>
        <div class="p-4 bg-gray-50 border border-dashed border-gray-300 rounded flex items-center gap-3">
          <input type="file" ref="agentFileInput" accept=".xlsx, .xls" class="text-sm" />
        </div>
      </div>
      <template #footer>
        <el-button @click="excelImportDialogVisible = false">取消</el-button>
        <el-button type="success" @click="handleBatchImportAgents" :loading="importing">開始批次匯入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const agents = ref<any[]>([])
const searchQuery = ref('')
const statusFilter = ref('')

const dialogVisible = ref(false)
const editingId = ref<string | null>(null)

const excelImportDialogVisible = ref(false)
const agentFileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)

const channelOptions = ref<string[]>(['直營', '保經代', '銀行通路'])
const districtOptions = ref<string[]>(['台北督導區', '台中區部', '高雄區部', '新竹區部'])
const branchOptions = ref<string[]>(['台北一處', '台北二處', '台中分公司', '高雄分公司', '飛昂通訊處'])
const jobTitleOptions = ref<string[]>([
  '區經理 (UM)',
  '處經理 (AM)',
  '財務顧問 (FSA)',
  '業務員 (Sales)',
  '業務主任',
  '區主任 (TS)',
  '業務總監',
  '副理',
  '協理'
])

const agentForm = reactive({
  agent_code: '',
  name: '',
  phone: '',
  channel: '直營',
  district: '台北督導區',
  branch_office: '台北一處',
  job_title: '區經理 (UM)',
  status: 'active'
})

const fetchTags = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/admin/tags')
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
        if (t.tag_category === 'channel' && !channelOptions.value.includes(t.tag_name)) {
          channelOptions.value.push(t.tag_name)
        }
      })
    }
  } catch (err) {}
}

const getStatusTagType = (st: string) => {
  if (st === 'active') return 'success'
  if (st === 'resigned') return 'danger'
  return 'warning'
}

const getStatusLabel = (st: string) => {
  if (st === 'active') return '🟢 在職'
  if (st === 'resigned') return '🔴 離職'
  return '🟡 停權'
}

const fetchAgents = async () => {
  loading.value = true
  try {
    let url = `http://localhost:8000/api/v1/admin/agents?`
    if (searchQuery.value) url += `query=${encodeURIComponent(searchQuery.value)}&`
    if (statusFilter.value) url += `status=${encodeURIComponent(statusFilter.value)}&`

    const res = await fetch(url)
    if (res.ok) {
      agents.value = await res.json()
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  editingId.value = null
  agentForm.agent_code = ''
  agentForm.name = ''
  agentForm.phone = ''
  agentForm.channel = '直營'
  agentForm.district = '台北督導區'
  agentForm.branch_office = '台北一處'
  agentForm.job_title = '區經理 (UM)'
  agentForm.status = 'active'
  dialogVisible.value = true
}

const openEditDialog = (row: any) => {
  editingId.value = row.id
  agentForm.agent_code = row.agent_code
  agentForm.name = row.name
  agentForm.phone = row.phone
  agentForm.channel = row.channel !== '-' ? row.channel : ''
  agentForm.district = row.district !== '-' ? row.district : ''
  agentForm.branch_office = row.branch_office !== '-' ? row.branch_office : ''
  agentForm.job_title = row.job_title !== '-' ? row.job_title : ''
  agentForm.status = row.status
  dialogVisible.value = true
}

const handleSaveAgent = async () => {
  if (!agentForm.name || !agentForm.phone || (!editingId.value && !agentForm.agent_code)) {
    ElMessage.warning('請完整填寫必要欄位！')
    return
  }

  try {
    const url = editingId.value
      ? `http://localhost:8000/api/v1/admin/agents/${editingId.value}`
      : 'http://localhost:8000/api/v1/admin/agents'
    const method = editingId.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(agentForm)
    })

    if (res.ok) {
      ElMessage.success(editingId.value ? '業務員異動資料已儲存！' : '新業務員建立成功！')
      dialogVisible.value = false
      fetchAgents()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '儲存失敗')
    }
  } catch (err: any) {
    ElMessage.error('儲存失敗：' + (err.message || '連線失敗'))
  }
}

const handleBatchImportAgents = async () => {
  if (!agentFileInput.value?.files?.length) {
    ElMessage.warning('請先選擇 Excel 檔案！')
    return
  }
  const file = agentFileInput.value.files[0]
  const formData = new FormData()
  formData.append('file', file)

  importing.value = true
  try {
    const res = await fetch('http://localhost:8000/api/v1/admin/agents/batch-import-excel', {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      const data = await res.json()
      ElMessage.success(data.message)
      excelImportDialogVisible.value = false
      fetchAgents()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '匯入失敗')
    }
  } catch (err: any) {
    ElMessage.error('匯入失敗：' + (err.message || '連線錯誤'))
  } finally {
    importing.value = false
  }
}

const handleOffboard = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `確定要辦理業務員「${row.name} (${row.agent_code})」離職嗎？\n辦理離職後將立即撤銷其 LINE 帳號存取權限。`,
      '離職辦理警告',
      { type: 'warning', confirmButtonText: '確認離職鎖定', cancelButtonText: '取消' }
    )
    const res = await fetch(`http://localhost:8000/api/v1/admin/agents/${row.id}/offboard`, { method: 'POST' })
    if (res.ok) {
      ElMessage.success(`業務員 ${row.name} 已成功辦理離職！`)
      fetchAgents()
    }
  } catch (err) {}
}

const handleUnbind = async (row: any) => {
  try {
    await ElMessageBox.confirm(`確定要解除業務員「${row.name}」的 LINE 綁定嗎？`, '解綁確認', { type: 'warning' })
    const res = await fetch(`http://localhost:8000/api/v1/admin/agents/${row.id}/unbind`, { method: 'POST' })
    if (res.ok) {
      ElMessage.success('已解除 LINE 綁定')
      fetchAgents()
    }
  } catch (err) {}
}

const handleDeleteAgent = async (row: any) => {
  try {
    await ElMessageBox.confirm(`確定要徹底刪除業務員「${row.name} (${row.agent_code})」的主資料紀錄嗎？`, '刪除業務員確認', {
      type: 'warning',
      confirmButtonText: '確認刪除',
      cancelButtonText: '取消'
    })
    const res = await fetch(`http://localhost:8000/api/v1/admin/agents/${row.id}`, { method: 'DELETE' })
    if (res.ok) {
      ElMessage.success(`業務員 ${row.name} 紀錄已刪除`)
      fetchAgents()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '刪除失敗')
    }
  } catch (err) {}
}

onMounted(() => {
  fetchAgents()
  fetchTags()
})
</script>
