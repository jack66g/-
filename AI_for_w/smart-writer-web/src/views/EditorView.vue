<template>
  <div class="editor-layout">
    <header class="glass-header">
      <div class="header-left">
        <el-button link @click="router.push('/user-workspace')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <el-input v-model="article.title" placeholder="给你的巨作起个标题..." class="title-input" />
      </div>
      <div class="header-right">
        <el-button type="info" round @click="handleSave('draft')">存草稿</el-button>
        <el-button type="primary" round class="publish-btn" @click="handleSave('published')"
          >正式发布</el-button
        >
      </div>
    </header>

    <main class="editor-main">
      <MdEditor
        v-model="article.content"
        theme="dark"
        class="custom-editor"
        placeholder="写下你的灵感，或让右边的 AI 助手代劳..."
      />

      <div :class="['ai-sidebar', aiVisible ? 'active' : '']">
        <div class="ai-toggle" @click="aiVisible = !aiVisible">
          <el-icon><MagicStick /></el-icon>
          <span>AI 助手</span>
        </div>

        <div class="ai-content-inner">
          <el-tabs v-model="activeTab" class="ai-tabs">
            <el-tab-pane label="📝 全文生成" name="generate">
              <div class="tab-pane-content">
                <p class="ai-label">你想写什么主题？</p>
                <el-input
                  v-model="aiParams.topic"
                  type="textarea"
                  :rows="3"
                  placeholder="例如：Vue3 响应式原理深度解析"
                  class="glass-input"
                />

                <p class="ai-label">创作风格</p>
                <el-select v-model="aiParams.style" placeholder="请选择风格" class="glass-input">
                  <el-option label="幽默风趣" value="幽默风趣" />
                  <el-option label="专业严谨" value="专业严谨" />
                  <el-option label="小红书爆款" value="小红书爆款" />
                  <el-option label="硬核技术" value="硬核技术" />
                </el-select>

                <el-button
                  type="primary"
                  class="magic-btn"
                  :loading="aiLoading"
                  @click="handleAIGenerate"
                >
                  🚀 开始魔法创作
                </el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="✨ 文本润色" name="polish">
              <div class="tab-pane-content">
                <p class="ai-label">需要润色的文字内容</p>
                <el-input
                  v-model="aiParams.polishContent"
                  type="textarea"
                  :rows="6"
                  placeholder="把写得不顺的话贴在这里，或者在左边复制过来..."
                  class="glass-input"
                />
                <el-button
                  type="success"
                  class="magic-btn"
                  :loading="aiLoading"
                  @click="handleAIPolish"
                >
                  🪄 瞬间变高级
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>

          <div v-if="aiResult" class="ai-result-box">
            <div class="result-header">
              <span>生成结果：</span>
              <el-button link type="primary" @click="applyToEditor">插入正文</el-button>
            </div>
            <div class="result-body">{{ aiResult }}</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { ArrowLeft, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/request'

const router = useRouter()
const route = useRoute()

const article = ref({ id: null, title: '', content: '', status: 'draft' })
const aiVisible = ref(false)
const aiLoading = ref(false)
const aiResult = ref('')
const activeTab = ref('generate')

const aiParams = reactive({
  topic: '',
  style: '幽默风趣',
  polishContent: '',
})

// 1. 初始化
onMounted(async () => {
  if (route.params.id) {
    try {
      const res = await api.get(`articles/${route.params.id}/`)
      article.value = res
    } catch (err) {
      ElMessage.error('文章加载失败')
    }
  }
})

// 2. 模式一：生成全文
const handleAIGenerate = async () => {
  if (!aiParams.topic) return ElMessage.warning('亲，还没告诉我主题呢~')
  aiLoading.value = true
  try {
    // 对应后端的 AIGenerateView
    const res = await api.post('ai/generate/', {
      topic: aiParams.topic,
      style: aiParams.style,
    })
    aiResult.value = res.result
    ElMessage.success('AI 已为您构思完毕！')
  } catch (err) {
  } finally {
    aiLoading.value = false
  }
}

// 3. 模式二：智能润色
const handleAIPolish = async () => {
  if (!aiParams.polishContent) return ElMessage.warning('请提供需要润色的内容哦~')
  aiLoading.value = true
  try {
    // 对应后端的 AIPolishView
    const res = await api.post('ai/polish/', {
      content: aiParams.polishContent,
    })
    aiResult.value = res.result
    ElMessage.success('润色完成！')
  } catch (err) {
  } finally {
    aiLoading.value = false
  }
}

// 4. 将 AI 结果合并入编辑器
const applyToEditor = () => {
  article.value.content += `\n\n${aiResult.value}`
  aiResult.value = ''
  ElMessage.success('已添加到编辑器尾部')
}

// 5. 保存逻辑
const handleSave = async (status) => {
  if (!article.value.title) return ElMessage.warning('起个标题吧~')
  article.value.status = status
  try {
    if (article.value.id) {
      await api.put(`articles/${article.value.id}/`, article.value)
    } else {
      await api.post('articles/', article.value)
    }
    ElMessage.success('保存成功')
    router.push('/user-workspace')
  } catch (err) {}
}
</script>

<style scoped>
.editor-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.glass-header {
  height: 70px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
}

.title-input :deep(.el-input__wrapper) {
  background: transparent !important;
  box-shadow: none !important;
}
.title-input :deep(input) {
  color: #ffb6c1 !important;
  font-size: 20px;
  font-weight: bold;
}

.publish-btn {
  background: linear-gradient(90deg, #ff9a9e, #fecfef);
  border: none;
  color: #d63384;
  font-weight: bold;
}

.editor-main {
  flex: 1;
  position: relative;
  overflow: hidden;
  display: flex;
}

/* AI 侧边栏：暖色玻璃风 */
.ai-sidebar {
  position: absolute;
  right: -400px;
  top: 0;
  width: 400px;
  height: 100%;
  background: rgba(255, 240, 245, 0.1);
  backdrop-filter: blur(25px);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.4s ease;
  z-index: 1000;
}
.ai-sidebar.active {
  right: 0;
}

.ai-toggle {
  position: absolute;
  left: -45px;
  top: 120px;
  width: 45px;
  background: #ff9a9e;
  color: white;
  padding: 20px 5px;
  border-radius: 15px 0 0 15px;
  cursor: pointer;
  writing-mode: vertical-lr;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: -5px 0 15px rgba(255, 154, 158, 0.3);
}

.ai-content-inner {
  padding: 30px;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.ai-label {
  font-size: 14px;
  color: #ffb6c1;
  margin: 15px 0 8px;
}

.glass-input :deep(.el-textarea__inner),
.glass-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

.magic-btn {
  width: 100%;
  margin-top: 25px;
  padding: 25px;
  border-radius: 15px;
  border: none;
  font-weight: bold;
}

.ai-result-box {
  margin-top: 30px;
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 15px;
  border: 1px dashed #ff9a9e;
  overflow-y: auto;
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.result-body {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 深度适配编辑器 */
.custom-editor {
  flex: 1;
  border: none !important;
  --md-bk-color: transparent !important;
}
:deep(.cm-editor) {
  font-family: 'Fira Code', monospace;
}
</style>
