<template>
  <div class="register-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2><el-icon><Camera /></el-icon> 人脸信息自动化录入</h2>
          <el-tag type="success">当前绑定学号：{{ studentId }} ({{ username }})</el-tag>
        </div>
      </template>

      <div class="camera-section">
        <div class="video-wrapper">
          <video ref="videoElement" autoplay playsinline></video>
          <div class="scan-line" v-if="isCapturing"></div>
        </div>
        <canvas ref="canvasElement" style="display: none;"></canvas>
      </div>

      <div class="status-section">
        <h3 :class="{'text-active': isCapturing || isUploading}">{{ statusMessage }}</h3>
        
        <el-progress 
          :text-inside="true" 
          :stroke-width="24" 
          :percentage="progressPercentage" 
          :status="progressStatus"
          class="progress-bar"
        />
      </div>

      <div class="controls">
        <el-button 
          type="primary" 
          size="large" 
          @click="startCapture" 
          :disabled="isCapturing || isUploading || isSuccess"
        >
          {{ isUploading ? '正在打包上传...' : '开始自动连拍' }}
        </el-button>
        <el-button size="large" @click="goBack" :disabled="isCapturing">
          返回控制台
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

// DOM 引用
const videoElement = ref(null)
const canvasElement = ref(null)

// 用户状态
const studentId = ref('')
const username = ref('')

// 流程控制状态
const isCapturing = ref(false)
const isUploading = ref(false)
const isSuccess = ref(false)
const capturedCount = ref(0)
const totalFrames = 30 // 连拍 30 张
const imagesArray = [] // 存放 base64 图片的数组
let mediaStream = null
let captureInterval = null

// 动态计算进度条百分比
const progressPercentage = computed(() => {
  return Math.floor((capturedCount.value / totalFrames) * 100)
})

// 进度条颜色状态
const progressStatus = computed(() => {
  if (isSuccess.value) return 'success'
  if (isUploading.value) return 'warning'
  return ''
})

// 动态提示文字
const statusMessage = computed(() => {
  if (isSuccess.value) return '录入成功！AI模型已更新完毕。'
  if (isUploading.value) return '采集完毕，正在上传并训练模型，请稍候...'
  if (isCapturing.value) return `正在提取面部特征... (${capturedCount.value}/${totalFrames})`
  return '请正对摄像头，摘下口罩/墨镜，保证光线充足。'
})

// 1. 初始化摄像头
const initCamera = async () => {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 640, height: 480, facingMode: 'user' } 
    })
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
    }
  } catch (err) {
    ElMessage.error('无法访问摄像头，请检查浏览器权限！')
    console.error(err)
  }
}

// 2. 开始连拍核心逻辑
const startCapture = () => {
  if (!videoElement.value || !canvasElement.value) return

  // 重置状态
  imagesArray.length = 0
  capturedCount.value = 0
  isCapturing.value = true
  isSuccess.value = false

  const video = videoElement.value
  const canvas = canvasElement.value
  const context = canvas.getContext('2d')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  // 设置定时器，每 100 毫秒截一张图
  captureInterval = setInterval(() => {
    // 画图并转成 base64
    context.drawImage(video, 0, 0, canvas.width, canvas.height)
    const base64Image = canvas.toDataURL('image/jpeg', 0.8)
    imagesArray.push(base64Image)
    
    capturedCount.value++

    // 拍够 30 张，停手，准备上传
    if (capturedCount.value >= totalFrames) {
      clearInterval(captureInterval)
      isCapturing.value = false
      uploadPhotos()
    }
  }, 100)
}

// 3. 上传给后端
const uploadPhotos = async () => {
  isUploading.value = true
  try {
    // 注意：这里的接口咱们还没写，所以目前点到这里会报 404
    await axios.post('http://localhost:8000/api/face/register/', {
      student_id: studentId.value,
      images: imagesArray
    })
    isSuccess.value = true
    ElMessage.success('录入成功！')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '上传失败，后端接口暂未联通')
  } finally {
    isUploading.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/dashboard')
}

// 生命周期
onMounted(() => {
  // 从本地取出信息
  studentId.value = localStorage.getItem('studentId')
  username.value = localStorage.getItem('username')
  
  if (!studentId.value) {
    ElMessage.warning('未能获取您的学号，请重新登录')
    router.push('/login')
    return
  }
  
  initCamera()
})

onBeforeUnmount(() => {
  // 离开页面前清理定时器和摄像头资源
  if (captureInterval) clearInterval(captureInterval)
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 20px;
}
.box-card {
  width: 100%;
  max-width: 600px;
  text-align: center;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.camera-section {
  position: relative;
  margin: 20px auto;
  width: 480px;
  height: 360px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
/* 录入时的扫描动画 */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: #67c23a;
  box-shadow: 0 0 10px #67c23a;
  animation: scan 1.5s infinite linear;
}
@keyframes scan {
  0% { top: 0; }
  50% { top: 100%; }
  100% { top: 0; }
}
.status-section {
  margin: 20px 0;
}
.text-active {
  color: #409eff;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.progress-bar {
  margin-top: 15px;
}
.controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}
</style>