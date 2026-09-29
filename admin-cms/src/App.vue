<template>
  <div class="min-h-screen flex bg-gray-100">
    <!-- 側邊欄導覽區 -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col shadow-xl">
      <div class="p-5 text-lg font-bold border-b border-slate-800 flex items-center gap-2">
        <span>🛡️</span> 保險通路管理後台
      </div>
      <nav class="flex-1 p-4 space-y-1 text-sm font-medium">
        <router-link to="/assets" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition" active-class="bg-emerald-600 text-white font-bold">
          <span>📦</span> 素材與表單管理
        </router-link>
        <router-link to="/batch-push" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition" active-class="bg-emerald-600 text-white font-bold">
          <span>📢</span> 通知與推播發送中心
        </router-link>
        <router-link to="/tags" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition" active-class="bg-emerald-600 text-white font-bold">
          <span>🏷️</span> 分眾標籤管理
        </router-link>
        <router-link to="/agents" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition" active-class="bg-emerald-600 text-white font-bold">
          <span>👥</span> 業務員主檔管理
        </router-link>
      </nav>
      <div class="p-4 border-t border-slate-800 text-xs text-slate-400">
        Insurance CMS v1.0
      </div>
    </aside>

    <!-- 主要內容區 -->
    <main class="flex-1 p-8 overflow-y-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>
