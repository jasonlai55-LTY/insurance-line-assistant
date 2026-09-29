<template>
  <div class="space-y-4">
    <!-- 歡迎卡片 -->
    <div class="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-5 rounded-2xl shadow-lg">
      <div class="text-sm opacity-90">歡迎使用</div>
      <div class="text-2xl font-extrabold mt-1">保險業務 LINE 助手</div>
      <p class="text-xs opacity-80 mt-2">提供商品 DM、銷售手冊、行政規範一鍵查詢與轉發</p>
    </div>

    <!-- 功能快捷區 -->
    <div class="grid grid-cols-2 gap-3">
      <router-link to="/products" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center hover:bg-gray-50 transition">
        <span class="text-3xl mb-1">📦</span>
        <span class="font-bold text-gray-800 text-sm">商品專區</span>
        <span class="text-xs text-gray-500">DM/銷售手冊/條款</span>
      </router-link>

      <router-link to="/guidelines" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center hover:bg-gray-50 transition">
        <span class="text-3xl mb-1">📋</span>
        <span class="font-bold text-gray-800 text-sm">行政規範庫</span>
        <span class="text-xs text-gray-500">投保/理賠指引表單</span>
      </router-link>

      <router-link to="/notifications" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center hover:bg-gray-50 transition">
        <span class="text-3xl mb-1">🔔</span>
        <span class="font-bold text-gray-800 text-sm">個人通知中心</span>
        <span class="text-xs text-gray-500">照會/異動歷史紀錄</span>
      </router-link>

      <router-link to="/login" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center hover:bg-gray-50 transition">
        <span class="text-3xl mb-1">🔐</span>
        <span class="font-bold text-gray-800 text-sm">工號與 OTP 綁定</span>
        <span class="text-xs text-gray-500">解鎖內部限定文件</span>
      </router-link>
    </div>

    <!-- 安全說明 -->
    <div class="bg-blue-50 border border-blue-200 text-blue-800 p-3 rounded-xl text-xs flex items-start gap-2">
      <span class="text-base">ℹ️</span>
      <div>
        <div class="font-bold">資安與合規防護</div>
        <p class="mt-0.5 opacity-90">所有行政照會資訊已進行去識別化與個資脫敏處理。限內部瀏覽之核保規範需通過 OTP 身分驗證。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
