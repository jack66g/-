const express = require('express');
const mysql = require('mysql2/promise');
const crypto = require('crypto');
const cors = require('cors');
require('dotenv').config();

const app = express();

// 中间件配置
app.use(cors({
    origin: process.env.CORS_ORIGIN || '*',
    methods: ['POST'],
    allowedHeaders: ['Content-Type'],
    credentials: true
}));
app.use(express.json());

// 数据库连接池
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '3124456607q',
  database: process.env.DB_NAME || 'registration_db',
  waitForConnections: true,
  connectionLimit: 10
});

// SHA-256加密函数
const sha256 = (text) => {
  return crypto
    .createHash('sha256')
    .update(text)
    .digest('hex');
};

// 管理员登录接口
app.post('/api/admin/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    // 输入验证
    const errors = [];
    if (!username) errors.push('用户名不能为空');
    if (!password) errors.push('密码不能为空');
    
    if (errors.length > 0) {
      return res.status(400).json({ 
        success: false,
        errors 
      });
    }

    // 计算密码哈希
    const hashedPassword = sha256(password);

    // 查询管理员
    const [results] = await pool.query(
      'SELECT id, username FROM rootfirst WHERE username = ? AND password_hash = ?',
      [username, hashedPassword]
    );

    if (results.length > 0) {
      res.status(200).json({
        success: true,
        message: '登录成功',
        user: results[0]
      });
    } else {
      res.status(401).json({
        success: false,
        errors: ['用户名或密码错误']
      });
    }

  } catch (error) {
    console.error('登录失败:', error);
    res.status(500).json({
      success: false,
      errors: ['服务器内部错误'],
      debug: process.env.NODE_ENV === 'development' ? error.message : null
    });
  }
});

// 启动服务
const PORT = process.env.ADMIN_PORT || 3005;
app.listen(PORT, () => {
  console.log(`🔑 管理员认证服务运行在：http://localhost:${PORT}`);
});