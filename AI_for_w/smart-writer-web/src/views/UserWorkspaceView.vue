<template>
  <div class="workspace-layout">
    <aside class="glass-sidebar">
      <div class="brand">
        <h2 class="logo-text">COGNICORE</h2>
        <div class="logo-line"></div>
      </div>

      <div class="user-profile">
        <el-avatar
          :size="64"
          src="https://api.dicebear.com/7.x/bottts/svg?seed=Felix"
          class="avatar-glow"
        />
        <p class="username">{{ userStore.username }}</p>
        <el-tag
          size="small"
          effect="dark"
          :class="userStore.role === 'admin' ? 'admin-tag' : 'role-tag'"
        >
          {{ userStore.role === 'admin' ? '最高管理员' : '标准创作者' }}
        </el-tag>
      </div>

      <nav class="side-nav">
        <div class="nav-item active">
          <el-icon><Document /></el-icon> 我的创作库
        </div>

        <div
          v-if="userStore.role === 'admin'"
          class="nav-item admin-entry"
          @click="router.push('/admin-dashboard')"
        >
          <el-icon><Monitor /></el-icon> 管理员控制台
        </div>

        <div class="nav-item" @click="router.push('/profile')">
          <el-icon><Setting /></el-icon> AI 密钥设置
        </div>

        <div class="nav-item" @click="router.push('/discovery')">
          <el-icon><Compass /></el-icon> 发现·公共广场
        </div>

        <div class="nav-item logout" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon> 退出系统
        </div>
      </nav>
    </aside>

    <main class="main-content">
      <div class="content-glass-card">
        <div class="table-header">
          <div class="header-left">
            <span class="emoji-icon">📝</span>
            <h2>我的创作库</h2>
          </div>
          <el-button class="ai-btn" @click="handleCreate">
            <el-icon><MagicStick /></el-icon> 开启 AI 创作
          </el-button>
        </div>

        <el-table
          :data="articles"
          v-loading="loading"
          class="custom-glass-table"
          style="width: 100%"
        >
          <el-table-column prop="title" label="文章标题" min-width="250" show-overflow-tooltip />

          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <span :class="['status-dot', scope.row.status]"></span>
              {{ scope.row.status === 'published' ? '已发布' : '草稿' }}
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="200">
            <template #default="scope">
              {{ formatTime(scope.row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="160" align="right">
            <template #default="scope">
              <el-button link class="edit-link" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button link class="delete-link" @click="handleDelete(scope.row.id)"
                >删除</el-button
              >
            </template>
          </el-table-column>

          <template #empty>
            <div class="empty-state">
              <el-empty description="暂时没有作品，快去让 AI 帮你写一篇吧" />
            </div>
          </template>
        </el-table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Setting,
  SwitchButton,
  MagicStick,
  Compass,
  Monitor,
} from '@element-plus/icons-vue'
import api from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()
const articles = ref([])
const loading = ref(false)

// 时间格式化助手
const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}

// 获取列表
const fetchArticles = async () => {
  loading.value = true
  try {
    const res = await api.get('articles/')
    articles.value = res
  } catch (error) {
    console.error('Fetch error:', error)
  } finally {
    loading.value = false
  }
}

// 删除文章
const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    customClass: 'glass-message-box',
  }).then(async () => {
    try {
      await api.delete(`articles/${id}/`)
      ElMessage.success('删除成功')
      fetchArticles()
    } catch (err) {}
  })
}

const handleLogout = () => {
  userStore.clearAuth()
  router.push('/login')
}

const handleCreate = () => router.push('/editor')
const handleEdit = (row) => router.push({ name: 'editor', params: { id: row.id } })

onMounted(fetchArticles)
</script>

<style scoped>
/* 1. 基础布局结构 */
.workspace-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  overflow: hidden;
}

/* 2. 侧边栏玻璃拟态 */
.glass-sidebar {
  width: 280px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  padding: 40px 20px;
}

.logo-text {
  color: #00f2ff;
  letter-spacing: 4px;
  text-align: center;
  font-size: 24px;
  text-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
}

.logo-line {
  height: 2px;
  background: linear-gradient(90deg, transparent, #00f2ff, transparent);
  margin: 10px 0 40px;
}

.user-profile {
  text-align: center;
  margin-bottom: 50px;
}

.username {
  color: #fff;
  margin: 15px 0 5px;
  font-weight: bold;
  font-size: 18px;
}

.avatar-glow {
  border: 2px solid rgba(0, 242, 255, 0.3);
  box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
}

.role-tag {
  background-color: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.admin-tag {
  background-color: rgba(0, 242, 255, 0.2) !important;
  border: 1px solid #00f2ff !important;
  color: #00f2ff !important;
}

.side-nav .nav-item {
  padding: 15px 20px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.side-nav .nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.side-nav .nav-item.active {
  background: rgba(0, 242, 255, 0.15);
  color: #00f2ff;
  border: 1px solid rgba(0, 242, 255, 0.3);
}

/* 管理员入口特殊发光效果 */
.admin-entry {
  color: #00f2ff !important;
  font-weight: bold;
  border: 1px dashed rgba(0, 242, 255, 0.3) !important;
  margin-top: 20px;
  background: rgba(0, 242, 255, 0.05);
}

.admin-entry:hover {
  background: rgba(0, 242, 255, 0.1) !important;
  box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
}

.side-nav .logout {
  margin-top: auto;
  color: #ff4d4d;
}

/* 3. 主内容区域 */
.main-content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}

.content-glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 40px;
  min-height: 80vh;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  color: #fff;
  font-size: 24px;
}

.ai-btn {
  background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
  border: none;
  color: white;
  padding: 20px 25px;
  border-radius: 12px;
  font-weight: bold;
  transition: transform 0.2s;
}

.ai-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4);
}

/* 4. 表格样式深度定制 */
:deep(.custom-glass-table) {
  background: transparent !important;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(255, 255, 255, 0.05);
  --el-table-border-color: rgba(255, 255, 255, 0.08);
  --el-table-text-color: rgba(255, 255, 255, 0.9);
  --el-table-header-text-color: #00f2ff;
}

:deep(.el-table__inner-wrapper::before) {
  display: none;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.status-dot.published {
  background: #00ff88;
  box-shadow: 0 0 8px #00ff88;
}
.status-dot.draft {
  background: #aaa;
}

.edit-link {
  color: #00f2ff;
}
.delete-link {
  color: #ff4d4d;
}

.empty-state {
  padding: 60px 0;
}
:deep(.el-empty__description p) {
  color: rgba(255, 255, 255, 0.5) !important;
}
</style>
