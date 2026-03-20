# AI 客服质检系统

一个基于 **DeepSeek 大模型** 的智能客服质检系统，支持自动化客服日志分析、Bad Case 检测、根因分析和质检日报生成。

## 🌟 功能特性

- 🤖 **AI 意图识别** - 使用 DeepSeek 大模型智能识别客户意图
- ⚠️ **Bad Case 检测** - 自动检测服务质量问题对话
- 📊 **根因分析** - 分析问题根本原因（语义理解错误、多意图识别失败等）
- 📈 **置信度评估** - 对每个识别结果给出置信度评分
- 📝 **自动报告生成** - 生成专业的质检日报
- 🎨 **可视化展示** - Bootstrap + Chart.js 图表展示
- 🔄 **双模式支持** - 演示模式（模拟数据）和真实 API 模式

## 🎯 演示模式 vs 真实 API 模式

| 特性 | 演示模式 | 真实 API 模式 |
|------|----------|--------------|
| 数据源 | 模拟生成 | 真实客服日志 |
| 分析引擎 | 规则匹配 | DeepSeek 大模型 |
| API Key | 不需要 | 需要 |
| 适用场景 | 快速演示、面试展示 | 真实业务分析 |
| 响应速度 | 快（2 秒） | 中等（5-10 秒） |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
# DeepSeek API Key（真实 API 模式需要）
DEEPSEEK_API_KEY=sk-your-api-key-here

# 是否使用真实 API（false=演示模式，true=真实模式）
USE_REAL_API=false
```

### 3. 启动服务

```bash
python flask_app.py
```

访问 http://127.0.0.1:5001

## 📁 项目结构

```
tongji/
├── flask_app.py          # Flask Web 应用（主程序）
├── deepseek_api.py       # DeepSeek API 调用模块
├── agents.py             # Agent 逻辑（数据生成、标注、分析、报告）
├── models.py             # 数据模型定义
├── config.py             # 配置管理
├── templates/
│   └── index.html        # 前端页面（UI + JavaScript）
├── output/               # 生成的报告
├── requirements.txt      # Python 依赖
├── vercel.json           # Vercel 部署配置
├── .env.example          # 环境变量示例
└── README.md             # 项目说明
```

## 🌐 在线体验

已部署到 Vercel，扫码访问：

![二维码](qrcode.png)

或访问：https://your-project.vercel.app

## 🔧 使用说明

### 演示模式（默认）

1. 选择演示模式（20 条/50 条/100 条）
2. 选择行业（电商/金融/物流等）
3. 点击"生成并分析"
4. 查看分析结果和图表

### 真实 API 模式

1. 在 `.env` 文件中设置 `USE_REAL_API=true`
2. 配置 `DEEPSEEK_API_KEY`
3. 重启服务
4. 输入真实客服日志或生成模拟数据
5. 点击"分析"，使用 DeepSeek 大模型进行真实分析

## 📊 功能展示

### 1. 核心痛点排行榜
展示 TOP 5 客户问题类型及占比

### 2. Bad Case 根因分析
- Bad Case 根因分布图
- 问题类型详细分布

### 3. 置信度分布分析
- 模型不确定性分析
- 高/中/低置信度分布

### 4. AI 模型评测核心指标
- 意图识别准确率
- Bad Case 检出率
- 覆盖率
- 置信度分布

### 5. 质检日报
自动生成专业的 Markdown 格式质检日报

### 6. 商业价值展示
- 节省人工时间
- 节省成本
- 效率提升
- 预估年化收益

## 🛠️ 技术栈

- **后端**: Flask 3.0
- **AI**: DeepSeek 大模型 API
- **前端**: HTML5 + Bootstrap 5 + Chart.js 4.4
- **数据**: Pandas + NumPy
- **图表**: Matplotlib + Chart.js
- **配置**: python-dotenv + pydantic

## 📦 依赖

```txt
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
pandas==2.1.4
matplotlib==3.8.2
qrcode==7.4.2
Pillow==10.1.0
```

## 🚀 部署到云端

### Vercel 部署

1. 上传到 GitHub
2. 访问 https://vercel.com 导入项目
3. 配置环境变量：
   - `DEEPSEEK_API_KEY`: 你的 DeepSeek API Key
   - `USE_REAL_API`: `false`（演示模式）
4. 点击 Deploy，等待部署完成
5. 生成访问二维码

详见 [QUICK_START.md](QUICK_START.md)

## 🎓 面试亮点

1. ✅ **AI 大模型集成** - 展示 DeepSeek API 调用能力
2. ✅ **双模式设计** - 演示模式快速展示，真实模式智能分析
3. ✅ **全栈开发** - 后端 Flask + 前端 Bootstrap + AI 集成
4. ✅ **云端部署** - Vercel 部署，24 小时在线
5. ✅ **商业思维** - 展示 AI 带来的商业价值（节省成本、提升效率）

## 📝 API 接口

### POST /generate_and_analyze

生成模拟数据并分析

```json
{
  "num_items": 20,
  "include_extreme_bad_cases": false,
  "industry": "电商",
  "demo_mode": "daily",
  "use_api": false
}
```

### POST /analyze

分析真实客服日志

```json
{
  "user_input": "客服对话日志..."
}
```

### GET /download_report

下载质检日报（Markdown 格式）

### GET /download_chart

下载图表（PNG 格式）

## 🔑 获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com
2. 注册账号并登录
3. 在控制台创建 API Key
4. 新用户有免费额度

## 📄 许可证

MIT License

##  贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请提交 Issue 或联系作者。

---

**项目亮点总结**：这是一个完整的 AI 质检系统，展示了从数据生成、AI 分析、可视化到报告生成的全流程。支持演示和真实两种模式，适合面试展示和实际业务使用。已部署到云端，扫码即可体验。
