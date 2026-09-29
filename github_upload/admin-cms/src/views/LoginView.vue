<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900">
    <div class="bg-white p-8 rounded-2xl shadow-2xl w-96 space-y-6">
      <div class="text-center">
        <div class="text-4xl mb-2">🛡️</div>
        <h1 class="text-xl font-bold text-gray-800">保險通路管理後台</h1>
        <p class="text-xs text-gray-500 mt-1">Admin CMS Management System</p>
      </div>

      <el-form :model="form" label-position="top">
        <el-form-item label="管理者帳號">
          <el-input v-model="form.username" placeholder="預設: admin" />
        </el-form-item>
        <el-form-item label="密碼">
          <el-input v-model="form.password" type="password" placeholder="預設: admin123" show-password />
        </el-form-item>
        <el-button type="primary" size="large" class="w-full mt-4" @click="handleLogin" :loading="loading">
          登入系統
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: 'admin',
  password: 'admin123'
})

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/v1/auth/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    const data = await res.json()
    if (res.ok) {
      localStorage.setItem('admin_token', data.access_token)
      ElMessage.success('登入成功')
      router.push('/assets')
    } else {
      ElMessage.error(data.detail || '登入失敗')
    }
  } catch (err) {
    ElMessage.error('伺服器連線失敗')
  } finally {
    loading.value = false
  }
}
</script>
