<template>
  <div class="camera-page">
    <h2>人脸识别签到</h2>
    
    <div class="video-container">
      <video ref="videoElement" autoplay playsinline></video>
      <canvas ref="canvasElement" style="display: none;"></canvas>
    </div>

    <div class="controls">
      <button @click="takeSnapshot" :disabled="isRecognizing" class="scan-btn">
        {{ isRecognizing ? '识别中...' : '点击打卡' }}
      </button>
      <button @click="$router.push('/dashboard')" class="back-btn">返回面板</button>
    </div>

    <div v-if="resultMessage" :class="['result-msg', resultType]">
      {{ resultMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const videoElement = ref(null)
const canvasElement = ref(null)
const isRecognizing = ref(false)
const resultMessage = ref('')
const resultType = ref('') // 'success' or 'error'
let mediaStream = null

// 初始化摄像头
const initCamera = async () => {
  try {
    // 请求摄像头权限并获取视频流
    mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 640, height: 480, facingMode: 'user' } 
    })
    // 将视频流赋给 video 标签
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
    }
  } catch (err) {
    resultMessage.value = '无法访问摄像头，请检查权限！'
    resultType.value = 'error'
    console.error(err)
  }
}

// 抓拍并发送给后端识别
const takeSnapshot = async () => {
  if (!videoElement.value || !canvasElement.value) return

  isRecognizing.value = true
  resultMessage.value = '正在提取面部特征...'
  resultType.value = ''

  const video = videoElement.value
  const canvas = canvasElement.value
  const context = canvas.getContext('2d')

  // 设置画布尺寸与视频一致
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  // 将当前视频帧画到 canvas 上
  context.drawImage(video, 0, 0, canvas.width, canvas.height)

  // 抽成 Base64 字符串 (JPEG 格式，0.8 质量压缩)
  const base64Image = canvas.toDataURL('image/jpeg', 0.8)

  try {
    const response = await axios.post('http://localhost:8000/api/recognize/', {
      image: base64Image
    })
    resultMessage.value = response.data.message
    resultType.value = 'success'
  } catch (error) {
    resultMessage.value = error.response?.data?.error || '识别服务异常'
    resultType.value = 'error'
  } finally {
    isRecognizing.value = false
  }
}

// 生命周期钩子：挂载时开摄像头，卸载时关摄像头
onMounted(() => {
  initCamera()
})

onBeforeUnmount(() => {
  // 离开页面时一定要释放硬件资源
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.camera-page { text-align: center; padding: 20px; }
.video-container { margin: 20px auto; max-width: 640px; border: 4px solid #333; border-radius: 8px; overflow: hidden; background: #000; }
video { width: 100%; display: block; }
.controls button { padding: 12px 24px; margin: 0 10px; font-size: 16px; cursor: pointer; border: none; border-radius: 4px; }
.scan-btn { background: #67c23a; color: white; }
.scan-btn:disabled { background: #b3e19d; }
.back-btn { background: #909399; color: white; }
.result-msg { margin-top: 20px; padding: 15px; font-size: 18px; font-weight: bold; border-radius: 4px; display: inline-block; }
.success { background: #f0f9eb; color: #67c23a; border: 1px solid #e1f3d8; }
.error { background: #fef0f0; color: #f56c6c; border: 1px solid #fde2e2; }
</style>