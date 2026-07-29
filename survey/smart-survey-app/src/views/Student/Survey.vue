<template>
  <div class="survey-page">
    <van-nav-bar title="问卷调查" left-text="返回" left-arrow @click-left="$router.back()" />

    <div v-if="!template" class="empty-state">
      <van-empty description="老师还没有发布问卷哦~" />
    </div>

    <div v-else class="survey-content">
      <div class="header">
        <h2>{{ template.title }}</h2>
        <p class="desc">请认真作答以下题目</p>
      </div>

      <van-form @submit="onSubmit">
        <div v-for="(q, index) in template.questions" :key="index" class="question-card">
          <div class="q-title">{{ index + 1 }}. {{ q.title }}</div>
          
          <van-radio-group v-model="answers[`q_${index}`]" class="mt-2">
            <van-cell-group inset>
              <van-cell 
                v-for="(opt, optIndex) in q.options" 
                :key="optIndex" 
                :title="opt" 
                clickable 
                @click="answers[`q_${index}`] = opt"
              >
                <template #right-icon>
                  <van-radio :name="opt" />
                </template>
              </van-cell>
            </van-cell-group>
          </van-radio-group>
        </div>

        <div class="p-4 mt-4">
          <van-button round block type="primary" native-type="submit">
            提交答卷
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { showToast, showSuccessToast } from 'vant';
import { getSurveyTemplate, saveStudentAnswer } from '../../store/localDb';
import { useRouter } from 'vue-router';

const router = useRouter();
const template = ref(null);
const answers = ref({}); // 存放用户的答案，结构如 { q_0: '选项A', q_1: '选项B' }

onMounted(() => {
  // 进页面时拉取最新的问卷模板
  template.value = getSurveyTemplate();
});

const onSubmit = () => {
  // 校验是否所有题都答了
  const questionCount = template.value.questions.length;
  const answeredCount = Object.keys(answers.value).length;
  
  if (answeredCount < questionCount) {
    showToast('请答完所有题目后再提交！');
    return;
  }

  // 保存答案到本地模拟数据库
  saveStudentAnswer({
    ...answers.value,
    submitTime: new Date().toLocaleString()
  });

  showSuccessToast('提交成功！');
  
  // 提交完清空表单，方便你测试刷数据
  answers.value = {}; 
  router.push('/teacher'); // 跳回教师端看看
};
</script>

<style scoped>
.empty-state { margin-top: 100px; }
.survey-content { padding-bottom: 80px; }
.header { text-align: center; padding: 20px; background: #fff; margin-bottom: 16px; }
.header h2 { margin: 0; font-size: 20px; color: #333; }
.header .desc { font-size: 14px; color: #666; margin-top: 8px; }
.question-card { margin-bottom: 20px; padding: 0 16px; }
.q-title { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #333; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.p-4 { padding: 16px; }
</style>