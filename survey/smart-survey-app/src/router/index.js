// 文件路径: src/router/index.js
import { createRouter, createWebHashHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/teacher' },
  { 
    path: '/teacher', 
    name: 'Teacher', 
    component: () => import('../views/Teacher/Dashboard.vue') 
  },
  { 
    path: '/setting', 
    name: 'Setting', 
    component: () => import('../views/Setting.vue') 
  },
  { 
    path: '/student', 
    name: 'Student', 
    component: () => import('../views/Student/Survey.vue') 
  },
  { 
    path: '/report', 
    name: 'Report', 
    component: () => import('../views/Teacher/Report.vue') 
  }
];

const router = createRouter({
  history: createWebHashHistory(), // 移动端本地打包必须用 Hash 模式
  routes
});

export default router;