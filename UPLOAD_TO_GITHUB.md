# 📤 上传到 GitHub 的两种方法

## 方法一：使用 Git 命令行（推荐）

### 1. 安装 Git

访问 <https://git-scm.com/download/win> 下载并安装

### 2. 初始化并上传

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "AI 客服质检系统 - 初始版本"

# 创建 GitHub 仓库后，关联远程仓库
git remote add origin https://github.com/你的用户名/仓库名.git

# 推送到 GitHub
git push -u origin main
```

***

## 方法二：使用 GitHub Desktop（适合新手）

### 1. 下载 GitHub Desktop

访问 <https://desktop.github.com/>

### 2. 操作步骤

1. 打开 GitHub Desktop
2. 点击 "File" → "Add Local Repository"
3. 选择你的项目文件夹 `a:\xiangmu\tongji`
4. 点击 "Commit to main"
5. 点击 "Publish repository"
6. 输入仓库名称，点击 "Publish"

***

## 方法三：直接网页上传（最简单）

### 1. 创建 GitHub 仓库

1. 访问 <https://github.com/new>
2. 输入仓库名称，如 `ai-cs-quality-check`
3. 点击 "Create repository"

### 2. 上传文件

1. 点击 "uploading an existing file"
2. 拖拽所有文件到网页
3. 点击 "Commit changes"

⚠️ **注意**：`.env` 文件不要上传！已添加到 `.gitignore` 了。

***

## ✅ 上传完成后

1. 确认 GitHub 仓库中有以下文件：
   - `flask_app.py`
   - `deepseek_api.py`
   - `config.py`
   - `agents.py`
   - `models.py`
   - `templates/index.html`
   - `requirements.txt`
   - `vercel.json`
   - `.env.example`（示例配置）
   - `README.md`
   - `QUICK_START.md`
   - `DEPLOY_GUIDE.md`
2. 接下来部署到 Vercel

***

## 🚀 部署到 Vercel

### 步骤 1：访问 Vercel

<https://vercel.com>

### 步骤 2：登录

使用 GitHub 账号登录

### 步骤 3：创建项目

1. 点击 "New Project"
2. 选择 "Import Git Repository"
3. 找到你的仓库，点击 "Import"

### 步骤 4：配置环境变量

在 "Environment Variables" 中添加：

```
DEEPSEEK_API_KEY = sk-b1b60ff0ad09440c9...（你的真实 API Key）
USE_REAL_API = false
```

### 步骤 5：部署

点击 "Deploy"，等待 1-2 分钟

### 步骤 6：获取访问地址

部署完成后，你会得到类似这样的地址：

```
https://ai-cs-quality-check.vercel.app
```

### 步骤 7：生成二维码

访问 <https://www.qr-code-generator.com/> 或搜索"二维码生成器"，输入你的 Vercel 地址生成二维码。

***

## 💡 提示

- `.env` 文件包含敏感信息，已添加到 `.gitignore`，不要上传到 GitHub
- 部署到 Vercel 时，环境变量在 Vercel 控制台配置
- 本地测试用 `.env`，云端用 Vercel 的环境变量

