// routes/admin.js
const express = require('express');
const router = express.Router();
const { pool } = require('../db');

router.post('/admin/login', async (req, res) => {
  const { account, password } = req.body;

  try {
    // 基础验证
    if (!account || !password) {
      return res.status(400).json({
        status: 'error',
        code: 'MISSING_FIELDS',
        message: '账号和密码不能为空'
      });
    }

    // 查询管理员信息（明文比对）
    const [admins] = await pool.query(
      `SELECT password 
       FROM admin_account 
       WHERE account = ?`,  // 直接查询明文账号
      [account]
    );

    if (admins.length === 0) {
      return res.status(401).json({
        status: 'error',
        code: 'INVALID_CREDENTIALS',
        message: '账号或密码错误'
      });
    }

    // 直接比对明文密码
    const admin = admins[0];
    if (password !== admin.password) {
      return res.status(401).json({
        status: 'error',
        code: 'INVALID_CREDENTIALS',
        message: '账号或密码错误'
      });
    }

    // 登录成功
    res.json({
      status: 'success',
      data: {
        redirectUrl: '../lending end/管理员排班后台.html'
      }
    });

  } catch (err) {
    console.error('管理员登录失败:', {
      error: err.message,
      stack: err.stack,
      requestBody: { account: account?.slice(0,3) + '****' }
    });
    
    res.status(500).json({
      status: 'error',
      code: 'SERVER_ERROR',
      message: '服务暂时不可用'
    });
  }
});

module.exports = router;