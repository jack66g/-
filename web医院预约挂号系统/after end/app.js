const path = require('path');
require('dotenv').config();
const express = require('express');
const helmet = require('helmet');

const cors = require('cors');


// 添加请求体大小限制（在express.json()之前）
const app = express();
app.use(express.json({ limit: '10mb' })); // 替换原来的express.json()
app.use(express.urlencoded({ limit: '10mb', extended: true })); // 新增


const fileUpload = require('express-fileupload'); // 新增文件上传模块



// 中间件配置
// 注意：关闭CSP因为前端HTML使用内联脚本，生产环境应配置合适的CSP策略
app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false
}));
// 允许所有来源（生产环境应限制）
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
}));
app.use(express.json());
app.use(fileUpload({  // 文件上传中间件
  limits: { fileSize: 5 * 1024 * 1024 }, // 限制5MB
  abortOnLimit: true,
  responseOnLimit: '文件大小超过5MB限制'
}));

// 托管前端静态页面（leading end 目录与 after end 同级）
app.use(express.static(path.join(__dirname, '..', 'leading end')));

// 数据库连接
const { pool } = require('./db');

// 路由配置
app.use('/api', require('./mianexe/Register'));
app.use('/api', require('./mianexe/login')); // 新增登录路由
app.use('/api', require('./mianexe/forget'));
app.use('/api', require('./mianexe/tool'));
app.use('/api', require('./mianexe/control')); // 新增医生管理路由
app.use('/api', require('./mianexe/endocrine'));
app.use('/api', require('./mianexe/human'));
app.use('/api', require('./mianexe/face')); // 新增人脸路由

// 健康检查接口
app.get('/health', (req, res) => {
  res.json({ 
    status: 'running',
    dbStatus: 'connected'
  });
});

// 全局错误处理
app.use((err, req, res, next) => {
  console.error('[GLOBAL ERROR]', err);
  res.status(500).json({
    status: 'error',
    code: 'INTERNAL_ERROR',
    message: '服务器内部错误'
  });
});

// 启动服务
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`
  ===================================
  🏥 医院预约挂号系统后端已启动
  📡 后端API：http://localhost:${PORT}/api
  🖥️ 前端界面：http://localhost:${PORT}/医院主界面.html
  📦 数据库：${process.env.DB_USER}@${process.env.DB_HOST}:${process.env.DB_PORT}
  ===================================
  `);
});
