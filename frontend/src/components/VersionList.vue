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
        加载中...
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
}

.version-filter {
  padding: $spacing-sm;
  border-bottom: 1px solid $color-border;
}

.filter-select {
  width: 100%;
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $color-border;
  border-radius: $border-radius-sm;
  font-size: $font-size-sm;
  background-color: $color-bg-primary;

  &:focus {
    outline: none;
    border-color: $color-primary;
  }
}

.version-items {
  flex: 1;
  overflow-y: auto;
}

.version-item {
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;
  cursor: pointer;
  transition: background-color $transition-fast;

  &:hover {
    background-color: $color-bg-tertiary;
  }

  &.active {
    background-color: rgba($color-primary, 0.1);
    border-left: 3px solid $color-primary;
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
  color: $color-text-primary;
}

.version-type {
  padding: 2px 6px;
  font-size: $font-size-xs;
  border-radius: $border-radius-sm;

  &.type-manual {
    background-color: rgba($color-primary, 0.1);
    color: $color-primary;
  }

  &.type-auto {
    background-color: rgba($color-text-secondary, 0.1);
    color: $color-text-secondary;
  }
}

.version-meta {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-xs;
  color: $color-text-secondary;
  margin-bottom: $spacing-xs;
}

.version-message {
  font-size: $font-size-sm;
  color: $color-text-secondary;
  margin-bottom: $spacing-xs;
  @include text-truncate-lines(2);
}

.version-stats {
  font-size: $font-size-xs;
  color: $color-text-disabled;
}

.loading-container,
.empty-state {
  padding: $spacing-lg;
  text-align: center;
  color: $color-text-secondary;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
}
</style>
