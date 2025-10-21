/**
 * 用户认证 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// 类型定义
export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  is_superuser: boolean
  timezone: string
  created_at: string
  updated_at: string
  last_login_at?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  verification_code: string
  full_name?: string
  timezone?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_superuser ?? false)

  // API 基础 URL
  const API_BASE_URL = '/api'

  /**
   * 用户注册
   */
  async function register(data: RegisterRequest): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post<TokenResponse>(
        `${API_BASE_URL}/auth/register`,
        data
      )

      // 保存认证信息
      saveAuthData(response.data)

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '注册失败,请重试'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户登录
   */
  async function login(credentials: LoginRequest): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post<TokenResponse>(
        `${API_BASE_URL}/auth/login`,
        credentials
      )

      // 保存认证信息
      saveAuthData(response.data)

      return true
    } catch (err: any) {
      if (err.response?.status === 401) {
        error.value = '用户名或密码错误'
      } else {
        error.value = err.response?.data?.detail || '登录失败,请重试'
      }
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户登出
   */
  async function logout(): Promise<void> {
    try {
      // 调用登出 API
      if (accessToken.value) {
        await axios.post(
          `${API_BASE_URL}/auth/logout`,
          {},
          {
            headers: {
              Authorization: `Bearer ${accessToken.value}`
            }
          }
        )
      }
    } catch (err) {
      console.error('Logout API error:', err)
    } finally {
      // 无论 API 是否成功,都清除本地数据
      clearAuthData()
    }
  }

  /**
   * 刷新访问令牌
   */
  async function refreshAccessToken(): Promise<boolean> {
    if (!refreshToken.value) {
      return false
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/refresh`,
        {
          refresh_token: refreshToken.value
        }
      )

      // 更新访问令牌
      accessToken.value = response.data.access_token
      localStorage.setItem('access_token', response.data.access_token)

      // 更新 axios 默认 header
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`

      return true
    } catch (err) {
      console.error('Token refresh failed:', err)
      // 刷新失败,清除认证信息
      clearAuthData()
      return false
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser(): Promise<boolean> {
    if (!accessToken.value) {
      return false
    }

    try {
      const response = await axios.get<User>(
        `${API_BASE_URL}/auth/me`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`
          }
        }
      )

      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))

      return true
    } catch (err: any) {
      console.error('Fetch user failed:', err)

      // 如果是 401 错误,尝试刷新令牌
      if (err.response?.status === 401) {
        const refreshed = await refreshAccessToken()
        if (refreshed) {
          // 刷新成功,重试获取用户信息
          return fetchCurrentUser()
        }
      }

      return false
    }
  }

  /**
   * 从本地存储恢复会话
   */
  async function restoreSession(): Promise<boolean> {
    const savedAccessToken = localStorage.getItem('access_token')
    const savedRefreshToken = localStorage.getItem('refresh_token')
    const savedUser = localStorage.getItem('user')

    if (!savedAccessToken || !savedUser) {
      return false
    }

    try {
      // 恢复认证信息
      accessToken.value = savedAccessToken
      refreshToken.value = savedRefreshToken
      user.value = JSON.parse(savedUser)

      // 设置 axios 默认 header
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedAccessToken}`

      // 验证令牌是否有效
      const valid = await fetchCurrentUser()

      if (!valid) {
        // 令牌无效,清除数据
        clearAuthData()
        return false
      }

      return true
    } catch (err) {
      console.error('Restore session failed:', err)
      clearAuthData()
      return false
    }
  }

  /**
   * 更新用户信息
   */
  async function updateProfile(data: Partial<User>): Promise<boolean> {
    if (!accessToken.value) {
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await axios.put<User>(
        `${API_BASE_URL}/auth/me`,
        data,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`
          }
        }
      )

      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新失败,请重试'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 修改密码
   */
  async function updatePassword(oldPassword: string, newPassword: string): Promise<boolean> {
    if (!accessToken.value) {
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      await axios.post(
        `${API_BASE_URL}/auth/me/password`,
        {
          old_password: oldPassword,
          new_password: newPassword
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`
          }
        }
      )

      // 修改密码成功,需要重新登录
      clearAuthData()

      return true
    } catch (err: any) {
      if (err.response?.status === 400) {
        error.value = '旧密码不正确'
      } else {
        error.value = err.response?.data?.detail || '修改密码失败'
      }
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 保存认证数据到状态和本地存储
   */
  function saveAuthData(data: TokenResponse): void {
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    user.value = data.user

    // 保存到 localStorage
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    // 设置 axios 默认 header
    axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
  }

  /**
   * 清除认证数据
   */
  function clearAuthData(): void {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    error.value = null

    // 清除 localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')

    // 清除 axios 默认 header
    delete axios.defaults.headers.common['Authorization']
  }

  /**
   * 清除错误信息
   */
  function clearError(): void {
    error.value = null
  }

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,

    // 计算属性
    isAuthenticated,
    isAdmin,

    // 方法
    register,
    login,
    logout,
    refreshAccessToken,
    fetchCurrentUser,
    restoreSession,
    updateProfile,
    updatePassword,
    clearError
  }
})
