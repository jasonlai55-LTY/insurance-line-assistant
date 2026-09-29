<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">分類與標籤管理</h1>
        <p class="text-xs text-gray-500 mt-1">管理個人通知中心訊息分類命名、素材分類與分眾標籤。</p>
      </div>
      <div class="flex items-center gap-3">
        <a href="http://localhost:8000/api/v1/admin/templates/tags" download target="_blank">
          <el-button size="large" type="info" plain>📄 下載空白範本檔 (.xlsx)</el-button>
        </a>
        <el-button type="success" size="large" @click="excelImportDialogVisible = true">📥 Excel 批次匯入標籤</el-button>
        <el-button type="primary" size="large" @click="openCreateTagDialog">+ 新增單一標籤</el-button>
      </div>
    </div>

    <el-tabs type="border-card">
      <!-- 頁籤一：通知與素材訊息分類命名管理 -->
      <el-tab-pane label="🔔 個人通知中心 - 訊息分類命名管理">
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <p class="text-xs text-gray-500">此處新增/重命名之分類，將同步更新於業務員端 LIFF 個人通知中心頁籤。</p>
            <el-button type="primary" size="small" @click="openCatDialog">+ 新增訊息分類</el-button>
          </div>

          <el-table :data="notifCategories" style="width: 100%">
            <el-table-column prop="name" label="分類名稱" min-width="200" />
            <el-table-column prop="sort_order" label="排序" width="100" />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" type="primary" plain @click="editCategory(row)">重命名</el-button>
                <el-button size="small" type="danger" plain @click="deleteCategory(row)">刪除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 頁籤二：分眾標籤管理 -->
      <el-tab-pane label="🏷️ 業務員分眾標籤管理">
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <p class="text-xs text-gray-500">維護 通路 >> 督導區 >> 通訊處 >> 職級 分眾標籤，用於 Multicast 廣播與下拉選單選擇。</p>
            <div class="flex items-center gap-2">
              <el-button type="success" size="small" @click="excelImportDialogVisible = true">📥 Excel 批次匯入標籤</el-button>
              <el-button type="primary" size="small" @click="openCreateTagDialog">+ 新增單一標籤</el-button>
            </div>
          </div>

          <el-table :data="tags" style="width: 100%">
            <el-table-column prop="tag_name" label="標籤名稱" min-width="200" />
            <el-table-column prop="tag_category" label="分類" width="160">
              <template #default="{ row }">
                <el-tag :type="getTagCategoryType(row.tag_category)">{{ getTagCategoryLabel(row.tag_category) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" type="primary" plain @click="openEditTagDialog(row)">編輯</el-button>
                <el-button size="small" type="danger" plain @click="deleteTag(row)">刪除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 分類對話框 -->
    <el-dialog v-model="catDialogVisible" :title="editingCatId ? '重命名分類' : '新增訊息分類'" width="450px">
      <el-form :model="catForm" label-width="100px">
        <el-form-item label="分類名稱">
          <el-input v-model="catForm.name" placeholder="例如：行政照會、營運活動、核保警示..." />
        </el-form-item>
        <el-form-item label="排序權重">
          <el-input-number v-model="catForm.sort_order" :min="0" :max="99" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="catDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory">確認儲存</el-button>
      </template>
    </el-dialog>

    <!-- 標籤對話框 (新增/修改) -->
    <el-dialog v-model="tagDialogVisible" :title="editingTagId ? '編輯分眾標籤' : '新增分眾標籤'" width="450px">
      <el-form :model="tagForm" label-width="110px">
        <el-form-item label="標籤分類">
          <el-select v-model="tagForm.tag_category" class="w-full">
            <el-option label="通路 (channel)" value="channel" />
            <el-option label="督導區/區部 (district)" value="district" />
            <el-option label="通訊處/單位 (branch)" value="branch" />
            <el-option label="職級 (job_title)" value="job_title" />
            <el-option label="自訂標籤 (custom)" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="標籤名稱">
          <el-input v-model="tagForm.tag_name" placeholder="例如：台北督導區、區經理、保經代" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTag">確認儲存</el-button>
      </template>
    </el-dialog>

    <!-- Excel 批次匯入標籤對話框 -->
    <el-dialog v-model="excelImportDialogVisible" title="Excel 批次匯入分眾標籤" width="480px">
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <p class="text-xs text-gray-500 leading-relaxed">
            標頭需包含：<b>標籤名稱</b> 與 <b>標籤分類</b> (如：職級、督導區、通訊處、通路)。
          </p>
          <a href="http://localhost:8000/api/v1/admin/templates/tags" download target="_blank">
            <el-button size="small" type="primary" link>下載空白範本 (.xlsx)</el-button>
          </a>
        </div>
        <div class="p-4 bg-gray-50 border border-dashed border-gray-300 rounded flex items-center gap-3">
          <input type="file" ref="tagFileInput" accept=".xlsx, .xls" class="text-sm" />
        </div>
      </div>
      <template #footer>
        <el-button @click="excelImportDialogVisible = false">取消</el-button>
        <el-button type="success" @click="handleBatchImportTags" :loading="importing">開始批次匯入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const notifCategories = ref<any[]>([])
const tags = ref<any[]>([])

const catDialogVisible = ref(false)
const editingCatId = ref<string | null>(null)
const catForm = reactive({
  name: '',
  sort_order: 0,
  type: 'notification_category'
})

const tagDialogVisible = ref(false)
const editingTagId = ref<string | null>(null)
const tagForm = reactive({
  tag_category: 'district',
  tag_name: ''
})

const excelImportDialogVisible = ref(false)
const tagFileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)

const getTagCategoryType = (cat: string) => {
  if (cat === 'job_title') return 'warning'
  if (cat === 'district') return 'primary'
  if (cat === 'branch') return 'success'
  if (cat === 'channel') return 'info'
  return 'info'
}

const getTagCategoryLabel = (cat: string) => {
  if (cat === 'job_title') return '職級 (job_title)'
  if (cat === 'district') return '督導區 (district)'
  if (cat === 'branch') return '通訊處 (branch)'
  if (cat === 'channel') return '通路 (channel)'
  return cat
}

const fetchCategories = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/admin/categories?type=notification_category')
    if (res.ok) {
      notifCategories.value = await res.json()
    }
  } catch (err) {
    console.error(err)
  }
}

const fetchTags = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/admin/tags')
    if (res.ok) {
      tags.value = await res.json()
    }
  } catch (err) {
    console.error(err)
  }
}

const openCatDialog = () => {
  editingCatId.value = null
  catForm.name = ''
  catForm.sort_order = 0
  catDialogVisible.value = true
}

const editCategory = (row: any) => {
  editingCatId.value = row.id
  catForm.name = row.name
  catForm.sort_order = row.sort_order
  catDialogVisible.value = true
}

const deleteCategory = async (row: any) => {
  try {
    await ElMessageBox.confirm(`確定要刪除訊息分類「${row.name}」嗎？`, '刪除分類確認', {
      type: 'warning',
      confirmButtonText: '確認刪除',
      cancelButtonText: '取消'
    })
    const res = await fetch(`http://localhost:8000/api/v1/admin/categories/${row.id}`, { method: 'DELETE' })
    if (res.ok) {
      ElMessage.success('訊息分類已成功刪除！')
      fetchCategories()
    } else {
      ElMessage.error('刪除失敗')
    }
  } catch (err) {}
}

const handleSaveCategory = async () => {
  if (!catForm.name.trim()) {
    ElMessage.warning('請輸入分類名稱！')
    return
  }
  try {
    const url = editingCatId.value
      ? `http://localhost:8000/api/v1/admin/categories/${editingCatId.value}`
      : 'http://localhost:8000/api/v1/admin/categories'
    const method = editingCatId.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(catForm)
    })

    if (res.ok) {
      ElMessage.success(editingCatId.value ? '分類重命名成功！' : '訊息分類新增成功！')
      catDialogVisible.value = false
      fetchCategories()
    }
  } catch (err: any) {
    ElMessage.error('連線失敗：' + err.message)
  }
}

const openCreateTagDialog = () => {
  editingTagId.value = null
  tagForm.tag_category = 'district'
  tagForm.tag_name = ''
  tagDialogVisible.value = true
}

const openEditTagDialog = (row: any) => {
  editingTagId.value = row.id
  tagForm.tag_category = row.tag_category
  tagForm.tag_name = row.tag_name
  tagDialogVisible.value = true
}

const deleteTag = async (row: any) => {
  try {
    await ElMessageBox.confirm(`確定要刪除分眾標籤「${row.tag_name}」嗎？`, '刪除標籤確認', {
      type: 'warning',
      confirmButtonText: '確認刪除',
      cancelButtonText: '取消'
    })
    const res = await fetch(`http://localhost:8000/api/v1/admin/tags/${row.id}`, { method: 'DELETE' })
    if (res.ok) {
      ElMessage.success(`標籤「${row.tag_name}」已成功刪除！`)
      fetchTags()
    } else {
      ElMessage.error('刪除失敗')
    }
  } catch (err) {}
}

const handleSaveTag = async () => {
  if (!tagForm.tag_name.trim()) {
    ElMessage.warning('請輸入標籤名稱！')
    return
  }
  try {
    const url = editingTagId.value
      ? `http://localhost:8000/api/v1/admin/tags/${editingTagId.value}`
      : 'http://localhost:8000/api/v1/admin/tags'
    const method = editingTagId.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tagForm)
    })

    if (res.ok) {
      ElMessage.success(editingTagId.value ? '分眾標籤更新成功！' : '分眾標籤新增成功！')
      tagDialogVisible.value = false
      fetchTags()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '操作失敗')
    }
  } catch (err: any) {
    ElMessage.error('連線失敗：' + err.message)
  }
}

const handleBatchImportTags = async () => {
  if (!tagFileInput.value?.files?.length) {
    ElMessage.warning('請先選擇 Excel 檔案！')
    return
  }
  const file = tagFileInput.value.files[0]
  const formData = new FormData()
  formData.append('file', file)

  importing.value = true
  try {
    const res = await fetch('http://localhost:8000/api/v1/admin/tags/batch-import-excel', {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      const data = await res.json()
      ElMessage.success(data.message)
      excelImportDialogVisible.value = false
      fetchTags()
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

onMounted(() => {
  fetchCategories()
  fetchTags()
})
</script>
