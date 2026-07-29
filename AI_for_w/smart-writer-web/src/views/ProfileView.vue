<template>
  <div class="profile-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚙️ 个人中心与 AI 配置</span>
          <el-button type="success" @click="router.push('/user-workspace')">返回工作台</el-button>
        </div>
      </template>

      <el-form label-width="150px">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.username" disabled />
        </el-form-item>
        <el-form-item label="当前角色">
          <el-tag>{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
        </el-form-item>

        <el-divider>核心配置</el-divider>

        <el-form-item label="DeepSeek API Key">
          <el-input
            v-model="userInfo.deepseek_api_key"
            type="password"
            show-password
            placeholder="sk-xxxxxxxxxxxxxxxxxxx"
          />
          <div style="font-size: 12px; color: #888; margin-top: 5px">
            请在此填入您的官方密钥，平台不会明文保存。
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="saveProfile">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/request'

const router = useRouter()
const userInfo = ref({ username: '', role: '', deepseek_api_key: '' })
const loading = ref(false)

// 页面加载时获取个人信息
onMounted(async () => {
  try {
    const res = await api.get('users/me/')
    userInfo.value = res
  } catch (error) {
    console.error(error)
  }
})

// 保存 API Key 到后端
const saveProfile = async () => {
  loading.value = true
  try {
    // 调用 PATCH 接口只更新允许修改的字段
    await api.patch('users/me/', {
      deepseek_api_key: userInfo.value.deepseek_api_key,
    })
    ElMessage.success('配置保存成功！您现在可以使用 AI 助手了。')
  } catch (error) {
    // 报错由拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-container {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
