import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例，指向 Django 后端地址
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  timeout: 60000, // 因为 AI 生成比较慢，超时时间设长一点
})

// 请求拦截器：自动把 Token 塞进请求头
api.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

// 响应拦截器：处理后端报错（比如 Token 过期）
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      const isLoginRequest = error.config.url.includes('login/')
      // 登录失败不应该提示"登录已过期"
      if (!isLoginRequest) {
        ElMessage.error('登录已过期，请重新登录')
        const userStore = useUserStore()
        userStore.clearAuth()
        router.push('/login')
      }
    } else {
      ElMessage.error(error.response?.data?.error || error.response?.data?.detail || '网络请求失败')
    }
    return Promise.reject(error)
  },
)

export default api
