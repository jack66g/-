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

// 数据库连接池（已根据您的配置调整）
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '3124456607q',
  database: process.env.DB_NAME || 'registration_db',
    connectionLimit: 10
});

// 根据ID获取产品信息
app.get('/api/products/:id', (req, res) => {
    const productId = req.params.id;
    
    pool.query(
        'SELECT * FROM products WHERE product_id = ?',
        [productId],
        (error, results) => {
            if (error) return res.status(500).json({ error: '数据库错误' });
            if (!results.length) return res.status(404).json({ error: '产品不存在' });
            
            const product = {
                ...results[0],
                // 确保图片路径正确（根据实际存储方式调整）
                product_image: results[0].product_image 
            };
            
            res.json(product);
        }
    );
});

// 处理购买请求
app.put('/api/products/:id/purchase', (req, res) => {
    const productId = req.params.id;
    const { quantity } = req.body;

    if (!quantity || quantity <= 0) {
        return res.status(400).json({ error: '无效的数量' });
    }

    pool.query(
        'UPDATE products SET sales = sales + ?, temp_sales = ? WHERE product_id = ?',
        [quantity, quantity, productId],
        (error) => {
            if (error) return res.status(500).json({ error: '更新失败' });
            res.json({ message: '购买成功!' });
        }
    );
});

// 启动服务
const PORT = 3010;
app.listen(PORT, () => {
    console.log(`服务运行在：http://localhost:${PORT}`);
});