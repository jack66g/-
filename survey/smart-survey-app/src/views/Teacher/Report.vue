<template>
  <div class="report-page">
    <van-nav-bar title="数据分析与报告" />

    <div v-if="stats.totalSubmissions === 0" class="empty-state">
      <van-empty description="暂无答卷数据，快去让学生填写吧" />
    </div>

    <div v-else class="content-area">
      <van-cell-group inset class="mt-4">
        <van-cell title="收集总份数" :value="`${stats.totalSubmissions} 份`" size="large" />
      </van-cell-group>

      <div class="chart-container mt-4">
        <div class="chart-title">核心问题数据占比</div>
        <div id="pieChart1" style="width: 100%; height: 250px;"></div>
        <div id="pieChart2" style="width: 100%; height: 250px;"></div>
      </div>

      <div class="p-4 mt-4">
        <van-button 
          type="primary" 
          block 
          round 
          icon="orders-o" 
          :loading="isGenerating"
          loading-text="AI 正在深度分析数据..."
          @click="handleGenerateReport"
        >
          一键生成 AI 教学改进报告
        </van-button>
      </div>

      <div v-if="aiReportText" class="report-box">
        <div class="report-header">
          <van-icon name="bulb-o" size="20" color="#1989fa" />
          <span>AI 教学督导建议</span>
        </div>
        <div class="report-content">{{ aiReportText }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { showNotify } from 'vant';
import { getStatistics } from '../../store/localDb';
import { generateReport } from '../../api/llmService';
import * as echarts from 'echarts';

const stats = ref({ totalSubmissions: 0, details: null });
const isGenerating = ref(false);
const aiReportText = ref('');

onMounted(async () => {
  // 获取本地统计数据
  stats.value = getStatistics();

  // 如果有数据，渲染 ECharts 图表
  if (stats.value.totalSubmissions > 0 && stats.value.details) {
    await nextTick(); // 确保 DOM 已经渲染
    renderCharts();
  }
});

// 渲染 ECharts 饼图的方法
const renderCharts = () => {
  const details = Object.values(stats.value.details);
  
  // 渲染第一题的数据
  if (details[0]) {
    initPieChart('pieChart1', details[0].title, details[0].optionsCount);
  }
  // 渲染第二题的数据（如果有）
  if (details[1]) {
    initPieChart('pieChart2', details[1].title, details[1].optionsCount);
  }
};

// ECharts 初始化工具函数
const initPieChart = (domId, title, optionsCount) => {
  const chartDom = document.getElementById(domId);
  if (!chartDom) return;
  const myChart = echarts.init(chartDom);
  
  // 将我们本地存的 {"选项A": 2, "选项B": 3} 格式转为 ECharts 需要的 [{name: "选项A", value: 2}]
  const pieData = Object.entries(optionsCount).map(([name, value]) => ({ name, value }));

  const option = {
    title: { text: 'Q: ' + (title.length > 15 ? title.substring(0, 15) + '...' : title), left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'item' },
    legend: { bottom: '0', left: 'center' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
        labelLine: { show: false },
        data: pieData
      }
    ]
  };
  myChart.setOption(option);
};

// 调用大模型生成报告
const handleGenerateReport = async () => {
  isGenerating.value = true;
  try {
    const text = await generateReport(stats.value);
    aiReportText.value = text;
    showNotify({ type: 'success', message: '报告生成完毕！' });
  } catch (error) {
    showNotify({ type: 'danger', message: error.message || '报告生成失败' });
  } finally {
    isGenerating.value = false;
  }
};
</script>

<style scoped>
.empty-state { margin-top: 100px; }
.content-area { padding-bottom: 80px; }
.mt-4 { margin-top: 16px; }
.p-4 { padding: 16px; }
.chart-container { background: #fff; margin: 16px; border-radius: 8px; padding: 16px 0; }
.chart-title { text-align: center; font-weight: bold; color: #333; margin-bottom: 16px; }
.report-box { background: #fff; margin: 16px; border-radius: 8px; padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.report-header { display: flex; align-items: center; font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #333; }
.report-header span { margin-left: 8px; }
.report-content { font-size: 14px; color: #666; line-height: 1.6; white-space: pre-wrap; /* 保留大模型返回的换行符 */ }
</style>