<template>
  <div class="version-list">
    <div class="version-filter">
      <select v-model="selectedFilter" class="filter-select" @change="handleFilterChange">
        <option value="">所有版本</option>
        <option value="manual">手动保存</option>
        <option value="auto">自动保存</option>
      </select>
    </div>

    <div class="version-items">
      <div
        v-for="version in versions"
        :key="version.id"
        class="version-item"
        :class="{ active: version.id === selectedVersionId }"
        @click="$emit('select', version)"
      >
        <div class="version-header">
          <span class="version-number">v{{ version.version_number }}</span>
          <span class="version-type" :class="`type-${version.save_type}`">
            {{ version.save_type === 'manual' ? '手动' : '自动' }}
          </span>
        </div>
        <div class="version-meta">
          <span class="version-time">{{ formatDate(version.created_at) }}</span>
          <span class="version-author">{{ version.author }}</span>
        </div>
        <div v-if="version.commit_message" class="version-message">
          {{ version.commit_message }}
        </div>
        <div class="version-stats">
          {{ version.content_length }} 字
        </div>
      </div>

      <div v-if="loading" class="loading-container">
        <span class="loading"></span>
        加载中222...
      </div>

      <div v-if="!loading && versions.length === 0" class="empty-state">
        暂无版本
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { VersionListItem } from '@/types'

interface Props {
  versions: VersionListItem[]
  selectedVersionId?: string
  loading?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['select', 'filter-change'])

const selectedFilter = ref('')

function handleFilterChange() {
  emit('filter-change', selectedFilter.value || undefined)
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`

  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.version-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-sidebar-bg);
}

.version-filter {
  padding: $spacing-md;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
}

.filter-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-input-border);
  border-radius: $border-radius-md;
  font-size: $font-size-sm;
  background: var(--color-input-bg);
  color: var(--color-text-primary);
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: var(--color-input-focus-border);
    box-shadow: 0 0 0 2px var(--color-input-focus-shadow);
  }
}

.version-items {
  flex: 1;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--color-scrollbar-track);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--color-scrollbar-thumb);
    border-radius: 3px;

    &:hover {
      background: var(--color-scrollbar-thumb-hover);
    }
  }
}

.version-item {
  padding: $spacing-md;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: all $transition-fast;
  background: var(--color-sidebar-bg);

  &:hover {
    background: var(--color-bg-hover);
  }

  &.active {
    background: var(--color-primary-light);
    border-left: 3px solid var(--color-primary);
    padding-left: calc(#{$spacing-md} - 3px);
  }
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-xs;
}

.version-number {
  font-weight: 600;
  font-size: $font-size-base;
  color: var(--color-text-primary);
}

.version-type {
  padding: 3px 8px;
  font-size: $font-size-xs;
  border-radius: $border-radius-sm;
  font-weight: 500;

  &.type-manual {
    background: var(--color-primary-light);
    color: var(--color-primary);
  }

  &.type-auto {
    background: var(--color-bg-tertiary);
    color: var(--color-text-secondary);
  }
}

.version-meta {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  margin-bottom: $spacing-xs;
}

.version-message {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin-bottom: $spacing-xs;
  line-height: 1.4;
  @include text-truncate-lines(2);
}

.version-stats {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
}

.loading-container,
.empty-state {
  padding: $spacing-xl;
  text-align: center;
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
}
</style>
