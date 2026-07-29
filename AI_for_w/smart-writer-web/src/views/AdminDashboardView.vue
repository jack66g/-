<template>
  <div class="admin-container">
    <aside class="admin-sidebar">
      <div class="admin-logo">
        <span class="pulse-dot"></span>
        控制中心
      </div>
      <nav class="admin-nav">
        <div
          :class="['nav-item', activeTab === 'stats' ? 'active' : '']"
          @click="activeTab = 'stats'"
        >
          <el-icon><DataLine /></el-icon> 数据总览
        </div>
        <div
          :class="['nav-item', activeTab === 'users' ? 'active' : '']"
          @click="activeTab = 'users'"
        >
          <el-icon><User /></el-icon> 用户管控
        </div>
        <div
          :class="['nav-item', activeTab === 'reports' ? 'active' : '']"
          @click="activeTab = 'reports'"
        >
          <el-icon><WarnTriangleFilled /></el-icon> 举报处理
          <el-badge
            v-if="stats.pending_reports > 0"
            :value="stats.pending_reports"
            class="report-badge"
          />
        </div>
      </nav>
      <div class="exit-btn" @click="router.push('/user-workspace')">退出管理</div>
    </aside>

    <main class="admin-main">
      <section class="stats-grid">
        <div class="stat-card blue">
          <div class="label">总用户量</div>
          <div class="value">{{ stats.total_users }}</div>
        </div>
        <div class="stat-card purple">
          <div class="label">总文章数</div>
          <div class="value">{{ stats.total_articles }}</div>
        </div>
        <div class="stat-card cyan">
          <div class="label">今日新增</div>
          <div class="value">{{ stats.today_articles }}</div>
        </div>
        <div class="stat-card red">
          <div class="label">待处理举报</div>
          <div class="value">{{ stats.pending_reports }}</div>
        </div>
      </section>

      <section class="content-view">
        <div v-if="activeTab === 'stats'" class="view-pane">
          <div class="chart-header">📈 全站创作增长趋势 (近 7 日实时数据)</div>
          <div ref="chartRef" class="main-chart"></div>
        </div>

        <div v-if="activeTab === 'users'" class="view-pane">
          <el-table :data="users" style="width: 100%" class="tech-table">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column label="注册时间">
              <template #default="scope">{{
                new Date(scope.row.date_joined).toLocaleDateString()
              }}</template>
            </el-table-column>
            <el-table-column label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                  {{ scope.row.is_active ? '正常' : '封禁中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button
                  size="small"
                  :type="scope.row.is_active ? 'danger' : 'success'"
                  @click="handleToggleUser(scope.row)"
                >
                  {{ scope.row.is_active ? '封禁' : '解封' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="activeTab === 'reports'" class="view-pane">
          <el-table :data="reports" style="width: 100%" class="tech-table">
            <el-table-column prop="reporter_name" label="举报人" width="120" />
            <el-table-column prop="article_title" label="违规内容" />
            <el-table-column prop="reason" label="理由" />
            <el-table-column label="状态">
              <template #default="scope">
                <span :class="scope.row.status">{{
                  scope.row.status === 'pending' ? '🔴 待处理' : '⚪ 已处理'
                }}</span>
              </template>
            </el-table-column>
            <el-table-column label="指令">
              <template #default="scope">
                <el-button
                  v-if="scope.row.status === 'pending'"
                  type="primary"
                  size="small"
                  @click="handleAudit(scope.row)"
                >
                  确认违规并删帖
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataLine, User, WarnTriangleFilled } from '@element-plus/icons-vue'
import api from '@/utils/request'
import * as echarts from 'echarts'

const router = useRouter()
const activeTab = ref('stats')
const stats = ref({ total_users: 0, total_articles: 0, today_articles: 0, pending_reports: 0 })
const users = ref([])
const reports = ref([])
const chartRef = ref(null)
const chartData = ref({ dates: [], counts: [] })
let myChart = null

// 1. 获取核心数据并填充图表变量
const fetchData = async () => {
  try {
    const [sRes, uRes, rRes] = await Promise.all([
      api.get('admin/stats/'),
      api.get('admin/mgr/users/'),
      api.get('admin/mgr/reports/'),
    ])
    stats.value = sRes
    // 注入后端返回的真实 7 天数据
    chartData.value = sRes.chart_data || { dates: [], counts: [] }

    users.value = Array.isArray(uRes) ? uRes : uRes.results || []
    reports.value = Array.isArray(rRes) ? rRes : rRes.results || []

    // 如果初始页是统计页，立即绘制
    if (activeTab.value === 'stats') initChart()
  } catch (err) {
    ElMessage.error('获取管理数据失败，请检查权限')
  }
}

// 2. 监听 Tab 切换，点回“数据总览”时必须重绘
watch(activeTab, (newVal) => {
  if (newVal === 'stats') {
    initChart()
  }
})

// 3. 初始化 Echarts (使用真实数据)
const initChart = () => {
  nextTick(() => {
    if (!chartRef.value || !chartData.value.dates.length) return

    // 如果已经有实例，先销毁，防止容器冲突
    if (myChart) myChart.dispose()

    myChart = echarts.init(chartRef.value)
    myChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0,0,0,0.7)',
        borderWidth: 0,
        textStyle: { color: '#fff' },
      },
      xAxis: {
        type: 'category',
        data: chartData.value.dates, // 后端传来的真实日期
        axisLabel: { color: '#888' },
      },
      yAxis: {
        type: 'value',
        minInterval: 1, // 保证是整数
        axisLabel: { color: '#888' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      },
      series: [
        {
          name: '文章发布量',
          data: chartData.value.counts, // 后端传来的真实投稿数
          type: 'bar',
          barWidth: '40%',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#00f2ff' },
              { offset: 1, color: '#0066ff' },
            ]),
            borderRadius: [5, 5, 0, 0],
          },
        },
      ],
    })

    // 自动适配窗口
    window.onresize = () => myChart.resize()
  })
}

// 4. 封禁/解封
const handleToggleUser = async (user) => {
  try {
    const res = await api.patch(`admin/mgr/users/${user.id}/toggle_active/`)
    // 局部更新状态，避免重新拉取全量数据导致的闪烁
    user.is_active = res.is_active
    ElMessage.success(res.is_active ? '用户已解封' : '用户已封禁')
  } catch (err) {}
}

// 5. 审核举报
const handleAudit = async (report) => {
  ElMessageBox.confirm('确认该文章违规并将其永久删除吗？', '严重警告', {
    confirmButtonText: '执行删除',
    type: 'warning',
  }).then(async () => {
    try {
      await api.post(`admin/mgr/reports/${report.id}/audit/`)
      ElMessage.success('违规文章已清理')
      fetchData()
    } catch (err) {}
  })
}

onMounted(fetchData)

// 离开时解绑事件，防止内存泄漏
onBeforeUnmount(() => {
  window.onresize = null
  if (myChart) myChart.dispose()
})
</script>

<style scoped>
/* 样式保持你的深色科技感不变 */
.admin-container {
  display: flex;
  height: 100vh;
  background: #0b0e14;
  color: #e0e0e0;
  font-family: 'Inter', sans-serif;
}
.admin-sidebar {
  width: 240px;
  background: #131720;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}
.admin-logo {
  font-size: 20px;
  font-weight: bold;
  color: #00f2ff;
  text-align: center;
  margin-bottom: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.pulse-dot {
  width: 8px;
  height: 8px;
  background: #00f2ff;
  border-radius: 50%;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(0, 242, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 242, 255, 0);
  }
}
.admin-nav {
  flex: 1;
}
.nav-item {
  padding: 15px 30px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #888;
}
.nav-item:hover,
.nav-item.active {
  background: rgba(0, 242, 255, 0.05);
  color: #00f2ff;
}
.nav-item.active {
  border-right: 3px solid #00f2ff;
}
.exit-btn {
  padding: 20px;
  text-align: center;
  color: #ff4d4d;
  cursor: pointer;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.admin-main {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}
.stat-card {
  padding: 25px;
  border-radius: 16px;
  background: #1a1f2b;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.stat-card.blue {
  border-left: 4px solid #0066ff;
}
.stat-card.purple {
  border-left: 4px solid #a855f7;
}
.stat-card.cyan {
  border-left: 4px solid #06b6d4;
}
.stat-card.red {
  border-left: 4px solid #ef4444;
}
.stat-card .label {
  color: #888;
  font-size: 14px;
}
.stat-card .value {
  font-size: 32px;
  font-weight: bold;
  margin-top: 10px;
}
.view-pane {
  background: #1a1f2b;
  border-radius: 16px;
  padding: 30px;
  min-height: 500px;
}
.main-chart {
  height: 400px;
  width: 100%;
}
:deep(.tech-table) {
  background-color: transparent !important;
  color: #ccc !important;
}
:deep(.el-table tr) {
  background-color: transparent !important;
}
:deep(.el-table th.el-table__cell) {
  background-color: #131720 !important;
  color: #888;
  border-bottom: 1px solid #2d3446;
}
:deep(.el-table__row:hover td) {
  background-color: rgba(255, 255, 255, 0.02) !important;
}
</style>
