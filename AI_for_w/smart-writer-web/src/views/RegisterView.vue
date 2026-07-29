<template>
  <div class="simple-login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>创建新账号</h2>
          <p>加入我们的 AI 创作社区</p>
        </div>
      </template>

      <el-form :model="regForm">
        <el-form-item>
          <el-input v-model="regForm.username" placeholder="设置用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="regForm.email" placeholder="邮箱地址 (可选)" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="regForm.password"
            type="password"
            placeholder="设置密码"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="regForm.confirm"
            type="password"
            placeholder="确认密码"
            size="large"
            show-password
          />
        </el-form-item>

        <el-button
          type="success"
          class="submit-btn"
          :loading="loading"
          @click="handleRegister"
          size="large"
        >
          立即注册
        </el-button>

        <div class="footer-links">
          <el-button link type="info" @click="router.push('/login')">已有账号？返回登录</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/request'

const router = useRouter()
const regForm = ref({ username: '', email: '', password: '', confirm: '' })
const loading = ref(false)

const handleRegister = async () => {
  if (!regForm.value.username || !regForm.value.password) return ElMessage.warning('必填项不能为空')
  if (regForm.value.password !== regForm.value.confirm) return ElMessage.error('两次密码输入不一致')

  loading.value = true
  try {
    await api.post('register/', {
      username: regForm.value.username,
      email: regForm.value.email,
      password: regForm.value.password,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (err) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 复用登录页的布局样式 */
.simple-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}
.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
}
.card-header {
  text-align: center;
}
.submit-btn {
  width: 100%;
}
.footer-links {
  margin-top: 20px;
  text-align: center;
}
</style>
