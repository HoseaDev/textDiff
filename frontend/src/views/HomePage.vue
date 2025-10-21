<template>
  <div class="home-page">
    <div class="container">
      <header class="header">
        <h1>📝 TextDiff</h1>
        <p>文本版本管理与差异比较系统</p>
      </header>

      <div class="actions">
        <div class="create-card">
          <h2>创建新文档</h2>
          <input
            v-model="newDocTitle"
            type="text"
            placeholder="输入文档标题..."
            class="input"
            @keyup.enter="createDocument"
          />
          <button class="btn btn-primary" @click="createDocument" :disabled="!newDocTitle || creating">
            {{ creating ? '创建中...' : '创建文档' }}
          </button>
        </div>

        <div class="documents-card" v-if="documents.length > 0">
          <h2>最近文档</h2>
          <div class="document-list">
            <div
              v-for="doc in documents"
              :key="doc.id"
              class="document-item"
              @click="openDocument(doc.id)"
            >
              <div class="doc-title">{{ doc.title }}</div>
              <div class="doc-meta">
                <span>v{{ doc.current_version_number }}</span>
                <span>{{ formatDate(doc.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { documentApi } from '@/api/client'
import type { Document } from '@/types'

const router = useRouter()
const newDocTitle = ref('')
const creating = ref(false)
const documents = ref<Document[]>([])

onMounted(async () => {
  try {
    documents.value = await documentApi.list({ limit: 10 })
  } catch (error) {
    console.error('Failed to load documents:', error)
  }
})

async function createDocument() {
  if (!newDocTitle.value.trim()) return

  creating.value = true
  try {
    const doc = await documentApi.create({
      title: newDocTitle.value,
      initial_content: '',
      author: 'user'
    })
    router.push(`/document/${doc.id}`)
  } catch (error) {
    console.error('Failed to create document:', error)
    alert('创建文档失败')
  } finally {
    creating.value = false
  }
}

function openDocument(id: string) {
  router.push(`/document/${id}`)
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
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

.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: $spacing-2xl $spacing-md;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: $spacing-2xl;

  h1 {
    font-size: 3rem;
    margin-bottom: $spacing-sm;

    @include mobile {
      font-size: 2rem;
    }
  }

  p {
    font-size: $font-size-lg;
    opacity: 0.9;

    @include mobile {
      font-size: $font-size-base;
    }
  }
}

.actions {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.create-card,
.documents-card {
  background: white;
  border-radius: $border-radius-lg;
  padding: $spacing-xl;
  box-shadow: $shadow-lg;

  @include mobile {
    padding: $spacing-md;
  }

  h2 {
    font-size: $font-size-xl;
    margin-bottom: $spacing-md;
    color: $color-text-primary;
  }
}

.create-card {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;

  .input {
    font-size: $font-size-lg;
    padding: $spacing-md;
  }

  .btn {
    padding: $spacing-md $spacing-lg;
    font-size: $font-size-lg;
  }
}

.document-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.document-item {
  padding: $spacing-md;
  border: 1px solid $color-border;
  border-radius: $border-radius-md;
  cursor: pointer;
  transition: all $transition-fast;

  &:hover {
    background: $color-bg-secondary;
    border-color: $color-primary;
    transform: translateX(4px);
  }
}

.doc-title {
  font-size: $font-size-base;
  font-weight: 600;
  color: $color-text-primary;
  margin-bottom: $spacing-xs;
}

.doc-meta {
  display: flex;
  gap: $spacing-md;
  font-size: $font-size-sm;
  color: $color-text-secondary;
}
</style>
