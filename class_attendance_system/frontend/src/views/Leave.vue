<template>
  <div class="leave-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2><el-icon><Document /></el-icon> 请假管理中心</h2>
          <el-button @click="$router.push('/dashboard')">返回控制台</el-button>
        </div>
      </template>

      <div v-if="role === 'student'" class="student-view">
        
        <el-card shadow="never" class="apply-section">
          <template #header>
            <span>发起新请假</span>
          </template>
          <el-form :model="leaveForm" label-width="80px">
            <el-form-item label="请假事由" required>
              <el-input 
                v-model="leaveForm.reason" 
                type="textarea" 
                :rows="3" 
                placeholder="请详细描述请假原因（如：因发烧去校医院就诊）..." 
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitLeave" :loading="isSubmitting">
                提交申请
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="history-section">
          <template #header>
            <span>我的请假记录</span>
          </template>
          <el-table :data="myLeaveList" border style="width: 100%" v-loading="isLoading">
            <el-table-column prop="apply_time" label="申请时间" width="180" />
            <el-table-column prop="reason" label="请假事由" />
            <el-table-column prop="status" label="审批状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <div v-if="role === 'teacher'" class="teacher-view">
        <el-alert title="教师审批功能开发中..." type="info" show-icon />
      </div>

    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const role = ref('')
const username = ref('')
const studentId = ref('')

const leaveForm = ref({ reason: '' })
const leaveList = ref([]) // 存放后端返回的所有请假数据

const isSubmitting = ref(false)
const isLoading = ref(false)

// 页面加载时初始化
onMounted(() => {
  role.value = localStorage.getItem('userRole')
  username.value = localStorage.getItem('username')
  studentId.value = localStorage.getItem('studentId')
  
  fetchLeaves()
})

// 计算属性：只过滤出当前登录学生的请假记录
const myLeaveList = computed(() => {
  return leaveList.value.filter(item => item.student_name === username.value)
})

// 状态标签颜色转换
const getStatusType = (status) => {
  if (status === '已通过') return 'success'
  if (status === '已拒绝') return 'danger'
  return 'warning' // 待审批
}

// 1. 获取请假列表数据
const fetchLeaves = async () => {
  isLoading.value = true
  try {
    // 调用的就是我们第二天在 Django 里写好的那个 GET 接口
    const res = await axios.get('http://localhost:8000/api/leaves/')
    leaveList.value = res.data
  } catch (error) {
    ElMessage.error('获取请假记录失败')
  } finally {
    isLoading.value = false
  }
}

// 2. 提交请假申请
const submitLeave = async () => {
  if (!leaveForm.value.reason.trim()) {
    ElMessage.warning('请假事由不能为空哦')
    return
  }

  isSubmitting.value = true
  try {
    // 调用的也是我们第二天在 Django 里写好的那个 POST 接口
    await axios.post('http://localhost:8000/api/leaves/', {
      student_id: studentId.value,
      reason: leaveForm.value.reason
    })
    
    ElMessage.success('请假申请提交成功！请等待老师审批。')
    leaveForm.value.reason = '' // 清空表单
    fetchLeaves() // 重新拉取最新记录
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '提交失败，请检查网络')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.leave-container { padding: 20px; max-width: 900px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.apply-section { margin-bottom: 20px; border-color: #ebeef5; }
.history-section { border-color: #ebeef5; }
</style>