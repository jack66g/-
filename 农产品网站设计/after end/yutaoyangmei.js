const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

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

// 产品查询接口
// 修改后的产品查询接口
app.get('/api/products/:name', (req, res) => {
    const productName = req.params.name;
    
    pool.query(
        'SELECT * FROM products WHERE product_name = ?',
        [productName],
        (error, results) => {
            if (error) {
                console.error('数据库错误:', error);
                return res.status(500).json({ error: '数据库查询失败' });
            }
            
            if (results.length === 0) {
                return res.status(404).json({ error: '未找到相关产品' });
            }

            // 直接返回存储的Base64字符串
            const products = results.map(product => ({
                ...product,
                product_image: `${product.product_image}`
            }));

            res.json(products);
        }
    );
});

// 启动服务
const PORT = process.env.PIR_PORT || 3008; // 使用独立环境变量和使用不同端口
app.listen(PORT, () => {
  console.log(`🔑 密码重置服务运行在：http://localhost:${PORT}`);
});