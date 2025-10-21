/**
 * 主题管理 Store
 */
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeMode = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  // 状态
  const mode = ref<ThemeMode>('light')

  // 初始化主题
  function initTheme() {
    // 从 localStorage 读取保存的主题
    const savedTheme = localStorage.getItem('theme') as ThemeMode
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      mode.value = savedTheme
    } else {
      // 检测系统主题偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      mode.value = prefersDark ? 'dark' : 'light'
    }

    // 应用主题
    applyTheme(mode.value)
  }

  // 切换主题
  function toggleTheme() {
    mode.value = mode.value === 'light' ? 'dark' : 'light'
  }

  // 设置主题
  function setTheme(theme: ThemeMode) {
    mode.value = theme
  }

  // 应用主题到DOM
  function applyTheme(theme: ThemeMode) {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }

  // 监听主题变化
  watch(mode, (newTheme) => {
    applyTheme(newTheme)
  })

  return {
    mode,
    initTheme,
    toggleTheme,
    setTheme
  }
})
