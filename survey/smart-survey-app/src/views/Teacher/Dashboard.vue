<template>
  <div class="dashboard-page">
    <van-nav-bar title="教师控制台" />

    <van-cell-group inset class="mt-4">
      <van-field
        v-model="topic"
        label="教学难点"
        type="textarea"
        placeholder="例如：集成电路设计基础中的CMOS工艺，学生普遍觉得难懂..."
        rows="3"
        autosize
      />
      <van-cell title="生成题目数量">
        <template #right-icon>
          <van-stepper v-model="questionCount" min="1" max="25" />
        </template>
      </van-cell>
    </van-cell-group>

    <div class="p-4">
      <van-button 
        type="primary" 
        block 
        round 
        icon="aim" 
        :loading="isGenerating"
        loading-text="AI 正在思考题目..."
        @click="generate"
      >
        一键智能生成问卷
      </van-button>
    </div>

    <div v-if="currentTemplate" class="p-4">
      <van-divider>当前启用的问卷</van-divider>
      <van-card
        :title="currentTemplate.title"
        :desc="`共 ${currentTemplate.questions?.length || 0} 道题目`"
        thumb="https://fastly.jsdelivr.net/npm/@vant/assets/ipad.jpeg"
      >
        <template #tags>
          <van-tag plain type="primary">AI 生成</van-tag>
        </template>
        <template #footer>
          <van-button size="mini" type="success" @click="$router.push('/student')">去填答体验</van-button>
        </template>
      </van-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { showToast, showNotify } from 'vant';
import { generateSurvey } from '../../api/llmService';
import { saveSurveyTemplate, getSurveyTemplate } from '../../store/localDb';

const topic = ref('');
const isGenerating = ref(false);
const currentTemplate = ref(null);

// 新增：响应式变量，默认设置为 10 题
const questionCount = ref(10);

onMounted(() => {
  currentTemplate.value = getSurveyTemplate();
});

const generate = async () => {
  if (!topic.value.trim()) {
    showToast('请输入教学难点或问卷主题');
    return;
  }

  isGenerating.value = true;
  try {
    // 修改点：将 questionCount.value 传入 API 函数
    const surveyJson = await generateSurvey(topic.value, questionCount.value); 
    
    saveSurveyTemplate(surveyJson);
    currentTemplate.value = surveyJson;
    showNotify({ type: 'success', message: `成功生成 ${questionCount.value} 道题目！` });
    topic.value = ''; 
    
  } catch (error) {
    showNotify({ type: 'danger', message: error.message || '生成失败，请检查 API Key' });
  } finally {
    isGenerating.value = false;
  }
};
</script>

<style scoped>
.mt-4 { margin-top: 16px; }
.p-4 { padding: 16px; }
</style>