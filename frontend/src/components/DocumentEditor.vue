<template>
  <div class="document-editor">
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button class="btn btn-primary" @click="handleSave" :disabled="!hasChanges || isSaving">
          <svg v-if="!isSaving" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke-width="2"/>
            <polyline points="17 21 17 13 7 13 7 21" stroke-width="2"/>
            <polyline points="7 3 7 8 15 8" stroke-width="2"/>
          </svg>
          <span class="loading" v-else></span>
          保存 (Ctrl+S)
        </button>
        <span class="word-count">{{ wordCount }} 字</span>
      </div>
      <div class="toolbar-right">
        <button class="btn btn-secondary btn-sm" @click="$emit('show-diff')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" stroke-width="2"/>
          </svg>
          查看差异
        </button>
      </div>
    </div>

    <textarea
      ref="editorRef"
      class="editor-textarea"
      :value="content"
      @input="handleInput"
      @keydown="handleKeydown"
      placeholder="开始输入内容..."
      :disabled="disabled"
    ></textarea>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDocumentStore } from '@/stores/document'
import { useDebounceFn } from '@/composables/useDebounceFn'

interface Props {
  content: string
  disabled?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:content', 'save', 'show-diff'])

const documentStore = useDocumentStore()
const editorRef = ref<HTMLTextAreaElement>()

const hasChanges = computed(() => documentStore.hasUnsavedChanges)
const isSaving = computed(() => documentStore.saveState.isSaving)
const wordCount = computed(() => props.content.length)

// 自动保存
const autoSave = useDebounceFn(async () => {
  if (documentStore.isAutoSaveEnabled && hasChanges.value) {
    await documentStore.saveVersion(undefined, 'auto')
  }
}, documentStore.saveState.autoSaveInterval)

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:content', target.value)
  documentStore.updateContent(target.value)

  // 触发自动保存
  if (documentStore.isAutoSaveEnabled) {
    autoSave()
  }
}

async function handleSave() {
  try {
    await documentStore.saveVersion(undefined, 'manual')
    emit('save')
  } catch (error) {
    console.error('Save failed:', error)
    alert('保存失败，请重试')
  }
}

function handleKeydown(event: KeyboardEvent) {
  // Ctrl+S 保存
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault()
    if (hasChanges.value) {
      handleSave()
    }
  }
}

onMounted(() => {
  // 离开页面前警告
  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    if (hasChanges.value && documentStore.saveSettings.warnBeforeLeave) {
      e.preventDefault()
      e.returnValue = ''
    }
  }
  window.addEventListener('beforeunload', handleBeforeUnload)

  onUnmounted(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload)
  })
})
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.document-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg-primary);
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);

  @include mobile {
    flex-direction: column;
    gap: $spacing-sm;
    align-items: stretch;
  }
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  @include mobile {
    justify-content: space-between;
  }
}

.word-count {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  padding: 4px 12px;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
}

.editor-textarea {
  flex: 1;
  padding: $spacing-lg;
  font-family: $font-family-mono;
  font-size: $font-size-base;
  line-height: 1.8;
  border: none;
  outline: none;
  resize: none;
  background: var(--color-editor-bg);
  color: var(--color-text-primary);

  @include mobile {
    padding: $spacing-md;
    font-size: $font-size-sm;
  }

  &::placeholder {
    color: var(--color-text-tertiary);
  }

  &::selection {
    background: var(--color-editor-selection);
  }

  &:disabled {
    background: var(--color-bg-tertiary);
    cursor: not-allowed;
    opacity: 0.6;
  }
}
</style>
