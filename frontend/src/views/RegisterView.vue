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
@import '@/assets/styles/variables.scss';

.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-primary);
  padding: 20px;
  position: relative;

  // 背景装饰
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    opacity: 0.1;
    z-index: 0;
  }
}

.register-card {
  width: 100%;
  max-width: 480px;
  background: var(--color-card-bg);
  border: 1px solid var(--color-card-border);
  border-radius: $border-radius-lg;
  box-shadow: var(--color-card-shadow);
  padding: 40px;
  animation: slideUp 0.4s ease-out;
  position: relative;
  z-index: 1;

  @include mobile {
    padding: 30px 20px;
  }
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
    font-size: $font-size-xl;
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 0 0 8px 0;
  }

  p {
    color: var(--color-text-secondary);
    font-size: $font-size-sm;
    margin: 0;
  }
}

.register-form {
  .form-group {
    margin-bottom: 20px;

    label {
      display: block;
      margin-bottom: 8px;
      font-size: $font-size-sm;
      font-weight: 500;
      color: var(--color-text-primary);
    }

    input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid var(--color-input-border);
      border-radius: $border-radius-md;
      font-size: $font-size-sm;
      background: var(--color-input-bg);
      color: var(--color-text-primary);
      transition: all $transition-fast;
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

    .password-strength {
      margin-top: 8px;
      height: 4px;
      background: var(--color-bg-tertiary);
      border-radius: 2px;
      overflow: hidden;

      .strength-bar {
        height: 100%;
        transition: all $transition-base;

        &.weak {
          background: var(--color-error);
        }

        &.medium {
          background: var(--color-warning);
        }

        &.strong {
          background: var(--color-success);
        }
      }
    }

    .password-hint {
      margin: 4px 0 0 0;
      font-size: $font-size-xs;
      color: var(--color-text-secondary);
    }

    .error-hint {
      margin: 4px 0 0 0;
      font-size: $font-size-xs;
      color: var(--color-error);
    }

    .success-hint {
      margin: 4px 0 0 0;
      font-size: $font-size-xs;
      color: var(--color-success);
    }

    .verification-input-group {
      display: flex;
      gap: 8px;

      input {
        flex: 1;
      }

      .btn-send-code {
        padding: 12px 20px;
        background: var(--color-primary);
        color: white;
        border: none;
        border-radius: $border-radius-md;
        font-size: $font-size-sm;
        font-weight: 500;
        cursor: pointer;
        transition: all $transition-fast;
        white-space: nowrap;

        &:hover:not(:disabled) {
          background: var(--color-primary-hover);
        }

        &:disabled {
          background: var(--color-bg-tertiary);
          color: var(--color-text-disabled);
          cursor: not-allowed;
          opacity: 0.6;
        }
      }
    }
  }

  .error-message {
    margin-bottom: 16px;
    padding: 12px;
    background: var(--color-error-bg);
    border: 1px solid var(--color-error-border);
    border-radius: $border-radius-md;
    color: var(--color-error);
    font-size: $font-size-sm;
    text-align: center;
  }

  .btn-register {
    width: 100%;
    padding: 12px;
    background: var(--color-primary);
    color: white;
    border: none;
    border-radius: $border-radius-md;
    font-size: $font-size-base;
    font-weight: 600;
    cursor: pointer;
    transition: all $transition-base;

    &:hover:not(:disabled) {
      background: var(--color-primary-hover);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px var(--color-shadow);
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
    font-size: $font-size-sm;
    color: var(--color-text-secondary);
    margin: 0;

    a {
      color: var(--color-primary);
      text-decoration: none;
      font-weight: 600;

      &:hover {
        text-decoration: underline;
        color: var(--color-primary-hover);
      }
    }
  }
}
</style>
