<template>
  <div class="login-container">
    <div class="heart-container" ref="heartContainer"></div>

    <div class="glass-card">
      <h2 class="title">✨ 智能创作平台 ✨</h2>
      <p class="subtitle">AI Powered, Made with ❤️</p>

      <el-form :model="form" label-width="0">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="请输入尊贵的账号"
            size="large"
            class="glass-input"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            @keyup.enter="handleLogin"
            show-password
            class="glass-input"
          />
        </el-form-item>
        <el-button class="glow-btn" :loading="loading" @click="handleLogin" size="large">
          开启创作之旅 🚀
        </el-button>

        <div class="reg-link-wrapper">
          <el-button link class="reg-link" @click="router.push('/register')">
            没有账号？点击注册新身份 ✨
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import api from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const heartContainer = ref(null)
let heartInterval = null

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    return ElMessage.warning({ message: '请输入账号和密码呀~', grouping: true })
  }
  loading.value = true
  try {
    const res = await api.post('login/', form.value)
    userStore.setAuth(res.access, res.role, res.username)
    ElMessage.success({ message: `欢迎回来，${res.username}！`, grouping: true })
    if (res.role === 'admin') router.push('/admin-dashboard')
    else router.push('/user-workspace')
  } catch (err) {
    // 登录失败提示具体原因
    const msg = err.response?.data?.detail || '账号或密码错误，请重试'
    ElMessage.error({ message: msg, grouping: true })
  } finally {
    loading.value = false
  }
}

const createHeart = () => {
  if (!heartContainer.value) return
  const heart = document.createElement('div')
  heart.classList.add('heart')
  heart.innerHTML = '❤️'
  heart.style.left = Math.random() * 100 + 'vw'
  heart.style.fontSize = Math.random() * 20 + 10 + 'px'
  heart.style.animationDuration = Math.random() * 3 + 2 + 's'
  heartContainer.value.appendChild(heart)
  setTimeout(() => {
    if (heart && heart.parentNode) heart.remove()
  }, 5000)
}

onMounted(() => {
  heartInterval = setInterval(createHeart, 300)
})
onBeforeUnmount(() => {
  if (heartInterval) clearInterval(heartInterval)
})
</script>

<style>
/* 继承之前的样式 ... */
body {
  margin: 0;
  overflow: hidden;
}
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab, #ffb6ff, #a0ff9d);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
  position: relative;
}
@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
.heart-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}
.heart {
  position: absolute;
  top: -5vh;
  transform: translateY(0);
  animation: fall linear forwards;
  opacity: 0.7;
}
@keyframes fall {
  to {
    transform: translateY(105vh);
    opacity: 0;
  }
}

.glass-card {
  width: 420px;
  padding: 50px 40px;
  z-index: 2;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  text-align: center;
}
.title {
  color: #fff;
  font-size: 28px;
  margin-bottom: 5px;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
}
.subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin-bottom: 30px;
  letter-spacing: 2px;
}
.glass-input .el-input__wrapper {
  background: rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
}
.glass-input .el-input__inner {
  color: #fff !important;
}
.glow-btn {
  width: 100%;
  margin-top: 20px;
  background: linear-gradient(90deg, #ff8a00, #e52e71);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: bold;
}

/* 新增：链接样式 */
.reg-link-wrapper {
  margin-top: 20px;
}
.reg-link {
  color: rgba(255, 255, 255, 0.8) !important;
  font-size: 13px !important;
}
.reg-link:hover {
  color: #fff !important;
  text-decoration: underline;
}
</style>
