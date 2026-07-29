const express = require('express');
const router = express.Router();
const { pool } = require('../db');

// 获取医生信息
router.get('/endocrine/doctor/:id', async (req, res) => {
  try {
    const [doctor] = await pool.query(
      'SELECT * FROM doctor_info WHERE doctor_id = ?',
      [req.params.id]
    );

    if (!doctor.length) return res.status(404).json({ error: "医生不存在" });

    const photoBase64 = doctor[0].photo_data.toString('base64');
    
    res.json({
      id: doctor[0].doctor_id,
      name: doctor[0].doctor_name,
      photo: `data:image/jpeg;base64,${photoBase64}`,
      intro: doctor[0].introduction,
      sources: {
        source1: +doctor[0].source_1,
        source2: +doctor[0].source_2,
        source3: +doctor[0].source_3,
        source4: +doctor[0].source_4
      }
    });

  } catch (err) {
    console.error('医生信息获取失败:', err);
    res.status(500).json({ error: "服务器错误" });
  }
});

// 患者验证接口（身份证版）
router.post('/endocrine/verify-patient', async (req, res) => {
  const { idCard } = req.body;
  const connection = await pool.getConnection();

  try {
    await connection.beginTransaction();

    const [patients] = await connection.query(
      `SELECT patient_id, is_registered 
       FROM patient_info 
       WHERE id_card = AES_ENCRYPT(?, UNHEX(?)) 
       FOR UPDATE`,
      [idCard, process.env.AES_KEY]
    );

    if (!patients.length) {
      await connection.rollback();
      return res.json({ 
        success: false, 
        error: "未找到匹配患者，请先建档" 
      });
    }

    if (patients[0].is_registered === 1) {
      await connection.rollback();
      return res.json({ 
        success: false,
        error: "该患者已有有效挂号" 
      });
    }

    await connection.commit();
    res.json({ 
      success: true,
      patientId: patients[0].patient_id 
    });

  } catch (err) {
    await connection.rollback();
    console.error('患者验证失败:', err);
    res.status(500).json({ error: "验证服务异常" });
  } finally {
    connection.release();
  }
});

// 挂号接口
router.post('/endocrine/register', async (req, res) => {
  const { doctorId, sourceType, patientId } = req.body;
  const connection = await pool.getConnection();

  try {
    await connection.beginTransaction();

    // 验证患者状态
    const [patients] = await connection.query(
      `SELECT is_registered FROM patient_info 
       WHERE patient_id = ? 
       FOR UPDATE`,
      [patientId]
    );

    if (patients[0].is_registered === 1) {
      await connection.rollback();
      return res.json({ 
        success: false,
        error: "患者状态已变更，请刷新后重试" 
      });
    }

    // 检查号源
    const [sources] = await connection.query(
      `SELECT source_${sourceType} FROM doctor_info 
       WHERE doctor_id = ? 
       FOR UPDATE`,
      [doctorId]
    );

    const remaining = +sources[0][`source_${sourceType}`];
    if (remaining < 1) {
      await connection.rollback();
      return res.json({ 
        success: false,
        error: "号源已满" 
      });
    }

    // 执行更新
    await Promise.all([
      connection.query(
        `UPDATE patient_info 
         SET is_registered = 1 
         WHERE patient_id = ?`,
        [patientId]
      ),
      connection.query(
        `UPDATE doctor_info 
         SET source_${sourceType} = ? 
         WHERE doctor_id = ?`,
        [remaining - 1, doctorId]
      )
    ]);

    await connection.commit();
    res.json({ 
      success: true,
      remaining: remaining - 1 
    });

  } catch (err) {
    await connection.rollback();
    console.error('挂号失败:', err);
    res.status(500).json({ error: "系统繁忙" });
  } finally {
    connection.release();
  }
});

module.exports = router;