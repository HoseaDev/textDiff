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

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 文档列表 -->
    <div v-else-if="documents.length > 0" class="document-grid">
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
    <div v-else class="empty-state">
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { documentApi } from '@/api/client'
import type { Document } from '@/types'
import { formatDate as formatDateUtil } from '@/utils/date'

const router = useRouter()

// 状态
const documents = ref<Document[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const sortBy = ref('updated_at')
const currentPage = ref(1)
const pageSize = 20
const totalCount = ref(0)

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

// 创建新文档
async function createNewDocument() {
  try {
    const newDoc = await documentApi.create({
      title: '未命名文档',
      initial_content: ''
    })
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
  loadDocuments()
})
</script>

<style scoped lang="scss">
.document-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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
      color: #333;
    }

    .document-count {
      color: #666;
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
      border: 1px solid #e1e4e8;
      border-radius: 6px;
      font-size: 14px;
      box-sizing: border-box;

      &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
    }
  }

  .sort-box {
    display: flex;
    align-items: center;
    gap: 8px;

    label {
      font-size: 14px;
      color: #666;
    }

    select {
      padding: 8px 12px;
      border: 1px solid #e1e4e8;
      border-radius: 6px;
      font-size: 14px;
      cursor: pointer;

      &:focus {
        outline: none;
        border-color: #667eea;
      }
    }
  }
}

.loading {
  text-align: center;
  padding: 60px 20px;

  .spinner {
    width: 48px;
    height: 48px;
    margin: 0 auto 16px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  p {
    color: #666;
    font-size: 14px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.document-card {
  background: white;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
      color: #333;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .card-actions {
      .btn-icon {
        padding: 4px 8px;
        background: none;
        border: none;
        color: #666;
        font-size: 20px;
        cursor: pointer;
        border-radius: 4px;

        &:hover {
          background: #f5f5f5;
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
          color: #666;
          min-width: 48px;
        }

        .value {
          color: #333;
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
    color: #333;
    margin: 0 0 8px 0;
  }

  p {
    color: #666;
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
    background: white;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;

    &:hover:not(:disabled) {
      border-color: #667eea;
      color: #667eea;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .page-info {
    font-size: 14px;
    color: #666;
  }
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  min-width: 120px;
  z-index: 1000;

  div {
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;

    &:hover {
      background: #f5f5f5;
    }

    &.danger {
      color: #f44336;

      &:hover {
        background: #fee;
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
</style>
