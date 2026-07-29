import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      // 这里的逻辑：如果想去首页，直接重定向到发现广场
      redirect: '/discovery',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/user-workspace',
      name: 'workspace',
      component: () => import('../views/UserWorkspaceView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin-dashboard',
      name: 'admin-dashboard', // 修复：之前这里有重复定义，现在保留这一个
      component: () => import('../views/AdminDashboardView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/editor',
      name: 'editor-new',
      component: () => import('../views/EditorView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/editor/:id',
      name: 'editor',
      component: () => import('../views/EditorView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/discovery',
      name: 'discovery',
      component: () => import('../views/DiscoveryView.vue'),
    },
  ],
})

/**
 * 路由守卫：全职保安，负责拦截和分流
 */
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const isAuthenticated = !!userStore.token
  const userRole = userStore.role

  // 1. 如果用户已登录，还想去登录页 -> 按照角色自动分流
  if (to.path === '/login' && isAuthenticated) {
    if (userRole === 'admin') {
      next('/admin-dashboard')
    } else {
      next('/user-workspace')
    }
    return // 结束本次逻辑
  }

  // 2. 鉴权逻辑：去需要登录的页面但没登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    ElMessage.warning('请先登录接入系统哦~')
    next('/login')
  }
  // 3. 权限逻辑：去管理员页面但不是管理员
  else if (to.meta.requiresAdmin && userRole !== 'admin') {
    ElMessage.error('权限不足：非管理员禁止接入控制中心！')
    next('/user-workspace')
  }
  // 4. 正常放行
  else {
    next()
  }
})

export default router
