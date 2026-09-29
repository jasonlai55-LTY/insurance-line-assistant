<template>
  <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-5">
    <div class="text-center">
      <h2 class="text-xl font-bold text-gray-800">業務員身分雙重驗證</h2>
      <p class="text-xs text-gray-500 mt-1">請輸入工號與手機進行簡訊 OTP 綁定</p>
    </div>

    <form @submit.prevent="handleSendOtp" class="space-y-4" v-if="step === 'request'">
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">業務員工號</label>
        <input v-model="form.agent_code" type="text" placeholder="例如：A001" class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-line-green outline-none" required />
      </div>

      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">手機號碼</label>
        <input v-model="form.phone" type="tel" placeholder="0912345678" class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-line-green outline-none" required />
      </div>

      <button type="submit" :disabled="loading" class="w-full bg-line-green text-white font-bold py-2.5 rounded-lg text-sm hover:bg-emerald-600 transition">
        {{ loading ? '發送中...' : '發送簡訊驗證碼' }}
      </button>
    </form>

    <form @submit.prevent="handleVerifyOtp" class="space-y-4" v-else>
      <div class="bg-emerald-50 text-emerald-700 p-3 rounded-lg text-xs">
        驗證碼已發送至 {{ form.phone }}（測試用 OTP: <strong>{{ mockOtp }}</strong>）
      </div>

      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">簡訊 6 位數 OTP 驗證碼</label>
        <input v-model="otpCode" type="text" maxlength="6" placeholder="123456" class="w-full px-3 py-2 border rounded-lg text-sm text-center tracking-widest font-mono text-lg focus:ring-2 focus:ring-line-green outline-none" required />
      </div>

      <button type="submit" :disabled="loading" class="w-full bg-line-green text-white font-bold py-2.5 rounded-lg text-sm hover:bg-emerald-600 transition">
        {{ loading ? '驗證中...' : '確認綁定' }}
      </button>

      <button type="button" @click="step = 'request'" class="w-full text-xs text-gray-500 underline text-center">
        重設工號與手機
      </button>
    </form>

    <div v-if="message" class="p-3 text-xs rounded-lg text-center" :class="isSuccess ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { API_BASE_URL } from '@/config'
import { globalLineUserId } from '@/store/liff'

const step = ref<'request' | 'verify'>('request')
const loading = ref(false)
const message = ref('')
const isSuccess = ref(false)
const mockOtp = ref('')
const otpCode = ref('')

const form = reactive({
  agent_code: '',
  phone: ''
})

onMounted(() => {
  if (globalLineUserId.value) {
    console.log('✅ Global Line User ID present:', globalLineUserId.value)
  }
})

const handleSendOtp = async () => {
  loading.value = true
  message.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/auth/request-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    const data = await res.json()
    if (res.ok) {
      step.value = 'verify'
      mockOtp.value = data.mock_otp
      message.value = '驗證碼發送成功！'
      isSuccess.value = true
    } else {
      message.value = data.detail || '發送失敗'
      isSuccess.value = false
    }
  } catch (err: any) {
    message.value = '無法連線至伺服器：' + (err?.message || err)
    isSuccess.value = false
  } finally {
    loading.value = false
  }
}

const handleVerifyOtp = async () => {
  loading.value = true
  message.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_code: form.agent_code,
        phone: form.phone,
        otp_code: otpCode.value,
        line_user_id: globalLineUserId.value
      })
    })
    const data = await res.json()
    if (res.ok) {
      localStorage.setItem('agent_token', data.access_token)
      message.value = `驗證成功！歡迎 ${data.name}`
      isSuccess.value = true
    } else {
      message.value = data.detail || '驗證失敗'
      isSuccess.value = false
    }
  } catch (err: any) {
    message.value = '無法連線至伺服器：' + (err?.message || err)
    isSuccess.value = false
  } finally {
    loading.value = false
  }
}
</script>
