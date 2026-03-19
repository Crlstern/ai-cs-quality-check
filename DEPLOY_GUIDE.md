# AI 客服质检系统 - 部署指南

## 项目简介

这是一个基于 AI 大模型的智能客服质检系统，可以自动分析客服对话日志，识别问题并生成质检报告。

### 功能特性

- 🤖 **AI 意图识别**：智能识别客户意图
- ⚠️ **Bad Case 检测**：自动检测服务质量问题
- 📊 **根因分析**：分析问题根本原因
- 📈 **置信度评估**：评估识别准确率
- 📝 **自动报告生成**：生成专业质检日报

### 技术栈

- **后端**：Flask + DeepSeek API
- **前端**：HTML + Bootstrap 5 + Chart.js
- **AI**：DeepSeek 大模型

---

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env` 并填入你的 DeepSeek API Key：

```bash
cp .env.example .env
# 编辑 .env 文件，替换 DEEPSEEK_API_KEY
```

### 3. 启动服务

```bash
python flask_app.py
```

访问 http://127.0.0.1:5001

---

## 部署到 Vercel（免费）

### 步骤 1：注册 Vercel

1. 访问 https://vercel.com
2. 使用 GitHub 账号注册/登录
3. 点击 "New Project" 创建新项目

### 步骤 2：导入项目

1. 连接到你的 GitHub 仓库
2. 选择本项目
3. 配置环境变量：
   - `DEEPSEEK_API_KEY`: 你的 DeepSeek API Key
   - `USE_REAL_API`: `false`（演示模式）或 `true`（真实 API）

### 步骤 3：部署

1. 点击 "Deploy"
2. 等待部署完成（约 1-2 分钟）
3. 获取访问地址，如：`https://your-project.vercel.app`

### 步骤 4：生成二维码

访问 https://www.sejda.com/png-to-qrcode 或其他二维码生成工具，将你的 Vercel 地址生成二维码。

---

## 使用说明

### 演示模式（默认）

- 不需要 API Key
- 使用模拟数据进行演示
- 适合面试展示

### 真实 API 模式

- 需要配置 DeepSeek API Key
- 使用真实 AI 进行分析
- 在 `.env` 文件中设置 `USE_REAL_API=true`

---

## 获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com
2. 注册账号
3. 在控制台创建 API Key
4. 充值或使用免费额度

---

## 面试亮点

1. ✅ 展示了 AI 大模型的集成能力
2. ✅ 真实的意图识别和 Bad Case 检测
3. ✅ 专业的质检报告生成
4. ✅ 云端部署能力
5. ✅ 前端可视化展示

---

## 许可证

MIT License
