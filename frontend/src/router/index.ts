import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DocumentListView from '@/views/DocumentListView.vue'
import DocumentView from '@/views/DocumentView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import SettingsView from '@/views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: DocumentListView,
      meta: { requiresAuth: true }
    },
    {
      path: '/documents',
      name: 'documents',
      component: DocumentListView,
      meta: { requiresAuth: true }
    },
    {
      path: '/document/:id',
      name: 'document',
      component: DocumentView,
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth) {
    // 需要认证的路由
    if (!authStore.isAuthenticated) {
      // 尝试从本地存储恢复会话
      const restored = await authStore.restoreSession()

      if (!restored) {
        // 未登录,跳转到登录页,并保存原始访问路径
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
  } else {
    // 不需要认证的路由(登录/注册页)
    if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      // 已登录用户访问登录/注册页,跳转到首页
      next({ path: '/' })
      return
    }
  }

  next()
})

export default router
