<template>
  <div class="stats-wrapper">
    <div class="glass-bg-circle circle-1"></div>
    <div class="glass-bg-circle circle-2"></div>

    <div class="main-content">
      <div class="top-nav">
        <h2 class="title">📊 教师教务大盘</h2>
        <el-button round class="glass-btn" @click="$router.push('/dashboard')">返回控制台</el-button>
      </div>

      <el-row :gutter="20" class="stat-cards">
        <el-col :span="6" v-for="(item, index) in summaryCards" :key="index">
          <div class="glass-card stat-item">
            <div class="icon">{{ item.icon }}</div>
            <div class="info">
              <p class="label">{{ item.label }}</p>
              <p class="number">{{ item.value }}</p>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-card class="glass-table-card">
        <template #header>
          <div class="card-header">
            <span>⚖️ 待处理请假申请</span>
            <el-tag type="danger" effect="dark" round>{{ pendingLeaves.length }} 条待办</el-tag>
          </div>
        </template>
        <el-table :data="pendingLeaves" style="width: 100%" max-height="300" class="custom-table">
          <el-table-column prop="student_name" label="申请人" width="120" />
          <el-table-column prop="apply_time" label="申请时间" width="180" />
          <el-table-column prop="reason" label="请假事由" show-overflow-tooltip />
          <el-table-column label="操作" width="180">
            <template #default="scope">
              <el-button size="small" type="success" @click="approveLeave(scope.row.id, '已通过')">通过</el-button>
              <el-button size="small" type="danger" @click="approveLeave(scope.row.id, '已拒绝')">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="glass-table-card mt-20">
        <template #header>
          <div class="card-header">
            <span>📅 全体考勤流水</span>
            <el-button type="primary" size="small" plain @click="fetchAttendance">刷新数据</el-button>
          </div>
        </template>
        <el-table :data="attendanceList" border stripe class="custom-table">
          <el-table-column prop="student_name" label="姓名" />
          <el-table-column prop="date" label="日期" width="150" />
          <el-table-column prop="check_in_time" label="签到时间" width="150" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.status === '已签到' ? 'success' : 'danger'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const stats = ref({ total_students: 0, present_count: 0, leave_count: 0, absent_count: 0 })
const allLeaves = ref([])
const attendanceList = ref([])

// 统计卡片配置
const summaryCards = computed(() => [
  { label: '学生总数', value: stats.value.total_students, icon: '👥' },
  { label: '今日签到', value: stats.value.present_count, icon: '✅' },
  { label: '请假人数', value: stats.value.leave_count, icon: '📝' },
  { label: '异常缺勤', value: stats.value.absent_count, icon: '🚨' }
])

// 过滤待审批记录
const pendingLeaves = computed(() => allLeaves.value.filter(l => l.status === '待审批'))

// 【核心修复】统一函数名为 fetchAttendance，对接后端接口
const fetchAttendance = async () => {
  try {
    const [sRes, lRes, aRes] = await Promise.all([
      axios.get('http://localhost:8000/api/stats/'),
      axios.get('http://localhost:8000/api/leaves/'),
      axios.get('http://localhost:8000/api/attendance/')
    ])
    stats.value = sRes.data
    allLeaves.value = lRes.data
    attendanceList.value = aRes.data
  } catch (err) {
    console.error("API Error:", err)
    ElMessage.error('数据加载失败，请检查后端 API 连通性')
  }
}

// 【核心修复】审批逻辑：转换状态码并发送 PUT 请求
const approveLeave = async (id, statusText) => {
  // 后端数据库字段只认 'approved' 或 'rejected'
  const backendStatus = statusText === '已通过' ? 'approved' : 'rejected'
  
  try {
    await axios.put('http://localhost:8000/api/leaves/', { 
      id: id, 
      status: backendStatus 
    })
    ElMessage.success(`审批成功：${statusText}`)
    fetchAttendance() // 成功后刷新列表和统计卡片
  } catch (err) {
    ElMessage.error('审批操作失败')
  }
}

onMounted(fetchAttendance)
</script>

<style scoped>
/* 容器背景渐变 */
.stats-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

/* 背景浮动圆圈 */
.glass-bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  z-index: 0;
}
.circle-1 { width: 300px; height: 300px; background: rgba(255, 255, 255, 0.2); top: -50px; left: -50px; }
.circle-2 { width: 400px; height: 400px; background: rgba(0, 255, 255, 0.1); bottom: -100px; right: -50px; }

.main-content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}
.title { color: white; margin: 0; font-size: 28px; text-shadow: 0 2px 10px rgba(0,0,0,0.2); }

/* 毛玻璃卡片通用样式 */
.glass-card {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.stat-cards { margin-bottom: 30px; }
.stat-item {
  display: flex;
  align-items: center;
  padding: 25px;
  transition: all 0.3s ease;
  color: white;
}
.stat-item:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.3); }
.stat-item .icon { font-size: 45px; margin-right: 20px; }
.label { margin: 0; font-size: 14px; opacity: 0.8; }
.number { margin: 5px 0 0 0; font-size: 30px; font-weight: bold; }

/* 表格卡片样式 */
.glass-table-card {
  background: rgba(255, 255, 255, 0.85) !important;
  border-radius: 20px !important;
  border: none !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
}

.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 18px; }
.mt-20 { margin-top: 20px; }

/* 自定义表格透明感 */
.custom-table { border-radius: 10px; overflow: hidden; }

.glass-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.5);
}
.glass-btn:hover { background: white; color: #764ba2; }
</style>