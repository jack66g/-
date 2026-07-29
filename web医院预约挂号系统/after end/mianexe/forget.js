// mainexe/password.js
const express = require('express');
const crypto = require('crypto');
const router = express.Router();
const { pool } = require('../db');

const PBKDF2_ITERATIONS = 10000;

router.post('/reset-password', async (req, res) => {
    const { phone, newPassword } = req.body;

    try {
        // 验证输入
        if (!phone || !newPassword) {
            return res.status(400).json({
                status: 'error',
                code: 'MISSING_FIELDS',
                message: '手机号和新密码不能为空'
            });
        }

        // 查询用户
        const [users] = await pool.query(
            `SELECT patient_id, salt FROM patient_info 
            WHERE phone = AES_ENCRYPT(?, UNHEX(?))`,
            [phone, process.env.AES_KEY]
        );

        if (users.length === 0) {
            return res.status(404).json({
                status: 'error',
                code: 'USER_NOT_FOUND',
                message: '该手机号未注册'
            });
        }

        // 生成新密码哈希
        const salt = users[0].salt;
        const hashedPassword = crypto.pbkdf2Sync(
            newPassword,
            salt,
            PBKDF2_ITERATIONS,
            64,
            'sha512'
        );

        // 更新数据库
        await pool.query(
            `UPDATE patient_info 
            SET password = ?
            WHERE phone = AES_ENCRYPT(?, UNHEX(?))`,
            [hashedPassword, phone, process.env.AES_KEY]
        );

        res.json({
            status: 'success',
            message: '密码已成功重置'
        });

    } catch (err) {
        console.error('密码重置失败:', err);
        res.status(500).json({
            status: 'error',
            code: 'SERVER_ERROR',
            message: '服务暂时不可用'
        });
    }
});

module.exports = router;