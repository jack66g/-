import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 1. 创建唯一实例
const app = createApp(App)

// 2. 依次挂载所有插件
app.use(router)
app.use(ElementPlus)

// 3. 把这个配置好的完整实例挂载到页面上
app.mount('#app')