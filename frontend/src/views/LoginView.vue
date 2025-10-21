<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>TextDiff</h1>
        <p>文本版本管理系统</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名或邮箱</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="请输入用户名或邮箱"
            required
            autofocus
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <div class="form-options">
          <label class="checkbox-label">
            <input v-model="rememberMe" type="checkbox" />
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-password">忘记密码?</a>
        </div>

        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <button
          type="submit"
          class="btn-login"
          :disabled="authStore.isLoading"
        >
          <span v-if="!authStore.isLoading">登录</span>
          <span v-else>登录中...</span>
        </button>
      </form>

      <div class="login-footer">
        <p>
          还没有账号?
          <router-link to="/register">立即注册</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  password: ''
})

const rememberMe = ref(false)

// 检查是否已登录
onMounted(async () => {
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})

async function handleLogin() {
  authStore.clearError()

  const success = await authStore.login(formData.value)

  if (success) {
    // 登录成功,跳转到首页或之前的页面
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/')
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
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

.login-header {
  text-align: center;
  margin-bottom: 32px;

  h1 {
    font-size: 32px;
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

.login-form {
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
  }

  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    .checkbox-label {
      display: flex;
      align-items: center;
      cursor: pointer;
      font-size: 14px;
      color: #666;

      input[type='checkbox'] {
        margin-right: 8px;
        width: auto;
      }
    }

    .forgot-password {
      font-size: 14px;
      color: #667eea;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
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

  .btn-login {
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

.login-footer {
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
