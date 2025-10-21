/**
 * 文档状态管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Document,
  Version,
  VersionListItem,
  SaveState,
  SaveSettings,
} from '@/types'
import { documentApi, versionApi } from '@/api/client'

export const useDocumentStore = defineStore('document', () => {
  // ========== State ==========
  const currentDocument = ref<Document | null>(null)
  const currentVersion = ref<Version | null>(null)
  const versions = ref<VersionListItem[]>([])
  const editorContent = ref('')
  const originalContent = ref('') // 用于判断是否有更改

  // 保存状态
  const saveState = ref<SaveState>({
    isDirty: false,
    isSaving: false,
    lastSaved: null,
    autoSaveEnabled: true,
    autoSaveInterval: 30000, // 30秒
  })

  // 保存设置
  const saveSettings = ref<SaveSettings>({
    saveMode: 'hybrid', // manual, auto, hybrid
    autoSaveInterval: 30, // 秒
    confirmBeforeSave: false,
    warnBeforeLeave: true,
  })

  // ========== Computed ==========
  const hasUnsavedChanges = computed(() => {
    return editorContent.value !== originalContent.value
  })

  const isAutoSaveEnabled = computed(() => {
    return (
      saveSettings.value.saveMode !== 'manual' && saveState.value.autoSaveEnabled
    )
  })

  // ========== Actions ==========

  /**
   * 加载文档
   */
  async function loadDocument(documentId: string) {
    try {
      currentDocument.value = await documentApi.get(documentId)
      await loadVersions(documentId)
      // 加载最新版本内容
      if (versions.value.length > 0) {
        await loadVersion(documentId, versions.value[0].id)
      }
    } catch (error) {
      console.error('Failed to load document:', error)
      throw error
    }
  }

  /**
   * 加载版本列表
   */
  async function loadVersions(documentId: string, saveType?: string) {
    try {
      versions.value = await versionApi.list(documentId, {
        limit: 100,
        save_type: saveType,
      })
    } catch (error) {
      console.error('Failed to load versions:', error)
      throw error
    }
  }

  /**
   * 加载指定版本
   */
  async function loadVersion(documentId: string, versionId: string) {
    try {
      currentVersion.value = await versionApi.get(documentId, versionId)
      editorContent.value = currentVersion.value.content
      originalContent.value = currentVersion.value.content
      saveState.value.isDirty = false
    } catch (error) {
      console.error('Failed to load version:', error)
      throw error
    }
  }

  /**
   * 保存新版本
   */
  async function saveVersion(
    commitMessage?: string,
    saveType: 'manual' | 'auto' = 'manual'
  ) {
    if (!currentDocument.value) {
      throw new Error('No document loaded')
    }

    // 如果内容未变化，不保存
    if (!hasUnsavedChanges.value) {
      console.log('No changes to save')
      return currentVersion.value
    }

    saveState.value.isSaving = true

    try {
      const newVersion = await versionApi.create(currentDocument.value.id, {
        content: editorContent.value,
        commit_message: commitMessage || `${saveType === 'auto' ? 'Auto-saved' : 'Saved'} version`,
        save_type: saveType,
        author: 'current-user', // TODO: 从用户系统获取
      })

      currentVersion.value = newVersion
      originalContent.value = editorContent.value
      saveState.value.isDirty = false
      saveState.value.lastSaved = new Date()

      // 重新加载版本列表
      await loadVersions(currentDocument.value.id)

      return newVersion
    } catch (error) {
      console.error('Failed to save version:', error)
      throw error
    } finally {
      saveState.value.isSaving = false
    }
  }

  /**
   * 恢复到指定版本
   */
  async function restoreVersion(versionId: string) {
    if (!currentDocument.value) {
      throw new Error('No document loaded')
    }

    try {
      const newVersion = await versionApi.restore(currentDocument.value.id, versionId)
      currentVersion.value = newVersion
      editorContent.value = newVersion.content
      originalContent.value = newVersion.content
      saveState.value.isDirty = false

      // 重新加载版本列表
      await loadVersions(currentDocument.value.id)

      return newVersion
    } catch (error) {
      console.error('Failed to restore version:', error)
      throw error
    }
  }

  /**
   * 更新编辑器内容
   */
  function updateContent(content: string) {
    editorContent.value = content
    saveState.value.isDirty = content !== originalContent.value
  }

  /**
   * 更新保存设置
   */
  function updateSaveSettings(settings: Partial<SaveSettings>) {
    saveSettings.value = { ...saveSettings.value, ...settings }
    // 更新自动保存间隔
    if (settings.autoSaveInterval) {
      saveState.value.autoSaveInterval = settings.autoSaveInterval * 1000
    }
    // 保存到 localStorage
    localStorage.setItem('saveSettings', JSON.stringify(saveSettings.value))
  }

  /**
   * 从 localStorage 加载保存设置
   */
  function loadSaveSettings() {
    const saved = localStorage.getItem('saveSettings')
    if (saved) {
      try {
        const settings = JSON.parse(saved)
        saveSettings.value = settings
        saveState.value.autoSaveInterval = settings.autoSaveInterval * 1000
      } catch (error) {
        console.error('Failed to load save settings:', error)
      }
    }
  }

  /**
   * 重置状态
   */
  function reset() {
    currentDocument.value = null
    currentVersion.value = null
    versions.value = []
    editorContent.value = ''
    originalContent.value = ''
    saveState.value.isDirty = false
    saveState.value.isSaving = false
  }

  return {
    // State
    currentDocument,
    currentVersion,
    versions,
    editorContent,
    saveState,
    saveSettings,

    // Computed
    hasUnsavedChanges,
    isAutoSaveEnabled,

    // Actions
    loadDocument,
    loadVersions,
    loadVersion,
    saveVersion,
    restoreVersion,
    updateContent,
    updateSaveSettings,
    loadSaveSettings,
    reset,
  }
})
