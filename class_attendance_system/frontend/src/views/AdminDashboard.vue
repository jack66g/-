<template>
  <div class="admin-layout">
    <el-container>
      <el-header class="header">
        <div class="logo">管理后台 - 账号与班级运维</div>
        <el-button type="danger" @click="logout">退出登录</el-button>
      </el-header>
      
      <el-main>
        <el-row :gutter="20" class="stat-row">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>学生总数</template>
              <div class="stat-num">{{ studentCount }} 人</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>教师总数</template>
              <div class="stat-num">{{ teacherCount }} 人</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>班级总数</template>
              <div class="stat-num">{{ classCount }} 个</div>
            </el-card>
          </el-col>
        </el-row>

        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <span>账号列表</span>
              <el-button type="primary" @click="dialogVisible = true">新增账号</el-button>
            </div>
          </template>
          
          <el-table :data="userList" border style="width: 100%" v-loading="loadingTable">
            <el-table-column prop="username" label="用户名/学号" width="180" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.role === 'teacher' ? 'warning' : 'success'">
                  {{ scope.row.role === 'teacher' ? '教师' : '学生' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="class_name" label="所属班级" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>

    <el-dialog v-model="dialogVisible" title="新增用户信息" width="30%">
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" placeholder="请输入学号或工号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="userForm.password" type="password" placeholder="设置初始密码" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%;">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="班级名称" v-if="userForm.role === 'student'">
          <el-input v-model="userForm.class_name" placeholder="例如：软件工程1班" />
        </el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">确认创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const dialogVisible = ref(false)
const userList = ref([])
const loadingTable = ref(false)
const submitLoading = ref(false)

const userForm = ref({ username: '', password: '', role: 'student', class_name: '' })

// 简单的计算属性，用来动态展示上面的统计卡片数据
const studentCount = computed(() => userList.value.filter(u => u.role === 'student').length)
const teacherCount = computed(() => userList.value.filter(u => u.role === 'teacher').length)
// 利用 Set 去重，计算一共有多少个不同的班级
const classCount = computed(() => {
  const classes = userList.value.filter(u => u.role === 'student').map(u => u.class_name)
  return new Set(classes).size
})

// 页面挂载时
onMounted(() => {
  const role = localStorage.getItem('userRole')
  const username = localStorage.getItem('username')
  
  // 简易权限拦截
  if (role !== 'teacher' && username !== 'admin') {
    ElMessage.error('权限不足，请使用管理员账号登录')
    router.push('/login')
    return
  }
  
  fetchUsers()
})

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

// 1. 拉取真实数据
const fetchUsers = async () => {
  loadingTable.value = true
  try {
    const res = await axios.get('http://localhost:8000/api/admin/users/')
    userList.value = res.data
  } catch (error) {
    ElMessage.error('获取账号列表失败，请检查后端服务')
  } finally {
    loadingTable.value = false
  }
}

// 2. 提交表单建人
const submitForm = async () => {
  if (!userForm.value.username || !userForm.value.password) {
    ElMessage.warning('账号和密码是必填项哦')
    return
  }
  
  submitLoading.value = true
  try {
    await axios.post('http://localhost:8000/api/admin/users/', userForm.value)
    ElMessage.success('账号创建成功！')
    dialogVisible.value = false
    
    // 清空表单，为下次做准备
    userForm.value = { username: '', password: '', role: 'student', class_name: '' }
    
    // 重新拉取数据刷新表格
    fetchUsers() 
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '创建失败')
  } finally {
    submitLoading.value = false
  }
}

// 3. 删除操作
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要彻底删除账号 [${row.username}] 吗？这会同时清除其相关数据！`, '高能预警', { 
    type: 'warning',
    confirmButtonText: '狠心删除',
    cancelButtonText: '再想想'
  }).then(async () => {
    try {
      await axios.delete('http://localhost:8000/api/admin/users/', { data: { id: row.id } })
      ElMessage.success('目标已清除')
      fetchUsers()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}
</script>

<style scoped>
.header { background: #409eff; color: white; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
.logo { font-size: 20px; font-weight: bold; }
.stat-row { margin-bottom: 20px; }
.stat-num { font-size: 24px; font-weight: bold; color: #409eff; text-align: center; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.table-card { margin-top: 20px; }
</style>