// 文件路径: src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
// 引入 Vant 及样式
import Vant from 'vant';
import 'vant/lib/index.css';

const app = createApp(App);
app.use(router);
app.use(Vant); // 为了快，我们全局全量引入 Vant
app.mount('#app');