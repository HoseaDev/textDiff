<template>
  <div class="diff-viewer">
    <div class="diff-header">
      <h3>对比结果</h3>
      <div class="diff-controls">
        <span class="control-label">显示：</span>
        <select v-model="displayMode" class="diff-select">
          <option value="diff-only">仅差异</option>
          <option value="full-text">完整文本</option>
        </select>

        <span class="control-label">粒度：</span>
        <select v-model="diffMode" class="diff-select">
          <option value="word">词级</option>
          <option value="character">字符级</option>
          <option value="line">行级</option>
          <option value="semantic">智能对比</option>
        </select>

        <label class="checkbox-label">
          <input type="checkbox" v-model="ignoreCase" />
          忽略大小写
        </label>

        <label class="checkbox-label">
          <input type="checkbox" v-model="ignoreWhitespace" />
          忽略空白
        </label>

        <button class="btn btn-close" @click="$emit('close')">关闭</button>
      </div>
    </div>

    <div class="diff-stats">
      <span class="stat-pill">
        新增：<strong>{{ stats.added }}</strong>
      </span>
      <span class="stat-pill">
        删除：<strong>{{ stats.deleted }}</strong>
      </span>
      <span class="stat-pill">
        修改：<strong>{{ stats.modified }}</strong>
      </span>
    </div>

    <div class="version-info">
      <span class="version-label">从 版本 {{ oldVersionNumber }} → 版本 {{ newVersionNumber }}</span>
    </div>

    <div class="diff-content">
      <div class="diff-unified" v-html="renderUnifiedDiff"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { DiffResponse, DiffChange } from '@/types'

interface Props {
  diffData: DiffResponse | null
  documentId?: string
  oldVersionId?: string
  newVersionId?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['close', 'refresh'])

const displayMode = ref<'diff-only' | 'full-text'>('diff-only')
const diffMode = ref('word')
const ignoreCase = ref(false)
const ignoreWhitespace = ref(false)

const oldVersionNumber = computed(() => props.diffData?.old_version_number ?? 0)
const newVersionNumber = computed(() => props.diffData?.new_version_number ?? 0)
const changes = computed(() => props.diffData?.changes ?? [])
const stats = computed(() => props.diffData?.stats ?? {
  added: 0,
  deleted: 0,
  modified: 0,
  unchanged: 0
})

const renderUnifiedDiff = computed(() => {
  if (!props.diffData) return '<div class="empty">暂无对比数据</div>'

  if (displayMode.value === 'full-text') {
    return generateFullTextDiff(changes.value)
  } else {
    return generateDiffOnlyDiff(changes.value)
  }
})

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function generateDiffOnlyDiff(changes: DiffChange[]): string {
  if (changes.length === 0) {
    return '<div class="empty">两个版本内容相同，无差异</div>'
  }

  // 仅显示有差异的部分
  return changes.map(change => {
    if (change.type === 'added') {
      const text = escapeHtml(change.new_text || '')
      return `<span class="diff-added">${text}</span>`
    } else if (change.type === 'deleted') {
      const text = escapeHtml(change.old_text || '')
      return `<span class="diff-deleted">${text}</span>`
    } else if (change.type === 'modified') {
      const oldText = escapeHtml(change.old_text || '')
      const newText = escapeHtml(change.new_text || '')
      return `<span class="diff-deleted">${oldText}</span><span class="diff-added">${newText}</span>`
    }
    return '' // 不显示未变化的内容
  }).filter(Boolean).join('')
}

function generateFullTextDiff(changes: DiffChange[]): string {
  if (changes.length === 0) {
    return '<div class="empty">两个版本内容相同，无差异</div>'
  }

  // 显示完整文本，在原文中标记差异
  return changes.map(change => {
    if (change.type === 'added') {
      const text = escapeHtml(change.new_text || '')
      return `<span class="diff-added">${text}</span>`
    } else if (change.type === 'deleted') {
      const text = escapeHtml(change.old_text || '')
      return `<span class="diff-deleted">${text}</span>`
    } else if (change.type === 'modified') {
      const oldText = escapeHtml(change.old_text || '')
      const newText = escapeHtml(change.new_text || '')
      return `<span class="diff-deleted">${oldText}</span><span class="diff-added">${newText}</span>`
    } else {
      // 显示未变化的内容
      const text = change.old_text || change.new_text || ''
      return `<span class="diff-unchanged">${escapeHtml(text)}</span>`
    }
  }).join('')
}

// 监听选项变化，重新请求差异数据
watch([diffMode, ignoreCase, ignoreWhitespace], () => {
  // 通知父组件重新获取差异数据
  emit('refresh', {
    diffMode: diffMode.value,
    ignoreCase: ignoreCase.value,
    ignoreWhitespace: ignoreWhitespace.value
  })
})
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.diff-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

// 头部
.diff-header {
  padding: $spacing-md $spacing-lg;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);

  h3 {
    font-size: $font-size-xl;
    font-weight: 600;
    margin: 0 0 $spacing-md 0;
    color: var(--color-text-primary);
  }
}

.diff-controls {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  flex-wrap: wrap;

  @include mobile {
    gap: $spacing-sm;
  }
}

.control-label {
  color: var(--color-text-secondary);
  font-size: $font-size-sm;
  font-weight: 500;
}

.diff-select {
  background: var(--color-input-bg);
  color: var(--color-text-primary);
  border: 1px solid var(--color-input-border);
  border-radius: $border-radius-md;
  padding: 8px 12px;
  font-size: $font-size-sm;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: var(--color-input-focus-border);
    box-shadow: 0 0 0 2px var(--color-input-focus-shadow);
  }
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: $font-size-sm;
  color: var(--color-text-primary);
  cursor: pointer;
  user-select: none;
  padding: 6px 12px;
  border-radius: $border-radius-md;
  transition: background 0.2s;

  &:hover {
    background: var(--color-bg-hover);
  }

  input[type="checkbox"] {
    cursor: pointer;
    width: 16px;
    height: 16px;
  }
}

.btn-close {
  background: var(--color-button-secondary-bg);
  color: var(--color-button-secondary-text);
  border: 1px solid var(--color-border);
  padding: 8px 16px;
  border-radius: $border-radius-md;
  cursor: pointer;
  font-size: $font-size-sm;
  font-weight: 500;
  margin-left: auto;
  transition: all 0.2s;

  &:hover {
    background: var(--color-button-secondary-hover);
    transform: translateY(-1px);
  }
}

// 统计信息
.diff-stats {
  display: flex;
  gap: 12px;
  padding: $spacing-md $spacing-lg;
  background: var(--color-bg-tertiary);
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;

  @include mobile {
    gap: $spacing-sm;
    padding: $spacing-sm $spacing-md;
  }
}

.stat-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  font-size: $font-size-sm;
  color: var(--color-text-secondary);

  strong {
    color: var(--color-text-primary);
    font-weight: 600;
  }
}

.version-info {
  padding: $spacing-sm $spacing-lg;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
}

.version-label {
  font-weight: 500;
}

// 差异内容
.diff-content {
  flex: 1;
  overflow: auto;
  background: var(--color-editor-bg);

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

.diff-unified {
  padding: $spacing-lg;
  min-height: 200px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: $font-family-mono;
  font-size: $font-size-base;
  line-height: 1.8;
  color: var(--color-text-primary);

  @include mobile {
    padding: $spacing-md;
    font-size: $font-size-sm;
  }

  .empty {
    color: var(--color-text-tertiary);
    text-align: center;
    padding: $spacing-2xl;
    font-size: $font-size-lg;
  }

  // 新增内容：绿色背景
  :deep(.diff-added) {
    background: var(--color-diff-added);
    color: var(--color-diff-added-text);
    border-radius: 3px;
    padding: 2px 4px;
    font-weight: 500;
  }

  // 删除内容：红色背景 + 删除线
  :deep(.diff-deleted) {
    background: var(--color-diff-deleted);
    color: var(--color-diff-deleted-text);
    text-decoration: line-through;
    border-radius: 3px;
    padding: 2px 4px;
  }

  // 未变化内容
  :deep(.diff-unchanged) {
    color: var(--color-text-primary);
    opacity: 0.7;
  }
}
</style>
