<template>
  <div class="dashboard-wrapper">
    <div class="bg-shape shape1"></div>
    <div class="bg-shape shape2"></div>
    <div class="bg-shape shape3"></div>

    <div class="glass-container">
      <div class="header">
        <div class="user-info">
          <h2><el-icon><Monitor /></el-icon> 班级智慧终端</h2>
          <p class="welcome-text">系统识别: <strong>{{ username }}</strong> | 接入身份: <el-tag size="small" effect="plain">{{ role === 'teacher' ? '教职人员' : '在校学生' }}</el-tag></p>
        </div>
        <el-button color="#ff4d4f" plain round @click="logout" class="logout-btn">
          安全退出
        </el-button>
      </div>

      <div class="actions-grid">
        
        <div class="glass-card" :class="{ 'locked-card': role === 'student' }">
          <div class="card-icon">📊</div>
          <h3>教务指挥中心</h3>
          
          <template v-if="role === 'teacher' || role === 'admin'">
            <p>管理全班考勤动态，处理审批事务并开启点名系统</p>
            <div class="btn-group-vertical">
              <el-button type="primary" size="large" @click="$router.push('/teacher-stats')" class="cyber-btn">
                进入数据大盘
              </el-button>
              <el-button type="warning" plain size="large" @click="$router.push('/camera')" class="cyber-btn">
                开启人脸点名
              </el-button>
            </div>
          </template>

          <template v-else>
            <p class="locked-text">仅限教职人员访问</p>
            <div class="lock-overlay">
              <el-icon class="lock-icon"><Lock /></el-icon>
            </div>
          </template>
        </div>

        <div class="glass-card" :class="{ 'locked-card': role === 'teacher' }">
          <div class="card-icon">🎓</div>
          <h3>学生个人中心</h3>
          
          <template v-if="role === 'student'">
            <p>维护个人人脸数据，完成课堂签到与请假申请</p>
            <div class="btn-group-vertical">
              <el-button type="success" @click="$router.push('/register')" class="cyber-btn">
                首次使用：录入人脸
              </el-button>
              <el-button type="primary" @click="$router.push('/camera')" class="cyber-btn">
                日常课堂打卡
              </el-button>
              <el-button type="warning" @click="$router.push('/leave')" class="cyber-btn">
                提交请假申请
              </el-button>
            </div>
          </template>

          <template v-else>
            <p class="locked-text">非学生账号 无法进行业务操作</p>
            <div class="lock-overlay">
              <el-icon class="lock-icon"><Lock /></el-icon>
            </div>
          </template>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, Lock } from '@element-plus/icons-vue' 

const router = useRouter()
const role = ref('')
const username = ref('')

onMounted(() => {
  role.value = localStorage.getItem('userRole')
  username.value = localStorage.getItem('username')
  
  if (!role.value) {
    router.push('/login')
  }
})

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
/* 1. 全局包裹层：确保渐变背景固定 */
.dashboard-wrapper {
  position: relative;
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  /* 使用 fixed 确保滚动时背景色不间断 */
  background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%) fixed;
  overflow-x: hidden;
  padding: 20px;
  box-sizing: border-box;
  font-family: 'Helvetica Neue', Helvetica, sans-serif;
}

/* 2. 背景形状：改为 fixed 定位，使其覆盖整个视口 */
.bg-shape {
  position: fixed; /* 关键：固定在屏幕，不随容器滚动 */
  filter: blur(100px);
  z-index: 0;
  pointer-events: none; /* 确保不阻挡点击事件 */
  animation: float 15s infinite ease-in-out;
}

/* 增大形状尺寸并调整位置，实现“铺开”效果 */
.shape1 { 
  width: 50vw; height: 50vw; 
  background: rgba(255, 154, 158, 0.6); 
  top: -10vh; left: -10vw; 
}
.shape2 { 
  width: 60vw; height: 60vw; 
  background: rgba(254, 207, 239, 0.6); 
  bottom: -15vh; right: -10vw; 
}
.shape3 { 
  width: 40vw; height: 40vw; 
  background: rgba(161, 196, 253, 0.6); 
  top: 30vh; left: 40vw; 
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -20px); }
}

/* 3. 毛玻璃容器样式保持不变 */
.glass-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 1000px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 30px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 25px;
  margin-bottom: 35px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.glass-card {
  position: relative;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  padding: 40px 25px;
  text-align: center;
  transition: transform 0.3s;
  display: flex;
  flex-direction: column;
}

.glass-card:hover:not(.locked-card) {
  transform: translateY(-10px);
}

.card-icon { font-size: 50px; margin-bottom: 15px; }
.glass-card h3 { color: #2c3e50; font-size: 22px; margin-bottom: 15px; }
.glass-card p { color: #555; font-size: 15px; margin-bottom: 30px; min-height: 45px; }

.btn-group-vertical {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.cyber-btn {
  margin-left: 0 !important;
  font-weight: bold;
  letter-spacing: 1px;
  border-radius: 12px !important;
}

.locked-card {
  background: rgba(0, 0, 0, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.3);
  filter: grayscale(0.8);
}

.locked-text {
  color: #888 !important;
  font-style: italic;
}

.lock-overlay {
  margin-top: 10px;
}

.lock-icon {
  font-size: 30px;
  color: #999;
}

@media (max-width: 768px) {
  .actions-grid { grid-template-columns: 1fr; }
}
</style>