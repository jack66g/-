<template>
  <div class="sweet-container">
    <div class="heart-rain" ref="heartRain"></div>

    <main class="discovery-content">
      <header class="sweet-header">
        <div class="header-card">
          <div class="brand-section">
            <span class="emoji-logo">📡</span>
            <div class="title-group">
              <h1 class="main-title">发现·公共节点</h1>
              <p class="en-subtitle">Discover · Public Node</p>
            </div>
          </div>
          <div class="btn-group">
            <el-button class="glass-btn primary" @click="router.push('/user-workspace')"
              >进入工作台</el-button
            >
            <el-button class="glass-btn info" @click="router.push('/profile')">AI 配置</el-button>
          </div>
        </div>
      </header>

      <div class="article-grid">
        <div v-for="item in articles" :key="item.id" class="sweet-card">
          <div class="card-glass-body">
            <h3 class="article-title" @click="viewFullArticle(item)">{{ item.title }}</h3>
            <div class="article-info">
              <span class="author">👤 {{ item.author_name }}</span>
              <span class="time">📅 {{ new Date(item.created_at).toLocaleDateString() }}</span>
            </div>
            <p class="article-excerpt">{{ item.content.slice(0, 80) }}...</p>

            <el-button link type="primary" class="read-more" @click="viewFullArticle(item)"
              >阅读全文 >>
            </el-button>

            <div class="interaction-bar">
              <div class="action-btns">
                <button
                  :class="['action-item', 'like', item.user_interact === 1 ? 'active' : '']"
                  @click="handleInteract(item, 1)"
                >
                  <span class="icon">👍</span> {{ item.like_count }}
                </button>
                <button
                  :class="['action-item', 'dislike', item.user_interact === 2 ? 'active' : '']"
                  @click="handleInteract(item, 2)"
                >
                  <span class="icon">👎</span>
                </button>
              </div>
              <button class="report-btn" @click="openReport(item)">🚨 举报</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <el-dialog
      v-model="detailVisible"
      :title="selectedArticle.title"
      width="60%"
      destroy-on-close
      custom-class="reading-dialog"
    >
      <div class="reading-meta">
        <span>作者: {{ selectedArticle.author_name }}</span>
        <el-divider direction="vertical" />
        <span>发布于: {{ new Date(selectedArticle.created_at).toLocaleString() }}</span>
      </div>
      <div class="reading-body">
        <MdPreview :modelValue="selectedArticle.content" theme="light" />
      </div>
      <template #footer>
        <el-button @click="detailVisible = false" round>关闭阅读</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="reportVisible"
      title="安全中心 - 异常反馈"
      width="380px"
      custom-class="sweet-dialog"
    >
      <el-input
        v-model="reportReason"
        type="textarea"
        placeholder="请告诉我们文章哪里不合适..."
        rows="4"
      />
      <template #footer>
        <el-button @click="reportVisible = false" round>算啦</el-button>
        <el-button type="danger" @click="submitReport" round>提交反馈</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MdPreview } from 'md-editor-v3' // ⚡ 引入预览组件
import 'md-editor-v3/lib/preview.css'
import api from '@/utils/request'

const router = useRouter()
const articles = ref([])
const heartRain = ref(null)

// 详情预览状态
const detailVisible = ref(false)
const selectedArticle = ref({})

// 举报相关
const reportVisible = ref(false)
const reportReason = ref('')
const currentArticleId = ref(null)

let heartInterval = null

const fetchPublicArticles = async () => {
  try {
    const res = await api.get('articles/public/')
    articles.value = res
  } catch (err) {}
}

// ⚡ 查看全文逻辑
const viewFullArticle = (item) => {
  selectedArticle.value = item
  detailVisible.value = true
}

const createHeart = () => {
  if (!heartRain.value) return
  const heart = document.createElement('div')
  heart.className = 'heart-drop'
  heart.innerHTML = '❤️'
  heart.style.left = Math.random() * 100 + 'vw'
  heart.style.fontSize = Math.random() * 15 + 10 + 'px'
  heart.style.animationDuration = Math.random() * 3 + 2 + 's'
  heartRain.value.appendChild(heart)
  setTimeout(() => heart.remove(), 4000)
}

const handleInteract = async (item, type) => {
  try {
    const res = await api.post(`articles/${item.id}/interact/`, { type })
    item.like_count = res.like_count
    item.dislike_count = res.dislike_count
    item.user_interact = res.current_interact
  } catch (err) {
    if (err.response?.status === 401) ElMessage.warning('登录之后才能互动哦~')
  }
}

const openReport = (item) => {
  currentArticleId.value = item.id
  reportVisible.value = true
}

const submitReport = async () => {
  if (!reportReason.value) return ElMessage.warning('给个理由嘛~')
  try {
    await api.post(`articles/${currentArticleId.value}/report/`, { reason: reportReason.value })
    ElMessage.success('收到！我们会处理的。')
    reportVisible.value = false
    reportReason.value = ''
  } catch (err) {}
}

onMounted(() => {
  fetchPublicArticles()
  heartInterval = setInterval(createHeart, 400)
})

onBeforeUnmount(() => clearInterval(heartInterval))
</script>

<style scoped>
/* 原有背景、标题、卡片样式保持不变 ... */
.sweet-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 30%, #fbc2eb 60%, #a1c4fd 100%);
  position: relative;
  overflow-x: hidden;
  padding-bottom: 50px;
}
.heart-rain {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}
:deep(.heart-drop) {
  position: absolute;
  top: -50px;
  animation: fallDown linear forwards;
}
@keyframes fallDown {
  to {
    transform: translateY(110vh) rotate(360deg);
    opacity: 0;
  }
}

.discovery-content {
  position: relative;
  z-index: 10;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}
.header-card {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(15px);
  border-radius: 24px;
  padding: 30px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.6);
}
.main-title {
  font-size: 32px;
  color: #fff;
  margin: 0;
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 30px;
}
.sweet-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}
.sweet-card:hover {
  transform: translateY(-5px);
}
.card-glass-body {
  padding: 25px;
}

/* ⚡ 增强标题交互感 */
.article-title {
  color: #d63384;
  font-size: 20px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: color 0.3s;
}
.article-title:hover {
  color: #ff6b6b;
  text-decoration: underline;
}

.read-more {
  margin-bottom: 15px;
  font-weight: bold;
}

.interaction-bar {
  border-top: 1px dashed rgba(255, 107, 107, 0.2);
  padding-top: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.action-item {
  background: white;
  border: 1px solid #ffebeb;
  color: #ff6b6b;
  padding: 5px 12px;
  border-radius: 20px;
  cursor: pointer;
  margin-right: 5px;
}
.action-item.active {
  background: #ff6b6b;
  color: white;
}

/* 📖 阅读弹窗深度定制 */
:deep(.reading-dialog) {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(25px) !important;
  border-radius: 30px !important;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1) !important;
}
:deep(.el-dialog__header) {
  padding-top: 30px;
  text-align: center;
}
:deep(.el-dialog__title) {
  font-size: 26px;
  color: #d63384;
  font-weight: bold;
}

.reading-meta {
  text-align: center;
  color: #888;
  margin-bottom: 20px;
  font-size: 13px;
}
.reading-body {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 15px;
}

/* 隐藏预览器的背景，让它透出弹窗的玻璃感 */
:deep(.md-editor-preview) {
  background: transparent !important;
}
</style>
