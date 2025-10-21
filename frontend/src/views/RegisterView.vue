<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1>注册 TextDiff</h1>
        <p>创建账号开始管理您的文本版本</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名 *</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="3-50个字符"
            required
            minlength="3"
            maxlength="50"
            autofocus
          />
        </div>

        <div class="form-group">
          <label for="email">邮箱 *</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="your@email.com"
            required
            @blur="validateEmail"
          />
        </div>

        <div class="form-group">
          <label for="verification-code">邮箱验证码 *</label>
          <div class="verification-input-group">
            <input
              id="verification-code"
              v-model="formData.verification_code"
              type="text"
              placeholder="请输入6位验证码"
              required
              maxlength="6"
              pattern="\d{6}"
            />
            <button
              type="button"
              class="btn-send-code"
              :disabled="!canSendCode || countdown > 0"
              @click="sendVerificationCode"
            >
              {{ codeButtonText }}
            </button>
          </div>
          <p v-if="codeSentMessage" class="success-hint">{{ codeSentMessage }}</p>
          <p v-if="codeErrorMessage" class="error-hint">{{ codeErrorMessage }}</p>
        </div>

        <div class="form-group">
          <label for="password">密码 *</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="至少6个字符"
            required
            minlength="6"
          />
          <div class="password-strength">
            <div
              class="strength-bar"
              :class="passwordStrength.class"
              :style="{ width: passwordStrength.width }"
            ></div>
          </div>
          <p class="password-hint">{{ passwordStrength.text }}</p>
        </div>

        <div class="form-group">
          <label for="confirm-password">确认密码 *</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            placeholder="再次输入密码"
            required
          />
          <p v-if="confirmPassword && !passwordsMatch" class="error-hint">
            两次密码不一致
          </p>
        </div>

        <div class="form-group">
          <label for="full-name">全名 (可选)</label>
          <input
            id="full-name"
            v-model="formData.full_name"
            type="text"
            placeholder="您的全名"
            maxlength="100"
          />
        </div>

        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <button
          type="submit"
          class="btn-register"
          :disabled="!canSubmit || authStore.isLoading"
        >
          <span v-if="!authStore.isLoading">注册</span>
          <span v-else>注册中...</span>
        </button>
      </form>

      <div class="register-footer">
        <p>
          已有账号?
          <router-link to="/login">立即登录</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { verificationApi } from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  verification_code: '',
  timezone: 'Asia/Shanghai'
})

const confirmPassword = ref('')

// 验证码相关
const countdown = ref(0)
const codeSentMessage = ref('')
const codeErrorMessage = ref('')
const emailValid = ref(false)
let countdownTimer: number | null = null

// 密码是否匹配
const passwordsMatch = computed(() => {
  return formData.value.password === confirmPassword.value
})

// 密码强度
const passwordStrength = computed(() => {
  const password = formData.value.password
  if (!password) {
    return { width: '0%', class: '', text: '' }
  }

  let strength = 0
  if (password.length >= 6) strength++
  if (password.length >= 10) strength++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++

  if (strength <= 1) {
    return { width: '25%', class: 'weak', text: '弱' }
  } else if (strength <= 3) {
    return { width: '50%', class: 'medium', text: '中等' }
  } else {
    return { width: '100%', class: 'strong', text: '强' }
  }
})

// 验证邮箱格式
function validateEmail() {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  emailValid.value = emailRegex.test(formData.value.email)
}

// 是否可以发送验证码
const canSendCode = computed(() => {
  return emailValid.value && formData.value.email.length > 0
})

// 验证码按钮文字
const codeButtonText = computed(() => {
  if (countdown.value > 0) {
    return `${countdown.value}秒后重试`
  }
  return '获取验证码'
})

// 发送验证码
async function sendVerificationCode() {
  if (!canSendCode.value || countdown.value > 0) {
    return
  }

  codeSentMessage.value = ''
  codeErrorMessage.value = ''

  try {
    const response = await verificationApi.send(formData.value.email, 'register')

    if (response.success) {
      codeSentMessage.value = response.message
      // 开始60秒倒计时
      startCountdown(60)
    }
  } catch (error: any) {
    codeErrorMessage.value = error.detail || '发送失败,请稍后重试'
  }
}

// 开始倒计时
function startCountdown(seconds: number) {
  countdown.value = seconds

  countdownTimer = window.setInterval(() => {
    countdown.value--

    if (countdown.value <= 0) {
      stopCountdown()
    }
  }, 1000)
}

// 停止倒计时
function stopCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
}

// 组件卸载时清理定时器
onUnmounted(() => {
  stopCountdown()
})

// 是否可以提交
const canSubmit = computed(() => {
  return (
    formData.value.username.length >= 3 &&
    formData.value.email &&
    formData.value.verification_code.length === 6 &&
    formData.value.password.length >= 6 &&
    passwordsMatch.value
  )
})

async function handleRegister() {
  if (!canSubmit.value) {
    return
  }

  authStore.clearError()

  const success = await authStore.register(formData.value)

  if (success) {
    // 注册成功,跳转到首页
    router.push('/')
  }
}
</script>

<style scoped lang="scss">
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  animation: slideUp 0.4s ease-out;
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

.register-header {
  text-align: center;
  margin-bottom: 32px;

  h1 {
    font-size: 28px;
    font-weight: 700;
    color: #333;
    margin: 0 0 8px 0;
  }

  p {
    color: #666;
    font-size: 14px;
    margin: 0;
  }
}

.register-form {
  .form-group {
    margin-bottom: 20px;

    label {
      display: block;
      margin-bottom: 8px;
      font-size: 14px;
      font-weight: 500;
      color: #333;
    }

    input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid #e1e4e8;
      border-radius: 6px;
      font-size: 14px;
      transition: all 0.2s;
      box-sizing: border-box;

      &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }

      &::placeholder {
        color: #999;
      }
    }

    .password-strength {
      margin-top: 8px;
      height: 4px;
      background: #e1e4e8;
      border-radius: 2px;
      overflow: hidden;

      .strength-bar {
        height: 100%;
        transition: all 0.3s;

        &.weak {
          background: #f44336;
        }

        &.medium {
          background: #ff9800;
        }

        &.strong {
          background: #4caf50;
        }
      }
    }

    .password-hint {
      margin: 4px 0 0 0;
      font-size: 12px;
      color: #666;
    }

    .error-hint {
      margin: 4px 0 0 0;
      font-size: 12px;
      color: #f44336;
    }

    .success-hint {
      margin: 4px 0 0 0;
      font-size: 12px;
      color: #4caf50;
    }

    .verification-input-group {
      display: flex;
      gap: 8px;

      input {
        flex: 1;
      }

      .btn-send-code {
        padding: 12px 20px;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        white-space: nowrap;

        &:hover:not(:disabled) {
          background: #5568d3;
        }

        &:disabled {
          background: #ccc;
          cursor: not-allowed;
          opacity: 0.6;
        }
      }
    }
  }

  .error-message {
    margin-bottom: 16px;
    padding: 12px;
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 6px;
    color: #c33;
    font-size: 14px;
    text-align: center;
  }

  .btn-register {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;

    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.register-footer {
  margin-top: 24px;
  text-align: center;

  p {
    font-size: 14px;
    color: #666;
    margin: 0;

    a {
      color: #667eea;
      text-decoration: none;
      font-weight: 600;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style>
