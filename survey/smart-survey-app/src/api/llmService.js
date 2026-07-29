// 文件路径: src/api/llmService.js
import { getApiKey } from '../store/localDb';

// 这里默认使用 DeepSeek 的 API 地址，如果你用通义千问或 Kimi，换成它们的就行
const API_URL = 'https://api.deepseek.com/chat/completions'; 
const MODEL_NAME = 'deepseek-chat'; 

/**
 * 基础请求函数：发送对话给大模型
 */
async function callLLM(messages, requireJson = false) {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('未设置 API Key，请先去设置页填写！');
  }

  const payload = {
    model: MODEL_NAME,
    messages: messages,
    temperature: 0.7, // 控制随机性，0.7比较适合生成多样化问卷
  };

  // 如果大模型支持强制 JSON 输出格式（DeepSeek 支持）
  if (requireJson) {
    payload.response_format = { type: "json_object" };
  }

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error?.message || '大模型请求失败');
    }

    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error("LLM 调用异常:", error);
    throw error;
  }
}

/**
 * =========================================
 * 核心功能 1: 智能生成问卷
 * =========================================
 * @param {string} topic - 老师输入的教学难点或问卷主题
 * @param {number} count - 题目数量，默认5题
 */
export async function generateSurvey(topic, count = 5) {
  const systemPrompt = `你是一个大学教育辅助系统。
请根据用户提供的主题，生成一份包含 ${count} 道单选题的调查问卷。
你必须严格输出合法的 JSON 对象，不要包含任何 Markdown 标记（如 \`\`\`json ）。
JSON 格式必须严格如下：
{
  "title": "生成的问卷主标题",
  "questions": [
    {
      "title": "题目1的问题描述",
      "type": "radio",
      "options": ["选项A的内容", "选项B的内容", "选项C的内容", "选项D的内容"]
    }
  ]
}`;

  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: `请帮我生成一份关于“${topic}”的教学情况调查问卷。` }
  ];

  try {
    const resultText = await callLLM(messages, true);
    // 将返回的 JSON 字符串解析为 JS 对象
    return JSON.parse(resultText);
  } catch (error) {
    throw new Error('问卷生成失败，可能是大模型返回的格式不正确或网络错误。');
  }
}

/**
 * =========================================
 * 核心功能 2: 智能生成调查结论报告
 * =========================================
 * @param {Object} statsData - 从 localDb.getStatistics() 拿到的统计数据
 */
export async function generateReport(statsData) {
  // 把统计对象转换成大模型能看懂的文字描述
  let statsText = `本次问卷共收到 ${statsData.totalSubmissions} 份有效答卷。\n具体各题答题分布如下：\n`;
  
  if (statsData.details) {
    Object.values(statsData.details).forEach((q, index) => {
      statsText += `第${index + 1}题：${q.title}\n`;
      Object.entries(q.optionsCount).forEach(([option, count]) => {
        // 计算百分比
        const percent = q.totalAnswers > 0 ? ((count / q.totalAnswers) * 100).toFixed(1) : 0;
        statsText += ` - [${option}] 被选次数: ${count} (${percent}%)\n`;
      });
    });
  }

  const systemPrompt = `你是一位资深的大学教学督导。
请阅读用户提供的“学生调查问卷统计数据”，生成一份约 300 字的“调查结论与教学改进建议”报告。
要求：
1. 语气正式、专业。
2. 直接指出学生反映集中的问题点。
3. 给出具有可操作性的教学改进建议。
4. 直接输出报告正文，不需要寒暄。`;

  const messages = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: statsText }
  ];

  // 这里不需要强制 JSON，直接返回纯文本即可
  return await callLLM(messages, false);
}