/**
 * API 客户端
 * 封装所有后端 API 调用
 */
import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  Version,
  VersionListItem,
  VersionCreate,
  DiffResponse,
  DiffOptions,
  VersionTag,
  VersionTagCreate,
} from '@/types'

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 access token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理 401 自动刷新 Token
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError) => {
    const originalRequest: any = error.config

    // 如果是 401 错误且未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // 获取 refresh token
        const refreshToken = localStorage.getItem('refresh_token')

        if (!refreshToken) {
          // 没有 refresh token,跳转到登录页
          window.location.href = '/login'
          return Promise.reject(error)
        }

        // 调用刷新 token API
        const response = await axios.post('/api/auth/refresh', {
          refresh_token: refreshToken
        })

        const { access_token } = response.data

        // 保存新的 access token
        localStorage.setItem('access_token', access_token)

        // 更新原始请求的 Authorization header
        originalRequest.headers.Authorization = `Bearer ${access_token}`

        // 重试原始请求
        return api(originalRequest)
      } catch (refreshError) {
        // 刷新失败,清除所有认证信息并跳转到登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // 统一错误处理
    const errorMessage = error.response?.data || error.message
    console.error('API Error:', errorMessage)
    return Promise.reject(errorMessage)
  }
)

// ========== 文档相关 API ==========

export const documentApi = {
  /**
   * 创建文档
   */
  create: (data: DocumentCreate): Promise<Document> => {
    return api.post('/documents', data)
  },

  /**
   * 获取文档列表
   */
  list: (params?: {
    skip?: number
    limit?: number
    sort_by?: string
  }): Promise<Document[]> => {
    return api.get('/documents', { params })
  },

  /**
   * 获取文档详情
   */
  get: (id: string): Promise<Document> => {
    return api.get(`/documents/${id}`)
  },

  /**
   * 更新文档
   */
  update: (id: string, data: DocumentUpdate): Promise<Document> => {
    return api.put(`/documents/${id}`, data)
  },

  /**
   * 删除文档
   */
  delete: (id: string): Promise<any> => {
    return api.delete(`/documents/${id}`)
  },
}

// ========== 版本相关 API ==========

export const versionApi = {
  /**
   * 创建新版本
   */
  create: (documentId: string, data: VersionCreate): Promise<Version> => {
    return api.post(`/documents/${documentId}/versions`, data)
  },

  /**
   * 获取版本列表
   */
  list: (
    documentId: string,
    params?: {
      skip?: number
      limit?: number
      save_type?: string
    }
  ): Promise<VersionListItem[]> => {
    return api.get(`/documents/${documentId}/versions`, { params })
  },

  /**
   * 获取版本详情
   */
  get: (documentId: string, versionId: string): Promise<Version> => {
    return api.get(`/documents/${documentId}/versions/${versionId}`)
  },

  /**
   * 根据版本号获取版本
   */
  getByNumber: (documentId: string, versionNumber: number): Promise<Version> => {
    return api.get(`/documents/${documentId}/versions/number/${versionNumber}`)
  },

  /**
   * 恢复到指定版本
   */
  restore: (documentId: string, versionId: string): Promise<Version> => {
    return api.post(`/documents/${documentId}/restore/${versionId}`)
  },
}

// ========== 差异比较 API ==========

export const diffApi = {
  /**
   * 比较两个版本（通过 ID）
   */
  compareById: (
    version1Id: string,
    version2Id: string,
    options?: DiffOptions
  ): Promise<DiffResponse> => {
    return api.get(`/diff/${version1Id}/${version2Id}`, {
      params: options,
    })
  },

  /**
   * 比较两个版本（通过版本号）
   */
  compareByNumber: (
    documentId: string,
    versionNum1: number,
    versionNum2: number,
    options?: DiffOptions
  ): Promise<DiffResponse> => {
    return api.get(`/diff/document/${documentId}/number/${versionNum1}/${versionNum2}`, {
      params: options,
    })
  },

  /**
   * 与最新版本比较
   */
  compareWithLatest: (
    documentId: string,
    versionId: string,
    options?: DiffOptions
  ): Promise<DiffResponse> => {
    return api.get(`/diff/document/${documentId}/latest/${versionId}`, {
      params: options,
    })
  },
}

// ========== 验证码 API ==========

export const verificationApi = {
  /**
   * 发送验证码
   */
  send: (email: string, purpose: string = 'register'): Promise<{
    success: boolean
    message: string
    code_id?: string
  }> => {
    return api.post('/verification/send', { email, purpose })
  },

  /**
   * 验证验证码
   */
  verify: (email: string, code: string, purpose: string = 'register'): Promise<{
    success: boolean
    message: string
  }> => {
    return api.post('/verification/verify', { email, code, purpose })
  },
}

// ========== 版本标签 API ==========

export const tagApi = {
  /**
   * 创建版本标签
   */
  create: (
    documentId: string,
    versionId: string,
    data: VersionTagCreate
  ): Promise<VersionTag> => {
    return api.post(`/documents/${documentId}/versions/${versionId}/tags`, data)
  },

  /**
   * 获取版本标签列表
   */
  list: (documentId: string, versionId: string): Promise<VersionTag[]> => {
    return api.get(`/documents/${documentId}/versions/${versionId}/tags`)
  },

  /**
   * 删除版本标签
   */
  delete: (tagId: string): Promise<any> => {
    return api.delete(`/documents/tags/${tagId}`)
  },
}

export default api
