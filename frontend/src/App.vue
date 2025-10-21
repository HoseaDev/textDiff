<template>
  <div id="app">
    <!-- 导航栏 - 仅在认证页面显示 -->
    <Navbar v-if="showNavbar" />

    <!-- 主内容区域 -->
    <main class="main-content" :class="{ 'with-navbar': showNavbar }">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

const route = useRoute()

// 在登录和注册页面不显示导航栏
const showNavbar = computed(() => {
  const publicPages = ['/login', '/register']
  return !publicPages.includes(route.path)
})
</script>

<style>
@import '@/assets/styles/global.scss';

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
}

.main-content {
  flex: 1;
  width: 100%;
}

.main-content.with-navbar {
  padding-top: 0;
}
</style>
