import { createRouter, createWebHistory } from 'vue-router'

// 引入各个页面组件
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Camera from '../views/Camera.vue'
import AdminDashboard from '../views/AdminDashboard.vue' // <-- 1. 引入我们刚写的管理员面板
import FaceRegister from '../views/FaceRegister.vue' // 1. 引入组件
import Leave from '../views/Leave.vue' // <-- 1. 引入请假页面组件
import TeacherStats from '../views/TeacherStats.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard },
  { path: '/camera', component: Camera },
  { path: '/admin', component: AdminDashboard }, // <-- 2. 配置管理员页面的路由路径
  { path: '/register', component: FaceRegister }, // 2. 注册路由
  { path: '/leave', component: Leave }, // <-- 2. 配置路由路径
  { path: '/teacher-stats', component: TeacherStats } // <-- 3. 配置教师统计页面的路由路径
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router