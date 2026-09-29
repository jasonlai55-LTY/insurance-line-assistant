<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">素材與表單管理</h1>
        <p class="text-xs text-gray-500 mt-1">管理商品 DM、銷售手冊、行政規範與版本過期警示設定</p>
      </div>
      <div class="flex items-center gap-3">
        <a href="http://localhost:8000/api/v1/admin/templates/assets" download target="_blank">
          <el-button size="large" type="info" plain>📄 下載空白範本檔 (.xlsx)</el-button>
        </a>
        <el-button type="success" size="large" @click="excelImportDialogVisible = true">📥 Excel 批次匯入素材</el-button>
        <el-button type="primary" size="large" @click="openCreateDialog">+ 新增素材/規範</el-button>
      </div>
    </div>

    <!-- 素材數據表格 -->
    <el-card shadow="never">
      <el-table :data="assets" style="width: 100%" v-loading="loading">
        <el-table-column prop="product_code" label="商品代號" width="130">
          <template #default="{ row }">
            <span class="font-medium text-gray-700">{{ row.product_code || '通用 (無代號)' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="素材標題" min-width="220" />
        <el-table-column prop="type" label="類別" width="140">
          <template #default="{ row }">
            <el-tag :type="row.type === 'product' ? 'success' : 'warning'">
              {{ row.type === 'product' ? '商品素材' : '行政規範表單' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_internal_only" label="內部權限" width="110">
          <template #default="{ row }">
            <el-tag :type="row.is_internal_only ? 'danger' : 'info'" size="small">
              {{ row.is_internal_only ? '限驗證業務' : '公開' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="上架狀態" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'">{{ row.status === 'published' ? '已上架' : '草稿/下架' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <el-button size="small" type="primary" plain @click="openEditDialog(row)">編輯</el-button>
              <el-button size="small" :type="row.status === 'published' ? 'warning' : 'success'" plain @click="toggleStatus(row)">
                {{ row.status === 'published' ? '下架' : '上架' }}
              </el-button>
              <el-button size="small" type="danger" plain @click="deleteAsset(row)">刪除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增 / 編輯對話框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '編輯商品素材 / 行政規範' : '新增商品素材 / 行政規範表單'" width="600px">
      <el-form :model="form" label-width="130px">
        <el-form-item label="素材類型">
          <el-radio-group v-model="form.type">
            <el-radio label="product">商品素材 (DM/銷售手冊)</el-radio>
            <el-radio label="admin_rule">行政規範表單 (通用規範)</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="商品代號">
          <el-input v-model="form.product_code" :placeholder="form.type === 'product' ? '例如 ACC01' : '通用規範可留空 (選填)'" />
        </el-form-item>

        <el-form-item label="素材/規範標題">
          <el-input v-model="form.title" placeholder="例如：投保規則 / 理賠申請書範本" />
        </el-form-item>

        <el-form-item label="檔案/圖檔 URL">
          <el-input v-model="form.file_url" placeholder="https://..." />
        </el-form-item>

        <el-form-item label="規範/表單分類" v-if="form.type === 'admin_rule'">
          <el-select v-model="form.category_name" filterable allow-create default-first-option placeholder="請選擇或輸入分類 (如：投保規則、理賠注意事項)" class="w-full">
            <el-option label="投保規則" value="投保規則" />
            <el-option label="保費規則" value="保費規則" />
            <el-option label="保全規則" value="保全規則" />
            <el-option label="理賠注意事項" value="理賠注意事項" />
            <el-option label="各式表單" value="各式表單" />
          </el-select>
        </el-form-item>

        <el-form-item label="內部權限防護">
          <el-switch v-model="form.is_internal_only" active-text="僅限驗證業務員存取 (核保/特批)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAsset">確認儲存</el-button>
      </template>
    </el-dialog>

    <!-- Excel 批次匯入素材對話框 -->
    <el-dialog v-model="excelImportDialogVisible" title="Excel 批次匯入素材與規範表單" width="520px">
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <p class="text-xs text-gray-500 leading-relaxed">
            標頭包含：<b>素材標題</b> (必填)、類別 (商品素材/行政規範表單)、商品代號、檔案網址、內部權限。
          </p>
          <a href="http://localhost:8000/api/v1/admin/templates/assets" download target="_blank">
            <el-button size="small" type="primary" link>下載空白範本 (.xlsx)</el-button>
          </a>
        </div>
        <div class="p-4 bg-gray-50 border border-dashed border-gray-300 rounded flex items-center gap-3">
          <input type="file" ref="assetFileInput" accept=".xlsx, .xls" class="text-sm" />
        </div>
      </div>
      <template #footer>
        <el-button @click="excelImportDialogVisible = false">取消</el-button>
        <el-button type="success" @click="handleBatchImportAssets" :loading="importing">開始批次匯入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const excelImportDialogVisible = ref(false)
const assetFileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)
const assets = ref<any[]>([])

const form = reactive({
  type: 'admin_rule',
  product_code: '',
  title: '',
  file_url: '',
  is_internal_only: false,
  category_id: '',
  category_name: '投保規則'
})

const openCreateDialog = () => {
  editingId.value = null
  form.type = 'admin_rule'
  form.product_code = ''
  form.title = ''
  form.file_url = ''
  form.is_internal_only = false
  form.category_name = '投保規則'
  dialogVisible.value = true
}

const openEditDialog = (row: any) => {
  editingId.value = row.id
  form.type = row.type || 'admin_rule'
  form.product_code = row.product_code || ''
  form.title = row.title || ''
  form.file_url = row.file_url || ''
  form.is_internal_only = Boolean(row.is_internal_only)
  form.category_name = row.category_name || '投保規則'
  dialogVisible.value = true
}

const fetchAssets = async () => {
  loading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/v1/admin/assets')
    if (res.ok) {
      assets.value = await res.json()
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSaveAsset = async () => {
  if (!form.title || !form.file_url) {
    ElMessage.warning('請輸入素材標題與檔案 URL！')
    return
  }
  try {
    const url = editingId.value
      ? `http://localhost:8000/api/v1/admin/assets/${editingId.value}`
      : 'http://localhost:8000/api/v1/admin/assets'
    const method = editingId.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    if (res.ok) {
      ElMessage.success(editingId.value ? '素材更新成功！' : '素材與規範表單上架成功！')
      dialogVisible.value = false
      fetchAssets()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '操作失敗')
    }
  } catch (err: any) {
    ElMessage.error('連線錯誤：' + (err.message || '連線錯誤'))
  }
}

const handleBatchImportAssets = async () => {
  if (!assetFileInput.value?.files?.length) {
    ElMessage.warning('請先選擇 Excel 檔案！')
    return
  }
  const file = assetFileInput.value.files[0]
  const formData = new FormData()
  formData.append('file', file)

  importing.value = true
  try {
    const res = await fetch('http://localhost:8000/api/v1/admin/assets/batch-import-excel', {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      const data = await res.json()
      ElMessage.success(data.message)
      excelImportDialogVisible.value = false
      fetchAssets()
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

const toggleStatus = async (row: any) => {
  const nextStatus = row.status === 'published' ? 'draft' : 'published'
  try {
    const res = await fetch(`http://localhost:8000/api/v1/admin/assets/${row.id}/status?status_val=${nextStatus}`, {
      method: 'PUT'
    })
    if (res.ok) {
      ElMessage.success(`已將「${row.title}」狀態切換為：${nextStatus === 'published' ? '已上架' : '下架'}`)
      fetchAssets()
    } else {
      ElMessage.error('狀態切換失敗')
    }
  } catch (err: any) {
    ElMessage.error('連線失敗：' + err.message)
  }
}

const deleteAsset = async (row: any) => {
  try {
    await ElMessageBox.confirm(`確定要刪除素材「${row.title}」嗎？`, '刪除素材確認', {
      type: 'warning',
      confirmButtonText: '確認刪除',
      cancelButtonText: '取消'
    })
    const res = await fetch(`http://localhost:8000/api/v1/admin/assets/${row.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      ElMessage.success(`素材「${row.title}」已成功刪除！`)
      fetchAssets()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '刪除失敗')
    }
  } catch (err) {}
}

onMounted(fetchAssets)
</script>
