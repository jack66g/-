const express = require('express');
const router = express.Router();
const { pool } = require('../db');
const sharp = require('sharp');

// 添加医生
router.post('/doctors', async (req, res) => {
    try {
        const { doctorId, name, introduction } = req.body;
        let photoData;
        
        // 处理图片压缩
        if (req.files?.photo) {
            photoData = await sharp(req.files.photo.data)
                .resize(300, 300)
                .jpeg({ quality: 80 })
                .toBuffer();
        }

        await pool.query(
            `INSERT INTO doctor_info SET ?`,
            {
                doctor_id: doctorId,
                doctor_name: name,
                photo_data: photoData,
                introduction,
                source_1: '00',  // 默认值
                source_2: '00',
                source_3: '00',
                source_4: '00'
            }
        );
        
        res.json({ success: true });
    } catch (error) {
        handleError(res, error);
    }
});

// 修改医生信息
router.put('/doctors/:id', async (req, res) => {
    try {
        const { name, introduction } = req.body;
        const updates = { doctor_name: name, introduction };
        
        // 处理图片更新
        if (req.files?.photo) {
            updates.photo_data = await sharp(req.files.photo.data)
                .resize(300, 300)
                .jpeg({ quality: 80 })
                .toBuffer();
        }

        const [result] = await pool.query(
            `UPDATE doctor_info SET ? WHERE doctor_id = ?`,
            [updates, req.params.id]
        );

        if (result.affectedRows === 0) {
            return res.status(404).json({ message: '医生不存在' });
        }
        
        res.json({ success: true });
    } catch (error) {
        handleError(res, error);
    }
});

// 分配号源
router.patch('/doctors/:id/sources', async (req, res) => {
    try {
        const { source1, source2, source3, source4 } = req.body;
        
        // 验证号源格式（允许空值但需要格式正确）
        const validateSource = (source) => {
            return source === null || source === undefined || /^\d{2}$/.test(source);
        };

        if (![source1, source2, source3, source4].every(validateSource)) {
            return res.status(400).json({ message: '号源格式错误，必须为两位数字' });
        }

        // 构建更新对象（只更新有值的字段）
        const updates = {};
        if (source1 !== undefined) updates.source_1 = source1;
        if (source2 !== undefined) updates.source_2 = source2;
        if (source3 !== undefined) updates.source_3 = source3;
        if (source4 !== undefined) updates.source_4 = source4;

        // 执行数据库更新
        const [result] = await pool.query(
            `UPDATE doctor_info SET ? WHERE doctor_id = ?`,
            [updates, req.params.id]
        );

        if (result.affectedRows === 0) {
            return res.status(404).json({ message: '医生不存在' });
        }
        
        res.json({ success: true });
    } catch (error) {
        handleError(res, error);
    }
});
// 错误处理统一方法
function handleError(res, error) {
    console.error(error);
    if (error.code === 'ER_DUP_ENTRY') {
        return res.status(400).json({ message: '医生工号已存在' });
    }
    res.status(500).json({ message: '服务器内部错误' });
}

module.exports = router;