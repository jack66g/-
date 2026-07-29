const express = require('express');
const axios = require('axios');
const router = express.Router();

// 百度API配置 —— 仅从环境变量读取，不暴露默认值
const BAIDU_API_KEY = process.env.BAIDU_API_KEY;
const BAIDU_SECRET_KEY = process.env.BAIDU_SECRET_KEY;

// 启动时校验密钥是否存在
if (!BAIDU_API_KEY || !BAIDU_SECRET_KEY) {
  console.error('⚠️ 百度人脸识别API密钥未配置！请在 .env 文件中设置 BAIDU_API_KEY 和 BAIDU_SECRET_KEY');
  console.error('   人脸识别功能将不可用，其他功能不受影响。');
}

let accessToken = '';

// 获取accessToken函数
async function getAccessToken() {
  if (!BAIDU_API_KEY || !BAIDU_SECRET_KEY) {
    console.error('获取百度Token失败: 密钥未配置');
    return null;
  }
  try {
    const response = await axios.post(
      `https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=${BAIDU_API_KEY}&client_secret=${BAIDU_SECRET_KEY}`
    );
    return response.data.access_token;
  } catch (error) {
    console.error('获取百度Token失败:', error.message);
    return null;
  }
}

// 人脸比对路由
router.post('/face-match', async (req, res) => {
  try {
    const { image1, image2 } = req.body;
    
    if (!image1 || !image2) {
      return res.status(400).json({
        success: false,
        error: '缺少图片数据'
      });
    }

    // 密钥未配置时直接返回错误
    if (!BAIDU_API_KEY || !BAIDU_SECRET_KEY) {
      return res.status(500).json({
        success: false,
        error: '人脸识别服务未配置，请联系管理员'
      });
    }
    
    if (!accessToken) {
      accessToken = await getAccessToken();
      if (!accessToken) {
        return res.status(500).json({
          success: false,
          error: '无法获取百度API访问令牌'
        });
      }
    }

    const response = await axios.post(
      `https://aip.baidubce.com/rest/2.0/face/v3/match?access_token=${accessToken}`,
      [
        {
          image: image1,
          image_type: "BASE64",
          face_type: "LIVE",
          quality_control: "NORMAL",
          liveness_control: "NORMAL"
        },
        {
          image: image2,
          image_type: "BASE64",
          face_type: "LIVE",
          quality_control: "NORMAL",
          liveness_control: "NORMAL"
        }
      ],
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000
      }
    );

    const baiduResult = response.data;
    if (baiduResult.error_code) {
      return res.json({ 
        success: false, 
        error: `百度API错误: ${baiduResult.error_msg} (${baiduResult.error_code})`
      });
    }

    const score = baiduResult.result?.score || 0;
    res.json({
      success: score > 80,
      score: score,
      message: score > 80 ? '验证成功' : '人脸比对失败'
    });

  } catch (error) {
    console.error('人脸验证失败:', error);
    res.status(500).json({
      success: false,
      error: '服务器内部错误: ' + error.message
    });
  }
});

// 启动时预获取Token（仅在密钥已配置时）
if (BAIDU_API_KEY && BAIDU_SECRET_KEY) {
  getAccessToken().then(token => {
    if (token) {
      accessToken = token;
      console.log('百度API访问令牌预获取成功');
    }
  });
}

module.exports = router;
