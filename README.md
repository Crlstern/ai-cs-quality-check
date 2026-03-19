# CS-Analytics-Squad (客服分析小队)

一个基于 **LangGraph StateGraph** 的多 Agent Demo，用于自动化客服日志质检、Bad Case 分析和日报生成。

## 技术栈

- Python 3.9+
- LangGraph (`StateGraph`)
- LangChain + ChatOpenAI（兼容 DeepSeek / Azure OpenAI 接口风格）
- Pydantic（数据模型）
- Pandas（统计分析）
- Matplotlib（生成错误分布饼图）

## 目录结构

- `main.py`：入口文件，构建并运行整个 StateGraph。
- `models.py`：Pydantic 数据结构与 State 定义。
- `agents.py`：4 个核心 Agent 的业务逻辑。
- `output/`：运行后自动创建，用于存放 `daily_report.md` 和 `error_dist.png`。

## 安装依赖

```bash
pip install -r requirements.txt
```

如需调用真实 LLM，请提前配置环境变量，例如：

```bash
set OPENAI_API_KEY=xxx        # Windows PowerShell / CMD
set OPENAI_BASE_URL=https://xxx/v1  # 如使用 DeepSeek / Azure 兼容接口
```

## 运行

```bash
python main.py
```

执行后你将获得：

- 一份保存在 `output/daily_report.md` 的 Markdown 日报；
- 一张错误类型分布饼图 `output/error_dist.png`。

