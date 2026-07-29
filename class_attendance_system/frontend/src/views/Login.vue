<template>
  <div class="login-container">
    <div class="tech-bg"></div>
    <div class="scan-line"></div>

    <div class="login-box">
      <div class="corner top-left"></div>
      <div class="corner top-right"></div>
      <div class="corner bottom-left"></div>
      <div class="corner bottom-right"></div>

      <h2 class="sys-title">
        <span class="icon">✜</span> 班级人脸考勤系统 <span class="icon">✜</span>
      </h2>
      <p class="subtitle">FACIAL RECOGNITION ATTENDANCE SYSTEM</p>

      <div class="form-group">
        <label>USER_ID // 用户名</label>
        <div class="input-wrapper">
          <input v-model="username" type="text" placeholder="请输入学号或工号..." />
          <span class="focus-border"></span>
        </div>
      </div>

      <div class="form-group">
        <label>PASSWORD // 密钥</label>
        <div class="input-wrapper">
          <input v-model="password" type="password" placeholder="请输入系统密钥..." @keyup.enter="handleLogin" />
          <span class="focus-border"></span>
        </div>
      </div>

      <button class="cyber-btn" @click="handleLogin" :disabled="loading">
        <span class="btn-text">{{ loading ? 'SYSTEM AUTHENTICATING...' : 'INITIALIZE LOGIN' }}</span>
        <span class="btn-glitch"></span>
      </button>

      <p v-if="errorMessage" class="error">
        <span class="warning-icon">⚠</span> {{ errorMessage }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMessage.value = 'ACCESS DENIED: 账号和密码不能为空'
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await axios.post('http://localhost:8000/api/login/', {
      username: username.value,
      password: password.value
    })
    
    // 登录成功，保存信息
    localStorage.setItem('userRole', response.data.role)
    localStorage.setItem('username', response.data.username)
    localStorage.setItem('studentId', response.data.student_id || '')
    
    // 【核心逻辑修改】如果是管理员账号，直接送去高大上的管理员面板！
    if (response.data.username === 'admin') {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
    
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'CONNECTION FAILED: 请检查网络连接'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 全局暗黑科技背景 */
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #050b14;
  overflow: hidden;
  font-family: 'Courier New', Courier, monospace;
}

/* 网格动态背景 */
.tech-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: 
    linear-gradient(rgba(0, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 30px 30px;
  z-index: 1;
}

/* 全局扫描线动画 */
.scan-line {
  position: absolute;
  width: 100%;
  height: 2px;
  background: rgba(0, 255, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
  animation: scan 4s linear infinite;
  z-index: 2;
}
@keyframes scan {
  0% { top: -10%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 110%; opacity: 0; }
}

/* 玻璃拟态与发光边框登录框 */
.login-box {
  position: relative;
  z-index: 10;
  background: rgba(10, 25, 47, 0.7);
  backdrop-filter: blur(10px);
  padding: 50px 40px;
  width: 380px;
  border: 1px solid rgba(0, 255, 255, 0.2);
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.1), inset 0 0 20px rgba(0, 255, 255, 0.05);
}

/* 科技感装饰角 */
.corner {
  position: absolute;
  width: 15px;
  height: 15px;
  border: 2px solid #0ff;
}
.top-left { top: -2px; left: -2px; border-right: none; border-bottom: none; }
.top-right { top: -2px; right: -2px; border-left: none; border-bottom: none; }
.bottom-left { bottom: -2px; left: -2px; border-right: none; border-top: none; }
.bottom-right { bottom: -2px; right: -2px; border-left: none; border-top: none; }

/* 标题样式 */
.sys-title {
  color: #0ff;
  font-size: 24px;
  text-align: center;
  margin: 0 0 5px 0;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
  letter-spacing: 2px;
}
.icon { font-size: 18px; vertical-align: middle; }
.subtitle {
  color: #8892b0;
  font-size: 12px;
  text-align: center;
  margin-bottom: 30px;
  letter-spacing: 1px;
}

/* 表单输入区 */
.form-group {
  margin-bottom: 25px;
  text-align: left;
}
.form-group label {
  display: block;
  color: #64ffda;
  font-size: 12px;
  margin-bottom: 8px;
  letter-spacing: 1px;
}
.input-wrapper {
  position: relative;
}
.input-wrapper input {
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(100, 255, 218, 0.3);
  color: #e6f1ff;
  font-family: inherit;
  font-size: 14px;
  box-sizing: border-box;
  outline: none;
  transition: all 0.3s ease;
}
.input-wrapper input:focus {
  border-color: #64ffda;
  box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
  background: rgba(100, 255, 218, 0.05);
}
.input-wrapper input::placeholder {
  color: rgba(136, 146, 176, 0.5);
}

/* 赛博朋克按钮 */
.cyber-btn {
  position: relative;
  width: 100%;
  padding: 15px;
  margin-top: 10px;
  background: transparent;
  color: #0ff;
  font-family: inherit;
  font-weight: bold;
  font-size: 16px;
  letter-spacing: 2px;
  border: 1px solid #0ff;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: inset 0 0 10px rgba(0, 255, 255, 0.2);
}
.cyber-btn:hover:not(:disabled) {
  background: rgba(0, 255, 255, 0.1);
  box-shadow: 0 0 15px #0ff, inset 0 0 15px #0ff;
  text-shadow: 0 0 5px #fff;
}
.cyber-btn:disabled {
  border-color: #444;
  color: #666;
  cursor: not-allowed;
  box-shadow: none;
}
.btn-glitch {
  position: absolute;
  top: 0; left: -100%;
  width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.4), transparent);
  transform: skewX(-45deg);
  animation: flash 3s infinite;
}
@keyframes flash {
  0% { left: -100%; }
  20% { left: 200%; }
  100% { left: 200%; }
}

/* 错误提示 */
.error {
  color: #ff4c4c;
  font-size: 12px;
  margin-top: 15px;
  text-align: center;
  text-shadow: 0 0 5px rgba(255, 76, 76, 0.5);
  animation: pulse-error 2s infinite;
}
@keyframes pulse-error {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
.warning-icon { font-weight: bold; }
</style>