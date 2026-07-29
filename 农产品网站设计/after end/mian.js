const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const cors = require('cors');
require('dotenv').config();

const app = express();

// ====================
// 中间件配置（与密码重置服务保持统一）
// ====================
app.use(cors({
    origin: '*', // 临时允许所有来源（仅限调试）
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true
}));
app.use(express.json());

// ====================
// 数据库配置（统一环境变量命名）
// ====================
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '3124456607q',
  database: process.env.DB_NAME || 'registration_db',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// ====================
// 登录接口（增强版）
// ====================
app.post('/api/login', async (req, res) => {
  const { username: phone, password } = req.body;
  const errors = [];

  try {
    // 输入验证
    if (!phone) errors.push('手机号不能为空');
    if (!password) errors.push('密码不能为空');
    if (errors.length > 0) return res.status(400).json({ errors });

    if (!/^1[3-9]\d{9}$/.test(phone)) {
      return res.status(400).json({ errors: ['手机号格式错误'] });
    }

    // 用户查询
    const [users] = await pool.query(
      'SELECT id, password_hash FROM users WHERE phone = ?',
      [phone]
    );

    if (users.length === 0) {
      return res.status(404).json({ errors: ['用户不存在'] });
    }

    // 密码验证
    const user = users[0];
    const isValid = await bcrypt.compare(password, user.password_hash);
    
    if (!isValid) {
      return res.status(401).json({ errors: ['密码错误'] });
    }


    res.status(200).json({
      success: true,
      message: '登录成功',
      user: {
        id: user.id,
        phone: phone
      },
    });

  } catch (error) {
    console.error('登录错误:', error);
    res.status(500).json({
      errors: ['服务器内部错误'],
      debug: process.env.NODE_ENV === 'development' ? error.message : null
    });
  }
});

// ====================
// 服务启动
// ====================
const PORT = process.env.LOGIN_PORT || 3002;
app.listen(PORT, () => {
  console.log(`🔐 登录服务运行在：http://localhost:${PORT}`);
});
