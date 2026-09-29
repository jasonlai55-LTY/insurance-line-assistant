import { ref } from 'vue'
import liff from '@line/liff'
import { API_BASE_URL } from '@/config'

export const isLiffInitialized = ref(false)
export const globalLineUserId = ref<string | null>(null)
export const globalUserProfile = ref<any>(null)

export async function initLiffApp() {
  if (isLiffInitialized.value) return
  
  const activeLiff = (window as any).liff || liff

  // 3 秒強制作答超時，確保即使 LIFF SDK 延遲也不會影響前端運作
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('LIFF init timeout')), 3000)
  })

  try {
    if (activeLiff && activeLiff.init) {
      await Promise.race([
        activeLiff.init({ liffId: '2011703143-uGCyFHl4' }),
        timeoutPromise
      ])
      
      isLiffInitialized.value = true
      console.log('✅ LIFF SDK root initialization success')

      if (activeLiff.isLoggedIn()) {
        const profile = await activeLiff.getProfile()
        globalUserProfile.value = profile
        globalLineUserId.value = profile.userId
        console.log('✅ LIFF Profile loaded globally, User ID:', profile.userId)

        try {
          const res = await fetch(`${API_BASE_URL}/auth/auto-login-by-line-id`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ line_user_id: profile.userId })
          })
          if (res.ok) {
            const data = await res.json()
            if (data.access_token) {
              localStorage.setItem('agent_token', data.access_token)
              console.log('✅ 免登入驗證成功！Agent:', data.agent_code)
            }
          }
        } catch (err) {
          console.log('Auto login skip or agent not verified yet')
        }
      }
    }
  } catch (err) {
    console.warn('LIFF init warning (non-blocking fallback):', err)
  }
}
