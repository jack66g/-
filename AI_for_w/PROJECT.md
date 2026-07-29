# SmartWriter 智能写作平台

基于 AI 的智能文章写作与管理平台，支持用户创作、发现和分享优质内容。

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 + Vite | Vue 3.5 / Vite 8 |
| UI 组件库 | Element Plus | 2.13 |
| 富文本编辑 | Vditor + md-editor-v3 | 3.11 / 6.4 |
| 图表 | ECharts | 6.0 |
| 状态管理 | Pinia | 3.0 |
| HTTP 客户端 | Axios | 1.15 |
| 后端框架 | Django + DRF | 5.2 / 3.17 |
| 认证 | Simple JWT | 5.5 |
| 数据库 | MySQL | 8.0 |
| 数据库驱动 | PyMySQL | 1.1 |

---

## 环境要求

| 环境 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 20.19+ 或 22.12+ | 前端构建工具 |
| MySQL | 8.0 | 数据库（服务名 `MySQL80`） |
| npm | 随 Node.js | 包管理器 |

---

## 从零开始配置

### 第一步：克隆项目

```bash
git clone <your-repo-url>
cd AI_for_w
```

### 第二步：安装 MySQL 并创建数据库

1. 安装 MySQL 8.0（[官网下载](https://dev.mysql.com/downloads/mysql/)）
2. 安装时记住 root 密码
3. 安装完成后，用命令行或 MySQL Workbench 连接：

```sql
CREATE DATABASE smart_writer_db DEFAULT CHARACTER SET utf8mb4;
```

### 第三步：配置后端

**3.1 打开 `SmartWriter_Backend/server_core/settings.py`**，修改数据库配置（第 84-93 行）：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smart_writer_db',      # 数据库名
        'USER': 'root',                 # 你的 MySQL 用户名
        'PASSWORD': '你的MySQL密码',      # 你的 MySQL 密码 ← 改这里
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

**3.2 创建虚拟环境并安装依赖：**

```bash
cd SmartWriter_Backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**3.3 初始化数据库：**

```bash
python manage.py migrate
```

**3.4 创建管理员账号：**

```bash
python manage.py createsuperuser
# 按提示输入用户名、邮箱、密码
```

### 第四步：配置前端

```bash
cd smart-writer-web

# 安装依赖
npm install
```

### 第五步：启动项目

**终端 1 — 启动后端：**

```bash
cd SmartWriter_Backend
venv\Scripts\activate
python manage.py runserver 8000
```

**终端 2 — 启动前端：**

```bash
cd smart-writer-web
npm run dev
```

浏览器访问 **http://localhost:5173**

> 也可以双击项目根目录的 `start.bat` 一键启动（会自动检查 MySQL、启动后端和前端）。

---

## 项目结构

```
AI_for_w/
├── start.bat                    # Windows 一键启动脚本
├── PROJECT.md                   # 本文档
├── .gitignore                   # Git 忽略规则
│
├── SmartWriter_Backend/         # Django 后端
│   ├── manage.py                # Django 管理入口
│   ├── requirements.txt         # Python 依赖清单
│   ├── server_core/             # Django 核心配置
│   │   ├── settings.py          # 数据库、JWT、CORS 配置
│   │   ├── urls.py              # 路由入口
│   │   └── wsgi.py              # WSGI 入口
│   ├── articles/                # 文章模块（CRUD、点赞、举报）
│   ├── ai_gateway/              # AI 网关（DeepSeek 调用）
│   ├── users/                   # 用户模块（自定义 User、JWT 认证）
│   │   ├── models.py            # User 模型
│   │   ├── views.py             # 登录/注册/个人中心
│   │   ├── serializers.py       # 序列化器
│   │   └── authentication.py    # 软 JWT 认证类
│   └── migrations/              # 数据库迁移文件
│
└── smart-writer-web/            # Vue 3 前端
    ├── package.json             # Node 依赖与脚本
    ├── vite.config.js           # Vite 构建配置
    ├── index.html               # HTML 入口
    └── src/
        ├── main.js              # Vue 应用入口
        ├── App.vue              # 根组件
        ├── router/index.js      # 路由配置（含权限守卫）
        ├── stores/user.js       # 用户状态（Pinia）
        ├── utils/request.js     # Axios 封装（自动 JWT）
        └── views/
            ├── LoginView.vue         # 登录
            ├── RegisterView.vue      # 注册
            ├── DiscoveryView.vue     # 发现广场（公开）
            ├── EditorView.vue        # 文章编辑器
            ├── UserWorkspaceView.vue  # 用户工作台
            ├── ProfileView.vue       # 个人中心（配置 AI Key）
            └── AdminDashboardView.vue # 管理后台
```

---

## API 接口

| 模块 | 路径 | 认证 | 说明 |
|------|------|:--:|------|
| 注册 | `POST /api/register/` | 否 | 用户注册 |
| 登录 | `POST /api/login/` | 否 | 获取 JWT Token |
| 刷新 Token | `POST /api/token/refresh/` | 否 | 刷新 Access Token |
| 个人中心 | `GET/PUT /api/users/me/` | 是 | 查看/修改个人信息 |
| 文章列表 | `GET /api/articles/` | 是 | 我的文章 |
| 公开文章 | `GET /api/articles/public/` | 否 | 发现广场 |
| 文章详情 | `GET /api/articles/{id}/` | 否 | 阅读全文 |
| 创建文章 | `POST /api/articles/` | 是 | 发布文章 |
| 点赞/踩 | `POST /api/articles/{id}/interact/` | 是 | 互动操作 |
| 举报 | `POST /api/articles/{id}/report/` | 是 | 举报文章 |
| AI 生成 | `POST /api/ai/generate/` | 是 | AI 写文章 |
| AI 润色 | `POST /api/ai/polish/` | 是 | AI 润色 |
| 管理后台 | `/admin/` | 管理员 | Django 原生后台 |

---

## 认证机制

- 使用 **Simple JWT**（JSON Web Token）
- Access Token 有效期：1 天
- Refresh Token 有效期：7 天
- 前端 Axios 拦截器自动附加 `Authorization: Bearer <token>`
- 使用 `SoftJWTAuthentication`：过期 Token 不会导致公开接口 401

---

## 路由权限

| 路由 | 公开 | 说明 |
|------|:--:|------|
| `/discovery` | ✅ | 发现广场，无需登录 |
| `/login` | ✅ | 登录页 |
| `/register` | ✅ | 注册页 |
| `/user-workspace` | ❌ | 用户工作台，需登录 |
| `/editor` | ❌ | 文章编辑器，需登录 |
| `/profile` | ❌ | 个人中心，需登录 |
| `/admin-dashboard` | ❌ | 管理后台，需管理员 |

---

## AI 功能配置

本平台的 AI 写作功能依赖 **DeepSeek API**。

1. 登录后进入「个人中心」
2. 填入你的 DeepSeek API Key（`sk-xxxx`）
3. 保存后即可在编辑器中调用 AI 生成/润色

> API Key 存储在数据库，代码中无硬编码。每个用户独立配置。

---

## 常见问题

**Q: 启动时 MySQL 连接失败？**
A: 确保 Windows 服务中 `MySQL80` 已启动。`Win+R` → `services.msc` → 找到 MySQL80 → 启动。

**Q: `npm run dev` 报错？**
A: 确认 Node.js 版本 ≥ 22.12，然后重新 `npm install`。

**Q: 前端页面打开但数据加载失败？**
A: 确认 Django 后端也在运行（另一个终端，端口 8000）。

**Q: 登录提示"No active account found"？**
A: 先注册账号，或用 `createsuperuser` 创建。注意：`migrate` 后老数据不再存在。

**Q: 如何上传 GitHub？**
A: `venv/`、`node_modules/`、`dist/` 已在 `.gitignore` 中排除，直接 `git add .` 即可。

---

## 安全提醒

- `settings.py` 中的 `SECRET_KEY` 和数据库密码仅供本地开发
- 部署生产环境时请改用环境变量读取敏感配置
- AI API Key 由用户自行在个人中心配置，不要提交到代码仓库
