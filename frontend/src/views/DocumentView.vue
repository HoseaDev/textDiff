<template>
  <AppLayout>
    <!-- 侧边栏：版本列表 -->
    <template #sidebar>
      <VersionList
        :versions="documentStore.versions"
        :selected-version-id="documentStore.currentVersion?.id"
        :loading="loading"
        @select="handleVersionSelect"
        @filter-change="handleFilterChange"
      />
    </template>

    <!-- 主内容：编辑器或差异查看 -->
    <DiffViewer
      v-if="showDiff && diffData"
      :diff-data="diffData"
      :document-id="documentStore.currentDocument?.id"
      :old-version-id="currentOldVersionId"
      :new-version-id="currentNewVersionId"
      @close="showDiff = false"
      @refresh="handleDiffRefresh"
    />
    <DocumentEditor
      v-else
      v-model:content="documentStore.editorContent"
      @show-diff="handleShowDiff"
    />

    <!-- 设置 -->
    <template #settings>
      <SaveSettings />
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { diffApi } from '@/api/client'
import type { DiffResponse, VersionListItem } from '@/types'

import AppLayout from '@/components/AppLayout.vue'
import DocumentEditor from '@/components/DocumentEditor.vue'
import VersionList from '@/components/VersionList.vue'
import DiffViewer from '@/components/DiffViewer.vue'
import SaveSettings from '@/components/SaveSettings.vue'

const route = useRoute()
const router = useRouter()
const documentStore = useDocumentStore()

const loading = ref(false)
const showDiff = ref(false)
const diffData = ref<DiffResponse | null>(null)
const currentOldVersionId = ref<string>('')
const currentNewVersionId = ref<string>('')

onMounted(async () => {
  // 加载保存设置
  documentStore.loadSaveSettings()

  // 加载文档
  const documentId = route.params.id as string
  if (documentId) {
    loading.value = true
    try {
      await documentStore.loadDocument(documentId)
    } catch (error) {
      console.error('Failed to load document:', error)
      // 文档不存在，跳转回首页
      router.push('/')
    } finally {
      loading.value = false
    }
  }
})

async function handleVersionSelect(version: VersionListItem) {
  if (!documentStore.currentDocument) return

  try {
    await documentStore.loadVersion(documentStore.currentDocument.id, version.id)
    showDiff.value = false
  } catch (error) {
    console.error('Failed to load version:', error)
    alert('加载版本失败')
  }
}

async function handleFilterChange(saveType?: string) {
  if (!documentStore.currentDocument) return

  try {
    await documentStore.loadVersions(documentStore.currentDocument.id, saveType)
  } catch (error) {
    console.error('Failed to filter versions:', error)
  }
}

async function handleShowDiff() {
  if (!documentStore.currentDocument || !documentStore.currentVersion) return

  // 获取最新版本
  const latestVersion = documentStore.versions[0]
  if (!latestVersion) return

  currentOldVersionId.value = documentStore.currentVersion.id
  currentNewVersionId.value = latestVersion.id

  try {
    diffData.value = await diffApi.compareWithLatest(
      documentStore.currentDocument.id,
      documentStore.currentVersion.id,
      { diff_mode: 'word' }
    )
    showDiff.value = true
  } catch (error) {
    console.error('Failed to load diff:', error)
    alert('加载差异失败')
  }
}

async function handleDiffRefresh(options: { diffMode: string; ignoreCase: boolean; ignoreWhitespace: boolean }) {
  if (!documentStore.currentDocument || !currentOldVersionId.value || !currentNewVersionId.value) return

  try {
    diffData.value = await diffApi.compareWithLatest(
      documentStore.currentDocument.id,
      currentOldVersionId.value,
      {
        diff_mode: options.diffMode,
        ignore_case: options.ignoreCase,
        ignore_whitespace: options.ignoreWhitespace
      }
    )
  } catch (error) {
    console.error('Failed to refresh diff:', error)
    alert('刷新差异失败')
  }
}
</script>
