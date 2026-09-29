<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <header class="bg-line-green text-white p-4 shadow-md flex items-center justify-between">
      <h1 class="text-lg font-bold flex items-center gap-2">
        <span>🛡️</span> 保險業務 LINE 助手
      </h1>
      <span class="text-xs bg-white/20 px-2 py-1 rounded">LIFF App</span>
    </header>

    <main class="flex-1 p-4 pb-20">
      <router-view />
    </main>

    <!-- 行動端底部導覽列 -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around p-2 text-xs font-medium text-gray-600">
      <router-link to="/" class="flex flex-col items-center gap-1" active-class="text-line-green">
        <span>🏠</span>
        <span>首頁</span>
      </router-link>
      <router-link to="/products" class="flex flex-col items-center gap-1" active-class="text-line-green">
        <span>📄</span>
        <span>商品專區</span>
      </router-link>
      <router-link to="/guidelines" class="flex flex-col items-center gap-1" active-class="text-line-green">
        <span>📚</span>
        <span>行政規範</span>
      </router-link>
      <router-link to="/notifications" class="flex flex-col items-center gap-1" active-class="text-line-green">
        <span>🔔</span>
        <span>通知中心</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
</script>
