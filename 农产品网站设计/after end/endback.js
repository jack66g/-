const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
require('dotenv').config();

const app = express();
// 中间件配置
app.use(cors({
    origin: process.env.CORS_ORIGIN || '*',
    methods: ['POST', 'PUT'],
    allowedHeaders: ['Content-Type'],
    credentials: true
}));
app.use(express.json());

// 数据库连接池配置
const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '3124456607q',
    database: process.env.DB_NAME || 'registration_db',
  waitForConnections: true,
  connectionLimit: 10,
  decimalNumbers: true // 确保正确解析DECIMAL类型
});

// 新增产品
app.post('/api/products', async (req, res) => {
    const { id, name, price, weight, image } = req.body;

    try {
        // 参数验证
        if (!/^\d{6}$/.test(id)) {
            return res.status(400).json({ message: '产品ID必须为6位数字' });
        }
        if (!name || name.length > 10) {
            return res.status(400).json({ message: '产品名称不能为空且不超过10个汉字' });
        }
        if (!price || price <= 0 || price.toString().length > 15) {
            return res.status(400).json({ message: '价格必须大于0且不超过15位数字' });
        }
        if (!weight || weight <= 0 || weight.toString().length > 14) {
            return res.status(400).json({ message: '重量必须大于0且不超过14位数字' });
        }

        // 插入数据库
        const [result] = await pool.query(
            `INSERT INTO products 
            (product_id, product_image, product_name, price, weight)
            VALUES (?, ?, ?, ?, ?)`,
            [id, image, name, price, weight]
        );

        res.status(201).json({ 
            message: '产品添加成功',
            productId: id
        });
    } catch (error) {
        console.error('数据库错误:', error);
        const message = error.code === 'ER_DUP_ENTRY' 
            ? '产品ID已存在' 
            : '服务器内部错误';
        res.status(500).json({ message });
    }
});

// 修改产品信息
app.put('/api/products/:id', async (req, res) => {
    const productId = req.params.id;
    const { price, weight } = req.body;

    try {
        // 参数验证
        if (!/^\d{6}$/.test(productId)) {
            return res.status(400).json({ message: '无效的产品ID格式' });
        }
        if (!price || price <= 0 || price.toString().length > 15) {
            return res.status(400).json({ message: '价格必须大于0且不超过15位数字' });
        }
        if (!weight || weight <= 0 || weight.toString().length > 14) {
            return res.status(400).json({ message: '重量必须大于0且不超过14位数字' });
        }

        // 执行更新
        const [result] = await pool.query(
            `UPDATE products 
            SET price = ?, weight = ?
            WHERE product_id = ?`,
            [price, weight, productId]
        );

        if (result.affectedRows === 0) {
            return res.status(404).json({ message: '未找到指定产品' });
        }

        res.json({ 
            message: '产品信息更新成功',
            updated: {
                productId,
                newPrice: price,
                newWeight: weight
            }
        });
    } catch (error) {
        console.error('数据库错误:', error);
        res.status(500).json({ 
            message: error.sqlMessage || '服务器内部错误' 
        });
    }
});

// 启动服务
const PORT = process.env.BACKPORT || 3006;
app.listen(PORT, () => {
    console.log(`服务器运行在端口 ${PORT}`);
});