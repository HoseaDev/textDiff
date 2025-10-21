<template>
  <div class="document-list-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h1>我的文档</h1>
        <span class="document-count">共 {{ totalCount }} 个文档</span>
      </div>
      <div class="toolbar-right">
        <button @click="createNewDocument" class="btn-primary">
          <span class="icon">+</span>
          新建文档
        </button>
      </div>
    </div>

    <!-- 筛选和排序 -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索文档..."
          @input="onSearch"
        />
      </div>
      <div class="sort-box">
        <label>排序:</label>
        <select v-model="sortBy" @change="loadDocuments">
          <option value="updated_at">最近更新</option>
          <option value="created_at">创建时间</option>
          <option value="title">标题</option>
        </select>
      </div>
    </div>

 

    <!-- 文档列表 -->
    <div  class="document-grid">
      <div
        v-for="doc in documents"
        :key="doc.id"
        class="document-card"
        @click="openDocument(doc.id)"
      >
        <div class="card-header">
          <h3>{{ doc.title }}</h3>
          <div class="card-actions" @click.stop>
            <button @click="showDocMenu(doc, $event)" class="btn-icon">⋮</button>
          </div>
        </div>
        <div class="card-body">
          <div class="meta-info">
            <span class="meta-item">
              <span class="label">版本:</span>
              <span class="value">v{{ doc.current_version_number }}</span>
            </span>
            <span class="meta-item">
              <span class="label">更新:</span>
              <span class="value">{{ formatDate(doc.updated_at) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div  class="empty-state">
      <div class="empty-icon">📄</div>
      <h3>还没有文档</h3>
      <p>点击上方"新建文档"按钮创建第一个文档</p>
      <button @click="createNewDocument" class="btn-primary">创建文档</button>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="btn-page"
      >
        上一页
      </button>
      <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
      <button
        @click="currentPage++"
        :disabled="currentPage >= totalPages"
        class="btn-page"
      >
        下一页
      </button>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.show"
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click="closeContextMenu"
    >
      <div @click="renameDocument(contextMenu.document)">重命名</div>
      <div @click="deleteDocument(contextMenu.document)" class="danger">删除</div>
    </div>

    <!-- 点击外部关闭菜单 -->
    <div
      v-if="contextMenu.show"
      class="context-menu-overlay"
      @click="closeContextMenu"
    ></div>

    <!-- 新建文档对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click="closeCreateDialog">
      <div class="dialog-card" @click.stop>
        <div class="dialog-header">
          <h3>新建文档</h3>
          <button @click="closeCreateDialog" class="btn-close">✕</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label for="new-doc-title">文档标题 *</label>
            <input
              id="new-doc-title"
              ref="titleInputRef"
              v-model="newDocTitle"
              type="text"
              placeholder="请输入文档标题"
              maxlength="255"
              @keyup.enter="confirmCreateDocument"
              @keyup.esc="closeCreateDialog"
            />
            <p class="input-hint">{{ newDocTitle.length }}/255</p>
          </div>
        </div>
        <div class="dialog-footer">
          <button @click="closeCreateDialog" class="btn-secondary">取消</button>
          <button
            @click="confirmCreateDocument"
            class="btn-primary"
            :disabled="!newDocTitle.trim()"
          >
            创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { documentApi } from '@/api/client'
import type { Document } from '@/types'
import { formatDate as formatDateUtil } from '@/utils/date'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()

// 状态
const documents = ref<Document[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const sortBy = ref('updated_at')
const currentPage = ref(1)
const pageSize = 20
const totalCount = ref(0)

// 加载动画类型
const loadingAnimationType = ref<'spinner' | 'dots' | 'pulse' | 'gradient'>('spinner')

// 新建文档对话框
const showCreateDialog = ref(false)
const newDocTitle = ref('')
const titleInputRef = ref<HTMLInputElement>()

// 右键菜单
const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  document: null as Document | null
})

// 计算属性
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

// 加载文档列表
async function loadDocuments() {
  isLoading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize
    const result = await documentApi.list({
      skip,
      limit: pageSize,
      sort_by: sortBy.value
    })

    documents.value = result
    totalCount.value = result.length // 注意:这里应该从后端返回总数,暂时用长度
  } catch (error: any) {
    console.error('Failed to load documents:', error)
    alert('加载文档列表失败: ' + (error.detail || error.message || '未知错误'))
  } finally {
    isLoading.value = false
  }
}

// 搜索文档
let searchTimeout: any = null
function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadDocuments()
  }, 300)
}

// 打开新建文档对话框
function createNewDocument() {
  newDocTitle.value = ''
  showCreateDialog.value = true
  nextTick(() => {
    titleInputRef.value?.focus()
  })
}

// 关闭对话框
function closeCreateDialog() {
  showCreateDialog.value = false
  newDocTitle.value = ''
}

// 确认创建文档
async function confirmCreateDocument() {
  if (!newDocTitle.value.trim()) {
    return
  }

  try {
    const newDoc = await documentApi.create({
      title: newDocTitle.value.trim(),
      initial_content: ''
    })
    closeCreateDialog()
    router.push(`/document/${newDoc.id}`)
  } catch (error: any) {
    console.error('Failed to create document:', error)
    alert('创建文档失败: ' + (error.detail || error.message || '未知错误'))
  }
}

// 打开文档
function openDocument(id: string) {
  router.push(`/document/${id}`)
}

// 显示右键菜单
function showDocMenu(doc: Document, event: MouseEvent) {
  event.preventDefault()
  event.stopPropagation()

  contextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    document: doc
  }
}

// 关闭右键菜单
function closeContextMenu() {
  contextMenu.value.show = false
}

// 重命名文档
async function renameDocument(doc: Document | null) {
  if (!doc) return

  const newTitle = prompt('请输入新的文档名称:', doc.title)
  if (newTitle && newTitle !== doc.title) {
    try {
      await documentApi.update(doc.id, { title: newTitle })
      await loadDocuments()
    } catch (error: any) {
      console.error('Failed to rename document:', error)
      alert('重命名失败: ' + (error.detail || error.message || '未知错误'))
    }
  }
}

// 删除文档
async function deleteDocument(doc: Document | null) {
  if (!doc) return

  if (confirm(`确定要删除文档"${doc.title}"吗?此操作不可恢复!`)) {
    try {
      await documentApi.delete(doc.id)
      await loadDocuments()
    } catch (error: any) {
      console.error('Failed to delete document:', error)
      alert('删除失败: ' + (error.detail || error.message || '未知错误'))
    }
  }
}

// 格式化日期
function formatDate(date: string | undefined): string {
  if (!date) return '-'
  return formatDateUtil(date, 'YYYY-MM-DD HH:mm')
}

// 监听页码变化
watch(currentPage, () => {
  loadDocuments()
})

// 组件挂载时加载文档
onMounted(() => {
  // 从 localStorage 读取加载动画类型
  const saved = localStorage.getItem('loadingAnimationType')
  if (saved && ['spinner', 'dots', 'pulse', 'gradient'].includes(saved)) {
    loadingAnimationType.value = saved as any
  }

  loadDocuments()
})
</script>

<style scoped lang="scss">
.document-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: var(--color-bg-primary);
  min-height: calc(100vh - 60px);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .toolbar-left {
    display: flex;
    align-items: baseline;
    gap: 12px;

    h1 {
      font-size: 28px;
      font-weight: 700;
      margin: 0;
      color: var(--color-text-primary);
    }

    .document-count {
      color: var(--color-text-secondary);
      font-size: 14px;
    }
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;

    .icon {
      font-size: 18px;
      font-weight: 700;
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
  }
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;

  .search-box {
    flex: 1;

    input {
      width: 100%;
      padding: 10px 16px;
      border: 1px solid var(--color-input-border);
      border-radius: 6px;
      font-size: 14px;
      box-sizing: border-box;
      background: var(--color-input-bg);
      color: var(--color-text-primary);

      &:focus {
        outline: none;
        border-color: var(--color-input-focus-border);
        box-shadow: 0 0 0 3px var(--color-input-focus-shadow);
      }
    }
  }

  .sort-box {
    display: flex;
    align-items: center;
    gap: 8px;

    label {
      font-size: 14px;
      color: var(--color-text-secondary);
    }

    select {
      padding: 8px 12px;
      border: 1px solid var(--color-input-border);
      border-radius: 6px;
      font-size: 14px;
      cursor: pointer;
      background: var(--color-input-bg);
      color: var(--color-text-primary);

      &:focus {
        outline: none;
        border-color: var(--color-input-focus-border);
      }
    }
  }
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 80px 20px;
  min-height: 400px;
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.document-card {
  background: var(--color-card-bg);
  border: 1px solid var(--color-card-border);
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: var(--color-primary);
    box-shadow: var(--color-card-shadow);
    transform: translateY(-2px);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 16px;

    h3 {
      flex: 1;
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--color-text-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .card-actions {
      .btn-icon {
        padding: 4px 8px;
        background: none;
        border: none;
        color: var(--color-text-secondary);
        font-size: 20px;
        cursor: pointer;
        border-radius: 4px;

        &:hover {
          background: var(--color-bg-hover);
        }
      }
    }
  }

  .card-body {
    .meta-info {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .meta-item {
        display: flex;
        font-size: 13px;

        .label {
          color: var(--color-text-secondary);
          min-width: 48px;
        }

        .value {
          color: var(--color-text-primary);
        }
      }
    }
  }
}

.empty-state {
  text-align: center;
  padding: 80px 20px;

  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  h3 {
    font-size: 20px;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 8px 0;
  }

  p {
    color: var(--color-text-secondary);
    font-size: 14px;
    margin: 0 0 24px 0;
  }

  .btn-primary {
    padding: 10px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;

    &:hover {
      opacity: 0.9;
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;

  .btn-page {
    padding: 8px 16px;
    background: var(--color-button-secondary-bg);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    color: var(--color-text-primary);
    transition: all 0.2s;

    &:hover:not(:disabled) {
      border-color: var(--color-primary);
      color: var(--color-primary);
      background: var(--color-primary-light);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .page-info {
    font-size: 14px;
    color: var(--color-text-secondary);
  }
}

.context-menu {
  position: fixed;
  background: var(--color-card-bg);
  border: 1px solid var(--color-card-border);
  border-radius: 6px;
  box-shadow: var(--color-card-shadow);
  padding: 4px 0;
  min-width: 120px;
  z-index: 1000;

  div {
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;
    color: var(--color-text-primary);

    &:hover {
      background: var(--color-bg-hover);
    }

    &.danger {
      color: var(--color-error);

      &:hover {
        background: var(--color-error-bg);
      }
    }
  }
}

.context-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

// 新建文档对话框
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dialog-card {
  background: var(--color-card-bg);
  border-radius: 12px;
  box-shadow: 0 8px 32px var(--color-shadow);
  width: 90%;
  max-width: 500px;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);

  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .btn-close {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;

    &:hover {
      background: var(--color-bg-hover);
      color: var(--color-text-primary);
    }
  }
}

.dialog-body {
  padding: 24px;

  .form-group {
    label {
      display: block;
      margin-bottom: 8px;
      font-size: 14px;
      font-weight: 500;
      color: var(--color-text-primary);
    }

    input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid var(--color-input-border);
      border-radius: 6px;
      font-size: 14px;
      background: var(--color-input-bg);
      color: var(--color-text-primary);
      box-sizing: border-box;

      &:focus {
        outline: none;
        border-color: var(--color-input-focus-border);
        box-shadow: 0 0 0 3px var(--color-input-focus-shadow);
      }

      &::placeholder {
        color: var(--color-text-tertiary);
      }
    }

    .input-hint {
      margin: 6px 0 0 0;
      font-size: 12px;
      color: var(--color-text-tertiary);
      text-align: right;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);

  button {
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: none;

    &.btn-secondary {
      background: var(--color-button-secondary-bg);
      color: var(--color-button-secondary-text);

      &:hover {
        background: var(--color-button-secondary-hover);
      }
    }

    &.btn-primary {
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
      color: white;

      &:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px var(--color-shadow);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}
</style>
