export const API_BASE_URL = window.location.hostname.includes('ngrok-free.dev') || window.location.hostname.includes('trycloudflare.com')
  ? '/api/v1'
  : (import.meta.env.VITE_API_BASE_URL || 'https://insurance-line-assistant.onrender.com/api/v1')
