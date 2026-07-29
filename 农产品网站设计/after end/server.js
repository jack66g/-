// server.js
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
  connectionLimit: 10,
  queueLimit: 0
});

// 数据库连接测试
async function testDatabaseConnection() {
  let connection;
  try {
    connection = await pool.getConnection();
    console.log('✅ 数据库连接成功');
    await connection.ping();
  } catch (error) {
    console.error('❌ 数据库连接失败:', error.message);
    process.exit(1);
  } finally {
    if (connection) connection.release();
  }
}

// 健康检查接口
app.get('/health', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT 1 + 1 AS result');
    res.status(200).json({
      status: 'ok',
      dbStatus: rows[0].result === 2 ? 'healthy' : 'unhealthy'
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      dbStatus: 'unavailable'
    });
  }
});

// 注册接口（带事务和输入验证）
app.post('/api/register', async (req, res) => {
  const { phone, password, confirmPassword } = req.body;

  // 输入验证
  const errors = [];
  if (!phone) errors.push('手机号不能为空');
  if (!password) errors.push('密码不能为空');
  if (!confirmPassword) errors.push('确认密码不能为空');
  
  if (errors.length > 0) {
    return res.status(400).json({ errors });
  }

  if (!/^1[3-9]\d{9}$/.test(phone)) {
    return res.status(400).json({ errors: ['请输入有效的中国大陆手机号'] });
  }

  if (password.length < 8 || password.length > 16) {
    return res.status(400).json({ errors: ['密码长度需为8-16位'] });
  }

  if (password !== confirmPassword) {
    return res.status(400).json({ errors: ['两次输入的密码不一致'] });
  }

  let connection;
  try {
    connection = await pool.getConnection();
    await connection.beginTransaction();

    // 检查手机号是否存在（行级锁）
    const [users] = await connection.query(
      `SELECT phone FROM users 
       WHERE phone = ? FOR UPDATE`,
      [phone]
    );

    if (users.length > 0) {
      await connection.rollback();
      return res.status(409).json({ errors: ['手机号已被注册'] });
    }

    // 密码加密
    const salt = await bcrypt.genSalt(12);
    const hashedPassword = await bcrypt.hash(password, salt);

    // 插入用户数据
    const [result] = await connection.query(
      `INSERT INTO users (phone, password_hash)
       VALUES (?, ?)`,
      [phone, hashedPassword]
    );

    await connection.commit();
    
    res.status(201).json({
      message: '注册成功',
      data: {
        userId: result.insertId,
        phone: phone,
        createdAt: new Date().toISOString()
      }
    });

  } catch (error) {
    if (connection) await connection.rollback();
    console.error('注册错误:', error.stack);
    res.status(500).json({ 
      errors: ['服务器内部错误'],
      debug: process.env.NODE_ENV === 'development' ? error.message : null
    });
  } finally {
    if (connection) connection.release();
  }
});

// 启动服务
async function startServer() {
  try {
    await testDatabaseConnection();
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
      console.log(`🚀 服务已启动: http://localhost:${PORT}`);
      console.log(`📊 健康检查: http://localhost:${PORT}/health`);
    });
  } catch (error) {
    console.error('❌ 服务启动失败:', error.message);
    process.exit(1);
  }
}

// 优雅关闭
process.on('SIGINT', async () => {
  console.log('\n🛑 正在关闭服务...');
  await pool.end();
  process.exit(0);
});

// 启动应用
startServer();