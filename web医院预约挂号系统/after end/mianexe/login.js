const express = require('express');
const crypto = require('crypto');
const router = express.Router();
const { pool } = require('../db');

// 安全配置验证
if (!process.env.AES_KEY || Buffer.from(process.env.AES_KEY, 'hex').length !== 32) {
  throw new Error('无效的AES_KEY配置，需要64字符的HEX字符串');
}

const AES_KEY = Buffer.from(process.env.AES_KEY, 'hex');
const PBKDF2_ITERATIONS = 10000; // 新增此行

// 统一响应格式
const responseWrapper = (res, code, data) => {
  const status = code >= 200 && code < 300 ? 'success' : 'error';
  return res.status(code).json({ status, ...data });
};

router.post('/login', async (req, res) => {
  const { phone, password } = req.body;

  try {
    // 基本验证
    if (!phone || !password) {
      return responseWrapper(res, 400, {
        code: 'MISSING_FIELDS',
        message: '手机号和密码不能为空'
      });
    }

    // 查询用户信息（参数化查询）
    const [users] = await pool.query(
      `SELECT password, salt, encryption_iv 
      FROM patient_info 
      WHERE phone = AES_ENCRYPT(?, UNHEX(?))`,
      [phone, process.env.AES_KEY]
    );

    // 用户不存在
    if (users.length === 0) {
      return responseWrapper(res, 401, {
        code: 'INVALID_CREDENTIALS',
        message: '手机号或密码错误'
      });
    }

    // 获取用户数据
    const user = users[0];
    const storedHash = user.password;
    const salt = user.salt;
    const iv = user.encryption_iv;

    // 密码验证
    const inputHash = crypto.pbkdf2Sync(
      password,
      salt,
      PBKDF2_ITERATIONS, // 使用定义的常量
      64,
      'sha512'
    );

    // 密码比对（安全的时间恒定比较）
    if (!crypto.timingSafeEqual(inputHash, storedHash)) {
      return responseWrapper(res, 401, {
        code: 'INVALID_CREDENTIALS',
        message: '手机号或密码错误'
      });
    }

    // 登录成功
    return responseWrapper(res, 200, {
      data: {
        redirectUrl: '../leading end/人脸识别.html'
      }
    });

  } catch (err) {
    console.error(`登录失败:`, {
      error: err.message,
      stack: err.stack,
      requestBody: { phone: phone?.slice(0,3) + '****' }
    });

    return responseWrapper(res, 500, {
      code: 'SERVER_ERROR',
      message: '服务暂时不可用，请稍后重试'
    });
  }
});

module.exports = router;