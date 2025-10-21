<template>
  <div class="app-layout" :class="{ 'mobile-menu-open': isMobileMenuOpen }">
    <!-- 文档信息栏 -->
    <div class="document-info-bar">
      <div class="info-left">
        <!-- 移动端菜单按钮 -->
        <button class="mobile-menu-btn" @click="toggleMobileMenu">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12h18M3 6h18M3 18h18" />
          </svg>
        </button>

        <div class="document-title-section">
          <span class="document-icon">📄</span>
          <h1 class="document-title">{{ documentStore.currentDocument?.title || '加载中321...' }}</h1>
        </div>
      </div>

      <div class="info-right">
        <!-- 保存状态指示器 -->
        <div class="save-indicator">
          <span v-if="documentStore.saveState.isSaving" class="saving">
            <span class="loading-spinner"></span>
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
      </div>
    </div>

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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDocumentStore } from '@/stores/document'

const documentStore = useDocumentStore()
const isMobileMenuOpen = ref(false)

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
  height: calc(100vh - 60px); // 减去Navbar高度
  overflow: hidden;
  background: var(--color-bg-primary);
}

// ========== 文档信息栏 ==========
.document-info-bar {
  height: 56px;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 $spacing-lg;
  flex-shrink: 0;

  @include mobile {
    height: 50px;
    padding: 0 $spacing-md;
  }
}

.info-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  flex: 1;
  min-width: 0; // 允许子元素收缩
}

.mobile-menu-btn {
  display: none;
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: 6px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background: var(--color-bg-hover);
    color: var(--color-text-primary);
  }

  @include tablet {
    display: flex;
  }
}

.document-title-section {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex: 1;
  min-width: 0;
}

.document-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.document-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  @include mobile {
    font-size: $font-size-base;
  }
}

.info-right {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  flex-shrink: 0;

  @include mobile {
    gap: $spacing-sm;
  }
}

// 保存状态指示器
.save-indicator {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: 6px 12px;
  background: var(--color-bg-tertiary);
  border-radius: $border-radius-md;
  font-size: $font-size-sm;

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .saving {
    color: var(--color-info);
  }

  .saved {
    color: var(--color-success);
  }

  .unsaved {
    color: var(--color-warning);
  }

  .last-saved {
    color: var(--color-text-tertiary);
    font-size: $font-size-xs;

    @include mobile {
      display: none;
    }
  }

  .loading-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: var(--color-info);
    border-right-color: var(--color-info);
    border-radius: 50%;
    animation: spin-smooth 0.8s linear infinite;
  }
}

@keyframes spin-smooth {
  to {
    transform: rotate(360deg);
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
  width: 320px;
  background: var(--color-sidebar-bg);
  border-right: 1px solid var(--color-sidebar-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  @include tablet {
    position: fixed;
    top: 60px; // Navbar高度
    left: 0;
    bottom: 0;
    z-index: 900;
    transform: translateX(-100%);
    transition: transform $transition-base;
    box-shadow: 4px 0 12px var(--color-shadow);

    &.is-open {
      transform: translateX(0);
    }
  }

  @include mobile {
    width: 80vw;
    max-width: 320px;
  }
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md $spacing-lg;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-secondary);

  h2 {
    font-size: $font-size-lg;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }
}

.mobile-close-btn {
  display: none;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 6px;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.2s;

  &:hover {
    background: var(--color-bg-hover);
    color: var(--color-text-primary);
  }

  @include tablet {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-md;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: var(--color-scrollbar-track);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--color-scrollbar-thumb);
    border-radius: 4px;

    &:hover {
      background: var(--color-scrollbar-thumb-hover);
    }
  }
}

// ========== 主编辑区 ==========
.app-content {
  flex: 1;
  overflow: auto;
  background: var(--color-bg-primary);

  &::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }

  &::-webkit-scrollbar-track {
    background: var(--color-scrollbar-track);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--color-scrollbar-thumb);
    border-radius: 5px;

    &:hover {
      background: var(--color-scrollbar-thumb-hover);
    }
  }
}

// 移动端菜单打开时，阻止背景滚动
.mobile-menu-open {
  @include tablet {
    overflow: hidden;
  }
}

// 遮罩层(移动端侧边栏打开时)
@include tablet {
  .mobile-menu-open::after {
    content: '';
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 899;
  }
}
</style>
