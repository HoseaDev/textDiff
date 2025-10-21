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
  background: #0b0f14;
  color: #e5e7eb;
}

// 头部
.diff-header {
  padding: $spacing-md;
  background: #121821;
  border-bottom: 1px solid #222b36;

  h3 {
    font-size: $font-size-lg;
    font-weight: 600;
    margin: 0 0 $spacing-sm 0;
    color: #cbd5e1;
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
  color: #6b7280;
  font-size: $font-size-sm;
}

.diff-select {
  background: #0e1622;
  color: #e5e7eb;
  border: 1px solid #222b36;
  border-radius: 10px;
  padding: 6px 10px;
  font-size: $font-size-sm;

  &:focus {
    outline: none;
    border-color: #2b3646;
  }
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: $font-size-sm;
  color: #e5e7eb;
  cursor: pointer;
  user-select: none;

  input[type="checkbox"] {
    cursor: pointer;
  }
}

.btn-close {
  background: #0e1622;
  color: #e5e7eb;
  border: 1px solid #222b36;
  padding: 6px 12px;
  border-radius: 10px;
  cursor: pointer;
  font-size: $font-size-sm;
  margin-left: auto;

  &:hover {
    border-color: #2b3646;
    background: #101a28;
  }
}

// 统计信息
.diff-stats {
  display: flex;
  gap: 10px;
  padding: $spacing-sm $spacing-md;
  background: #121821;
  border-bottom: 1px solid #222b36;
  flex-wrap: wrap;

  @include mobile {
    gap: $spacing-xs;
  }
}

.stat-pill {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid #222b36;
  background: #0e1622;
  font-size: $font-size-sm;
  color: #9ca3af;

  strong {
    color: #e5e7eb;
    margin-left: 4px;
  }
}

.version-info {
  padding: $spacing-xs $spacing-md;
  background: #0b1320;
  border-bottom: 1px solid #222b36;
  font-size: $font-size-sm;
  color: #6b7280;
}

.version-label {
  font-weight: 500;
}

// 差异内容
.diff-content {
  flex: 1;
  overflow: auto;
  background: #0b1320;
}

.diff-unified {
  padding: $spacing-md;
  min-height: 200px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: $font-family-mono;
  font-size: $font-size-sm;
  line-height: 1.8;

  @include mobile {
    padding: $spacing-sm;
    font-size: $font-size-xs;
  }

  .empty {
    color: #6b7280;
    text-align: center;
    padding: $spacing-xl;
  }

  // 新增内容：绿色背景
  :deep(.diff-added) {
    background: rgba(6, 94, 46, 0.5);
    color: #78f3b1;
    border-radius: 4px;
    padding: 1px 2px;
  }

  // 删除内容：红色背景 + 删除线
  :deep(.diff-deleted) {
    background: rgba(128, 0, 0, 0.5);
    color: #ff9aa2;
    text-decoration: line-through;
    border-radius: 4px;
    padding: 1px 2px;
  }

  // 未变化内容：浅色
  :deep(.diff-unchanged) {
    color: #cbd5e1;
  }
}

// 自定义滚动条
.diff-content {
  @include custom-scrollbar;

  &::-webkit-scrollbar-track {
    background: #0b1320;
  }

  &::-webkit-scrollbar-thumb {
    background: #222b36;

    &:hover {
      background: #2b3646;
    }
  }
}
</style>
