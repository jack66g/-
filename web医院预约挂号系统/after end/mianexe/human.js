const express = require('express');
const router = express.Router();
const { pool } = require('../db');

// 检查挂号状态（带事务锁定）
router.post('/cancel/check', async (req, res) => {
  const { idCard } = req.body;
  const connection = await pool.getConnection();
  
  try {
    await connection.beginTransaction();

    // 使用SELECT FOR UPDATE锁定记录
    const [patients] = await connection.query(
      `SELECT patient_id, is_registered 
       FROM patient_info 
       WHERE id_card = AES_ENCRYPT(?, UNHEX(?)) 
       FOR UPDATE`,
      [idCard, process.env.AES_KEY]
    );

    if (patients.length === 0) {
      await connection.rollback();
      return res.status(404).json({ 
        code: 'NO_RECORD',
        message: '未找到有效挂号记录' 
      });
    }

    if (patients[0].is_registered === 0) {
      await connection.rollback();
      return res.status(409).json({
        code: 'ALREADY_CANCELED',
        message: '当前没有可取消的挂号'
      });
    }

    await connection.commit();
    res.json({
      code: 'FOUND_RECORD',
      data: { patientId: patients[0].patient_id }
    });

  } catch (err) {
    await connection.rollback();
    console.error('[取消挂号] 检查异常:', err);
    res.status(500).json({
      code: 'SERVER_ERROR',
      message: '系统繁忙，请稍后重试'
    });
  } finally {
    connection.release();
  }
});

// 执行取消操作
router.post('/cancel/confirm', async (req, res) => {
  const { idCard } = req.body;
  const connection = await pool.getConnection();

  try {
    await connection.beginTransaction();

    // 原子化更新操作
    const [result] = await connection.query(
      `UPDATE patient_info 
       SET is_registered = 0 
       WHERE id_card = AES_ENCRYPT(?, UNHEX(?)) 
       AND is_registered = 1`,
      [idCard, process.env.AES_KEY]
    );

    if (result.affectedRows === 0) {
      await connection.rollback();
      return res.status(409).json({
        code: 'STATUS_CHANGED',
        message: '挂号状态已变更，请重新查询'
      });
    }

    await connection.commit();
    res.json({
      code: 'CANCEL_SUCCESS',
      message: '取消成功，退款将于24小时内原路返回'
    });

  } catch (err) {
    await connection.rollback();
    console.error('[取消挂号] 执行异常:', err);
    res.status(500).json({
      code: 'SERVER_ERROR',
      message: '系统繁忙，请稍后重试'
    });
  } finally {
    connection.release();
  }
});

module.exports = router;