# Smart Survey App — 智能教学问卷系统

基于 **Vue 3 + Vite + Vant + ECharts** 的移动端教学问卷工具，接入大模型 API，实现问卷的**智能生成 → 学生填答 → 数据分析 → AI 改进建议**完整闭环。

## 功能概览

| 模块 | 说明 |
|------|------|
| 🎓 **教师控制台** | 输入教学难点主题，AI 自动生成 N 道单选题问卷 |
| ✏️ **学生填答** | 移动端友好的问卷答题界面，提交后数据实时入库 |
| 📊 **分析报告** | ECharts 饼图可视化各题选项分布 + AI 教学督导建议 |
| ⚙️ **系统设置** | 配置大模型 API Key、一键清空历史数据 |

## 技术栈

- **Vue 3** — Composition API (`<script setup>`)
- **Vite 8** — 极速构建工具
- **Vant 4** — 移动端 UI 组件库
- **ECharts 6** — 数据可视化图表
- **Vue Router 4** — Hash 模式路由
- **DeepSeek API** — AI 问卷生成 & 报告生成
- **localStorage** — 本地数据持久化

## 快速启动

### 环境要求

- **Node.js >= 18**
- **npm >= 9**

### 安装与运行

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd smart-survey-app

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

浏览器访问 `http://localhost:5173` 即可。

### 构建生产版本

```bash
npm run build      # 输出到 dist/
npm run preview    # 预览构建结果
```

## 使用指南

### 1. 配置 API Key

首次使用需在**「设置」**页面填写 DeepSeek API Key（[获取地址](https://platform.deepseek.com/api_keys)）。

> 如使用其他大模型（通义千问、Kimi 等），修改 `src/api/llmService.js` 中的 `API_URL` 和 `MODEL_NAME` 即可。

### 2. 生成问卷

在**「教师控制台」**输入教学难点主题（如"集成电路 CMOS 工艺"），设定题目数量（1–25 题），点击「一键智能生成问卷」，AI 将自动生成带选项的单选题问卷。

### 3. 学生填答

切换到**「学生填答」** Tab，逐题选择答案后提交，数据保存在浏览器本地。

### 4. 查看报告

切换到**「分析报告」** Tab：
- 查看各题选项分布的 ECharts 饼图
- 点击「一键生成 AI 教学改进报告」获得教学督导建议

## 项目结构

```
smart-survey-app/
├── index.html                  # 入口 HTML
├── vite.config.js              # Vite 配置
├── package.json                # 依赖清单
├── src/
│   ├── main.js                 # 应用入口
│   ├── App.vue                 # 根组件（底部 TabBar）
│   ├── style.css               # 全局样式
│   ├── api/
│   │   └── llmService.js       # 大模型 API 调用（问卷生成 + 报告生成）
│   ├── store/
│   │   └── localDb.js          # localStorage 数据存取（增删改查 + 统计）
│   ├── router/
│   │   └── index.js            # 路由配置（Hash 模式）
│   └── views/
│       ├── Teacher/
│       │   ├── Dashboard.vue   # 教师控制台 — AI 生成问卷
│       │   └── Report.vue      # 数据分析报告 — ECharts + AI 建议
│       ├── Student/
│       │   └── Survey.vue      # 学生填答问卷
│       └── Setting.vue         # 系统设置 — API Key 管理
```

## 常见问题

**Q: 生成问卷失败，提示"未设置 API Key"？**  
A: 请先到「设置」页填写有效的 DeepSeek API Key。

**Q: 数据存在哪里？会丢失吗？**  
A: 所有数据存储在浏览器 localStorage 中，清除浏览器缓存会导致数据丢失。正式使用建议接入后端数据库。

**Q: 支持其他大模型吗？**  
A: 支持。修改 `src/api/llmService.js` 第 5–6 行的 `API_URL` 和 `MODEL_NAME` 即可切换。

## License

MIT
