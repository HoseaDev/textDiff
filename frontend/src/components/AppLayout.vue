<template>
  <div class="app-layout" :class="{ 'mobile-menu-open': isMobileMenuOpen }">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <button
            class="mobile-menu-btn btn btn-secondary"
            @click="toggleMobileMenu"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M3 12h18M3 6h18M3 18h18" />
            </svg>
          </button>

          <h1 class="app-title">TextDiff</h1>
        </div>

        <div class="header-right">
          <!-- 保存状态指示器 -->
          <div class="save-indicator">
            <span v-if="documentStore.saveState.isSaving" class="saving">
              <span class="loading"></span>
              保存中...
            </span>
            <span v-else-if="!documentStore.hasUnsavedChanges" class="saved">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M20 6L9 17l-5-5" stroke-width="2" stroke-linecap="round" />
              </svg>
              已保存
            </span>
            <span v-else class="unsaved">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="8" />
              </svg>
              未保存
            </span>
            <span v-if="documentStore.saveState.lastSaved" class="last-saved">
              {{ formatTime(documentStore.saveState.lastSaved) }}
            </span>
          </div>

          <!-- 设置按钮 -->
          <button class="btn btn-secondary btn-sm" @click="showSettings = true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3" stroke-width="2" stroke-linecap="round" />
            </svg>
            <span class="hide-mobile">设置</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="app-main">
      <!-- 左侧边栏（版本列表） -->
      <aside
        class="app-sidebar"
        :class="{ 'is-open': isMobileMenuOpen }"
      >
        <div class="sidebar-header">
          <h2>版本历史</h2>
          <button
            class="mobile-close-btn"
            @click="isMobileMenuOpen = false"
          >
            ×
          </button>
        </div>
        <div class="sidebar-content">
          <slot name="sidebar"></slot>
        </div>
      </aside>

      <!-- 主编辑区/对比区 -->
      <main class="app-content">
        <slot></slot>
      </main>
    </div>

    <!-- 设置模态框 -->
    <div v-if="showSettings" class="modal-overlay" @click="showSettings = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>保存设置</h2>
          <button class="btn-close" @click="showSettings = false">×</button>
        </div>
        <div class="modal-body">
          <slot name="settings"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDocumentStore } from '@/stores/document'

const documentStore = useDocumentStore()
const isMobileMenuOpen = ref(false)
const showSettings = ref(false)

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

function formatTime(date: Date) {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`

  const days = Math.floor(hours / 24)
  return `${days}天前`
}
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

// ========== 顶部导航栏 ==========
.app-header {
  height: 60px;
  background-color: $color-bg-primary;
  border-bottom: 1px solid $color-border;
  z-index: 100;

  @include mobile {
    height: 50px;
  }
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 $spacing-md;

  @include mobile {
    padding: 0 $spacing-sm;
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.mobile-menu-btn {
  display: none;
  padding: $spacing-xs;

  @include tablet {
    display: flex;
  }
}

.app-title {
  font-size: $font-size-xl;
  font-weight: 700;
  color: $color-primary;

  @include mobile {
    font-size: $font-size-lg;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  @include mobile {
    gap: $spacing-sm;
  }
}

// 保存状态指示器
.save-indicator {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-xs $spacing-sm;
  background-color: $color-bg-secondary;
  border-radius: $border-radius-md;
  font-size: $font-size-sm;

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .saving {
    color: $color-info;
  }

  .saved {
    color: $color-success;
  }

  .unsaved {
    color: $color-warning;
  }

  .last-saved {
    color: $color-text-secondary;
    font-size: $font-size-xs;

    @include mobile {
      display: none;
    }
  }
}

// ========== 主内容区 ==========
.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

// ========== 侧边栏 ==========
.app-sidebar {
  width: 300px;
  background-color: $color-bg-secondary;
  border-right: 1px solid $color-border;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  @include tablet {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform $transition-base;
    box-shadow: $shadow-lg;

    &.is-open {
      transform: translateX(0);
    }
  }

  @include mobile {
    width: 80vw;
    max-width: 300px;
  }
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;

  h2 {
    font-size: $font-size-lg;
    font-weight: 600;
  }
}

.mobile-close-btn {
  display: none;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: $color-text-secondary;

  @include tablet {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-sm;
}

// ========== 主编辑区 ==========
.app-content {
  flex: 1;
  overflow: auto;
  background-color: $color-bg-primary;
}

// ========== 模态框 ==========
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
  padding: $spacing-md;
}

.modal-content {
  background-color: $color-bg-primary;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-lg;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  @include mobile {
    max-width: 100%;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;

  h2 {
    font-size: $font-size-lg;
    font-weight: 600;
  }
}

.btn-close {
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: $color-text-secondary;
  transition: color $transition-fast;

  &:hover {
    color: $color-text-primary;
  }
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-md;
}

// 移动端菜单打开时，阻止背景滚动
.mobile-menu-open {
  @include tablet {
    overflow: hidden;
  }
}
</style>
