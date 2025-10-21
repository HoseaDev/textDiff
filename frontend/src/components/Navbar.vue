<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- Logo and Title -->
      <div class="navbar-brand">
        <router-link to="/" class="brand-link">
          <span class="brand-icon">📝</span>
          <span class="brand-text">TextDiff</span>
        </router-link>
      </div>

      <!-- Navigation Links -->
      <div class="navbar-nav">
        <router-link to="/documents" class="nav-link" active-class="active">
          <span class="nav-icon">📄</span>
          <span>我的文档</span>
        </router-link>
      </div>

      <!-- User Menu -->
      <div class="navbar-user">
        <div class="user-info" @click="toggleUserMenu">
          <div class="user-avatar">
            {{ userInitial }}
          </div>
          <span class="user-name">{{ currentUser?.username || '用户' }}</span>
          <span class="dropdown-icon">▼</span>
        </div>

        <!-- Dropdown Menu -->
        <div v-if="showUserMenu" class="user-dropdown">
          <div class="dropdown-header">
            <div class="user-avatar-large">{{ userInitial }}</div>
            <div class="user-details">
              <div class="user-name-large">{{ currentUser?.username }}</div>
              <div class="user-email">{{ currentUser?.email }}</div>
            </div>
          </div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-menu">
            <router-link to="/profile" class="dropdown-item" @click="closeUserMenu">
              <span class="item-icon">👤</span>
              <span>个人资料</span>
            </router-link>
            <router-link to="/settings" class="dropdown-item" @click="closeUserMenu">
              <span class="item-icon">⚙️</span>
              <span>设置</span>
            </router-link>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item danger" @click="handleLogout">
              <span class="item-icon">🚪</span>
              <span>退出登录</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Click outside to close menu -->
    <div
      v-if="showUserMenu"
      class="dropdown-overlay"
      @click="closeUserMenu"
    ></div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// State
const showUserMenu = ref(false)

// Computed
const currentUser = computed(() => authStore.user)
const userInitial = computed(() => {
  if (!currentUser.value?.username) return '?'
  return currentUser.value.username.charAt(0).toUpperCase()
})

// Methods
function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function closeUserMenu() {
  showUserMenu.value = false
}

async function handleLogout() {
  closeUserMenu()
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  border-bottom: 1px solid #e1e4e8;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-brand {
  .brand-link {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    font-size: 20px;
    font-weight: 700;
    color: #333;
    transition: opacity 0.2s;

    &:hover {
      opacity: 0.8;
    }

    .brand-icon {
      font-size: 24px;
    }

    .brand-text {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
}

.navbar-nav {
  display: flex;
  gap: 8px;
  flex: 1;
  margin-left: 40px;

  .nav-link {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 6px;
    text-decoration: none;
    color: #666;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s;

    .nav-icon {
      font-size: 16px;
    }

    &:hover {
      background: #f5f5f5;
      color: #333;
    }

    &.active {
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
      color: #667eea;
    }
  }
}

.navbar-user {
  position: relative;

  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
      background: #f5f5f5;
    }

    .user-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 14px;
    }

    .user-name {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .dropdown-icon {
      font-size: 10px;
      color: #666;
      transition: transform 0.2s;
    }
  }

  .user-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    width: 280px;
    background: white;
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    animation: slideDown 0.2s ease-out;

    .dropdown-header {
      padding: 16px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      gap: 12px;
      align-items: center;

      .user-avatar-large {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid white;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 20px;
      }

      .user-details {
        flex: 1;
        min-width: 0;

        .user-name-large {
          font-size: 16px;
          font-weight: 600;
          color: white;
          margin-bottom: 4px;
        }

        .user-email {
          font-size: 13px;
          color: rgba(255, 255, 255, 0.9);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }

    .dropdown-divider {
      height: 1px;
      background: #e1e4e8;
      margin: 0;
    }

    .dropdown-menu {
      padding: 8px 0;
    }

    .dropdown-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 16px;
      color: #333;
      font-size: 14px;
      text-decoration: none;
      cursor: pointer;
      transition: background 0.2s;

      .item-icon {
        font-size: 16px;
        width: 20px;
        text-align: center;
      }

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
}

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Responsive
@media (max-width: 768px) {
  .navbar-nav {
    margin-left: 20px;
  }

  .user-name {
    display: none;
  }

  .user-dropdown {
    width: 260px;
  }
}
</style>
