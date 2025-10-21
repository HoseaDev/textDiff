/**
 * 前端类型定义
 */

// ========== 文档类型 ==========

export interface Document {
  id: string
  title: string
  created_at: string
  updated_at: string
  current_version_number: number
}

export interface DocumentCreate {
  title: string
  initial_content?: string
  author?: string
}

export interface DocumentUpdate {
  title?: string
}

// ========== 版本类型 ==========

export interface Version {
  id: string
  document_id: string
  version_number: number
  content: string
  content_hash: string
  created_at: string
  author: string
  commit_message?: string
  save_type: 'manual' | 'auto' | 'draft'
  parent_version_id?: string
}

export interface VersionListItem {
  id: string
  version_number: number
  created_at: string
  author: string
  commit_message?: string
  save_type: string
  content_length: number
}

export interface VersionCreate {
  content: string
  commit_message?: string
  save_type?: 'manual' | 'auto' | 'draft'
  author?: string
}

// ========== 差异类型 ==========

export interface DiffChange {
  type: 'added' | 'deleted' | 'modified' | 'unchanged'
  old_text?: string
  new_text?: string
  old_line_start?: number
  old_line_end?: number
  new_line_start?: number
  new_line_end?: number
}

export interface DiffResponse {
  old_version_id: string
  new_version_id: string
  old_version_number: number
  new_version_number: number
  changes: DiffChange[]
  stats: {
    added: number
    deleted: number
    modified: number
    unchanged: number
  }
}

export interface DiffOptions {
  diff_mode?: 'character' | 'word' | 'line' | 'semantic'
  ignore_whitespace?: boolean
  ignore_case?: boolean
}

// ========== 版本标签类型 ==========

export interface VersionTag {
  id: string
  version_id: string
  tag_name: string
  description?: string
  created_at: string
}

export interface VersionTagCreate {
  tag_name: string
  description?: string
}

// ========== 保存状态类型 ==========

export interface SaveState {
  isDirty: boolean
  isSaving: boolean
  lastSaved: Date | null
  autoSaveEnabled: boolean
  autoSaveInterval: number // 毫秒
}

export interface SaveSettings {
  saveMode: 'manual' | 'auto' | 'hybrid'
  autoSaveInterval: number // 秒
  confirmBeforeSave: boolean
  warnBeforeLeave: boolean
}

// ========== WebSocket 消息类型 ==========

export interface WebSocketMessage {
  type: string
  [key: string]: any
}

export interface CursorPosition {
  line: number
  column: number
}

export interface UserInfo {
  username: string
  color?: string
}

// ========== API 响应类型 ==========

export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error?: {
    code: number
    message: string
    type: string
  }
}
