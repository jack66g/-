// 文件路径: src/store/localDb.js

// 定义 localStorage 的 Key 值常量，防止拼写错误
const KEYS = {
  API_KEY: 'survey_api_key',
  TEMPLATE: 'survey_template',
  ANSWERS: 'survey_answers'
};

/**
 * =========================================
 * 1. API Key 管理 (存取大模型密钥)
 * =========================================
 */
export const saveApiKey = (key) => {
  localStorage.setItem(KEYS.API_KEY, key);
};

export const getApiKey = () => {
  return localStorage.getItem(KEYS.API_KEY) || '';
};

/**
 * =========================================
 * 2. 问卷模板管理 (保存 AI 生成的 JSON)
 * =========================================
 */
export const saveSurveyTemplate = (data) => {
  // data 应该是一个对象，例如: { title: "高数问卷", questions: [...] }
  localStorage.setItem(KEYS.TEMPLATE, JSON.stringify(data));
};

export const getSurveyTemplate = () => {
  const data = localStorage.getItem(KEYS.TEMPLATE);
  try {
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.error("解析问卷模板失败:", e);
    return null;
  }
};

/**
 * =========================================
 * 3. 学生答卷管理 (保存学生的答卷数据)
 * =========================================
 */
export const saveStudentAnswer = (answerData) => {
  // 读取已有的所有答卷，如果没有则是空数组
  const existingAnswers = getAllAnswers();
  
  // 将新答卷追加进去，并重新保存
  // answerData 结构建议: { q_0: "选项A", q_1: "选项B", submitTime: "2026-04-15..." }
  existingAnswers.push({
    ...answerData,
    _id: Date.now().toString(), // 给每份答卷生成一个简单的唯一ID
  });
  
  localStorage.setItem(KEYS.ANSWERS, JSON.stringify(existingAnswers));
};

export const getAllAnswers = () => {
  const data = localStorage.getItem(KEYS.ANSWERS);
  try {
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error("解析答卷数据失败:", e);
    return [];
  }
};

/**
 * =========================================
 * 4. 数据统计引擎 (读取答卷，计算百分比供图表使用)
 * =========================================
 */
export const getStatistics = () => {
  const template = getSurveyTemplate();
  const answers = getAllAnswers();

  // 如果没有模板或者没人填问卷，直接返回 null
  if (!template || !template.questions || answers.length === 0) {
    return { totalSubmissions: 0, details: null };
  }

  // 1. 初始化统计结果的结构
  const stats = {};
  template.questions.forEach((q, index) => {
    // 假设题目在数据中的标识是 q_0, q_1 ...
    const qKey = `q_${index}`; 
    stats[qKey] = {
      title: q.title,         // 题目文本
      type: q.type,           // 题目类型 (radio/checkbox等)
      optionsCount: {},       // 各选项被选次数 { "A": 0, "B": 0 }
      totalAnswers: 0         // 该题总作答人数
    };
    
    // 初始化每个选项的计数器为 0
    if (q.options && Array.isArray(q.options)) {
      q.options.forEach(opt => {
        stats[qKey].optionsCount[opt] = 0;
      });
    }
  });

  // 2. 遍历所有收集到的答卷，进行计票
  answers.forEach(ans => {
    Object.keys(ans).forEach(qKey => {
      // 确保答卷里的题目 key 在我们的模板统计结构中
      if (stats[qKey] && stats[qKey].optionsCount[ans[qKey]] !== undefined) {
        stats[qKey].optionsCount[ans[qKey]] += 1; // 票数 +1
        stats[qKey].totalAnswers += 1;            // 总人数 +1
      }
    });
  });

  // 返回最终的统计结果和总提交份数
  return {
    totalSubmissions: answers.length,
    details: stats
  };
};

/**
 * =========================================
 * 5. 辅助工具
 * =========================================
 */
// 方便你在开发测试时一键清空数据
export const clearAllData = () => {
  localStorage.removeItem(KEYS.TEMPLATE);
  localStorage.removeItem(KEYS.ANSWERS);
  console.log("本地问卷与答题数据已清空！(API Key已保留)");
};