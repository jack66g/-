const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// 数据库连接池
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: '3124456607q',
  database: 'registration_db',
  connectionLimit: 10
});

// 获取商品信息接口
app.get('/api/products/:id', (req, res) => {
    const productId = req.params.id;
    
    pool.query(
        'SELECT product_id, product_name, price, product_image, temp_sales FROM products WHERE product_id = ?',
        [productId],
        (error, results) => {
            if (error) return res.status(500).json({ error: '数据库错误' });
            if (!results.length) return res.status(404).json({ error: '商品不存在' });
            
            res.json(results[0]);
        }
    );
});

// 启动服务
const PORT = 3011;
app.listen(PORT, () => {
    console.log(`订单服务运行在：http://localhost:${PORT}`);
});