const express = require('express');
const crypto = require('crypto');
const router = express.Router();
const { pool } = require('../db');

// 安全配置验证
if (!process.env.AES_KEY || Buffer.from(process.env.AES_KEY, 'hex').length !== 32) {
  throw new Error('无效的AES_KEY配置，需要64字符的HEX字符串');
}

const AES_KEY = Buffer.from(process.env.AES_KEY, 'hex');
const PBKDF2_ITERATIONS = 10000;

// 统一响应格式
const responseWrapper = (res, code, data) => {
  const status = code >= 200 && code < 300 ? 'success' : 'error';
  return res.status(code).json({ status, ...data });
};

// 注册接口
router.post('/register', async (req, res) => {
  const { phone, password, name, gender, age, idCard, medicalCard, address } = req.body;

  try {
    // 输入验证
    const validations = [
      // 原有验证...
      // 新增验证
      {
        check: !name || !gender || !age || !idCard || !medicalCard || !address,
        code: 400,
        error: { code: 'MISSING_FIELDS', message: '所有字段不能为空' }
      },
      {
        check: !/^[\u4e00-\u9fa5]{1,10}$/.test(name),
        code: 400,
        error: { code: 'INVALID_NAME', message: '姓名必须为1-10个汉字' }
      },
      {
        check: !['男', '女'].includes(gender),
        code: 400,
        error: { code: 'INVALID_GENDER', message: '无效性别' }
      },
      {
        check: !/^\d{17}[\dX]$/i.test(idCard),
        code: 400,
        error: { code: 'INVALID_ID_CARD', message: '身份证格式不正确' }
      },
      {
        check: !/^\d{16}$/.test(medicalCard),
        code: 400,
        error: { code: 'INVALID_MEDICAL_CARD', message: '医保卡号必须为16位数字' }
      }
    ];

    for (const val of validations) {
      if (val.check) return responseWrapper(res, val.code, val.error);
    }

    // 加密处理
    const iv = crypto.randomBytes(16);
    const salt = crypto.randomBytes(32);
    const hashedPassword = crypto.pbkdf2Sync(password, salt, PBKDF2_ITERATIONS, 64, 'sha512');

    // 检查手机号是否已存在
    const [existing] = await pool.query(
      `SELECT patient_id FROM patient_info 
      WHERE phone = AES_ENCRYPT(?, UNHEX(?))`,
      [phone, process.env.AES_KEY]
    );

    if (existing.length > 0) {
      return responseWrapper(res, 409, { code: 'PHONE_EXISTS', message: '该手机号已注册' });
    }

    // 插入数据库
    await pool.query(
      `INSERT INTO patient_info 
      (name, gender, age, phone, password, id_card, address, medical_card, encryption_iv, salt)
      VALUES (
        AES_ENCRYPT(?, UNHEX(?)), 
        AES_ENCRYPT(?, UNHEX(?)), 
        AES_ENCRYPT(?, UNHEX(?)), 
        AES_ENCRYPT(?, UNHEX(?)), 
        ?, 
        AES_ENCRYPT(?, UNHEX(?)), 
        AES_ENCRYPT(?, UNHEX(?)), 
        AES_ENCRYPT(?, UNHEX(?)), 
        ?, 
        ?
      )`,
      [
        name, process.env.AES_KEY,
        gender, process.env.AES_KEY,
        age.toString(), process.env.AES_KEY,
        phone, process.env.AES_KEY,
        hashedPassword,
        idCard, process.env.AES_KEY,
        address, process.env.AES_KEY,
        medicalCard, process.env.AES_KEY,
        iv, salt
      ]
    );

    return responseWrapper(res, 201, {
      message: '注册成功',
      data: { maskedPhone: `${phone.slice(0,3)}****${phone.slice(7)}` }
    });

  } catch (err) {
    console.error(`注册失败:`, err);
    const statusCode = err.code === 'ER_DUP_ENTRY' ? 409 : 500;
    return responseWrapper(res, statusCode, {
      code: 'SERVER_ERROR',
      message: '服务暂时不可用，请稍后重试'
    });
  }
});

module.exports = router;