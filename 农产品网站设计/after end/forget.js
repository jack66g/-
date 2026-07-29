const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
const cors = require('cors');
require('dotenv').config();

const app = express();

// 中间件配置
app.use(cors({
    origin: '*', // 临时允许所有来源（仅限调试）
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
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

// 密码重置接口
app.post('/api/reset-password', async (req, res) => {
  const { phone, newPassword, confirmPassword } = req.body;

  try {
    // 验证输入
    const errors = [];
    if (!phone) errors.push('手机号不能为空');
    if (!newPassword) errors.push('新密码不能为空');
    if (!confirmPassword) errors.push('确认密码不能为空');
    
    if (errors.length > 0) {
      return res.status(400).json({ errors });
    }

    if (!/^1[3-9]\d{9}$/.test(phone)) {
      return res.status(400).json({ errors: ['手机号格式错误'] });
    }

    if (newPassword !== confirmPassword) {
      return res.status(400).json({ errors: ['两次密码不一致'] });
    }

    // 查询用户
    const [users] = await pool.query(
      'SELECT id FROM users WHERE phone = ?',
      [phone]
    );

    if (users.length === 0) {
      return res.status(404).json({ errors: ['该手机号未注册'] });
    }

    // 更新密码
    const salt = await bcrypt.genSalt(12);
    const hashedPassword = await bcrypt.hash(newPassword, salt);

    await pool.query(
      'UPDATE users SET password_hash = ? WHERE phone = ?',
      [hashedPassword, phone]
    );

    res.status(200).json({ 
      message: '密码重置成功',
      success: true
    });

  } catch (error) {
    console.error('密码重置失败:', error);
    res.status(500).json({ 
      errors: ['服务器内部错误'],
      debug: process.env.NODE_ENV === 'development' ? error.message : null
    });
  }
});

// 启动服务
const PORT = process.env.RESET_PORT || 3001; // 使用独立环境变量和使用不同端口
app.listen(PORT, () => {
  console.log(`🔑 密码重置服务运行在：http://localhost:${PORT}`);
});