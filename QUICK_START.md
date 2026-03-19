# 🚀 快速部署指南 - 5 分钟上线

## 方式一：部署到 Vercel（推荐）⭐

### 1. 上传到 GitHub

```bash
# 初始化 Git（如果还没有）
git init
git add .
git commit -m "AI 客服质检系统"

# 创建 GitHub 仓库并推送
# 访问 https://github.com/new 创建仓库
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 2. 部署到 Vercel

1. **访问** https://vercel.com
2. **登录** - 使用 GitHub 账号
3. **New Project** - 点击创建新项目
4. **Import Git Repository** - 选择你的仓库
5. **配置环境变量**：
   ```
   DEEPSEEK_API_KEY = sk-your-api-key
   USE_REAL_API = false
   ```
6. **Deploy** - 点击部署
7. **完成！** - 获得访问地址，如：`https://your-project.vercel.app`

### 3. 生成二维码

访问 https://www.qr-code-generator.com/ 或搜索"二维码生成器"，输入你的 Vercel 地址生成二维码。

---

## 方式二：本地运行（演示用）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）

创建 `.env` 文件：
```bash
DEEPSEEK_API_KEY=sk-your-api-key
USE_REAL_API=false
```

### 3. 启动服务

```bash
python flask_app.py
```

访问 http://127.0.0.1:5001

---

## 面试展示建议

### 方案 A：云端部署（最佳）⭐
- ✅ 24 小时在线
- ✅ 扫码即可访问
- ✅ 专业可靠
- ✅ 加分项：展示部署能力

### 方案 B：本地运行 + 录屏
- 录制演示视频
- 面试时播放
- 适合网络不好的情况

### 方案 C：本地运行 + 热点分享
- 使用手机热点
- 现场启动服务
- 让面试官扫码访问你的电脑 IP

---

## 面试话术建议

```
"这是我开发的 AI 客服质检系统，主要特点有：

1. 接入了 DeepSeek 大模型 API，可以真实地进行意图识别和 Bad Case 检测
2. 支持两种模式：演示模式（快速展示）和真实 API 模式（智能分析）
3. 已经部署到云端，您可以扫码随时访问体验
4. 项目展示了我的全栈开发能力：后端 Flask、前端 Bootstrap、AI 大模型集成

您现在可以扫码试用，或者我现场为您演示一下。"
```

---

## 常见问题

**Q: DeepSeek API 收费吗？**
A: 新用户有免费额度，足够面试演示使用。

**Q: 必须部署到 Vercel 吗？**
A: 不是，也可以用 Render、Railway 等其他平台。

**Q: 没有 API Key 能用吗？**
A: 可以！演示模式不需要 API Key，使用模拟数据。

**Q: 部署后访问很慢怎么办？**
A: Vercel 在国内访问速度一般，可以考虑国内云平台。

---

## 下一步

1. ✅ 获取 DeepSeek API Key
2. ✅ 创建 `.env` 文件
3. ✅ 测试本地运行
4. ✅ 上传到 GitHub
5. ✅ 部署到 Vercel
6. ✅ 生成二维码
7. ✅ 准备面试

祝你面试顺利！🎉
