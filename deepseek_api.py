"""
DeepSeek API 调用模块
用于真实的 AI 客服日志分析
"""
import os
import json
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your-api-key-here')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'


def call_deepseek_api(prompt: str, max_tokens: int = 2000) -> str:
    """
    调用 DeepSeek API 进行 AI 分析
    
    Args:
        prompt: 提示词
        max_tokens: 最大生成 token 数
    
    Returns:
        AI 生成的回复
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'system',
                'content': '你是一个专业的 AI 客服质检专家，擅长分析客服对话日志，识别问题并提供改进建议。'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': max_tokens,
        'temperature': 0.7
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"DeepSeek API 调用失败：{e}")
        return ""


def analyze_dialogues_with_api(dialogues: List[str]) -> Dict[str, Any]:
    """
    使用 DeepSeek API 分析客服对话
    
    Args:
        dialogues: 客服对话列表
    
    Returns:
        分析结果字典
    """
    # 构建分析提示词
    prompt = f"""
请分析以下客服对话日志，完成以下任务：

1. **意图识别**：识别每个对话的客户意图（如：退款、物流查询、账号问题等）
2. **Bad Case 检测**：找出服务质量差的对话，并说明原因
3. **根因分析**：分析 Bad Case 的根本原因（如：语义理解错误、多意图识别失败等）
4. **置信度评估**：对每个意图识别结果给出置信度评分（0-1）
5. **改进建议**：提供具体的优化建议

客服对话日志：
{chr(10).join(dialogues)}

请以 JSON 格式返回分析结果，格式如下：
{{
    "intents": [
        {{"dialogue_id": 1, "intent": "退款", "confidence": 0.95}},
        ...
    ],
    "bad_cases": [
        {{"dialogue_id": 2, "reason": "客服响应慢，态度差"}},
        ...
    ],
    "root_causes": {{
        "语义理解错误": 3,
        "多意图识别失败": 2,
        ...
    }},
    "suggestions": ["建议 1", "建议 2", ...]
}}
"""
    
    response = call_deepseek_api(prompt)
    
    try:
        # 解析 JSON 结果
        result = json.loads(response)
        return result
    except:
        # 如果解析失败，返回基础结构
        return {
            'intents': [],
            'bad_cases': [],
            'root_causes': {},
            'suggestions': ['API 分析失败，请检查 API Key 或网络连接']
        }


def generate_report_with_api(analysis_result: Dict[str, Any]) -> str:
    """
    使用 DeepSeek API 生成质检日报
    
    Args:
        analysis_result: 分析结果
    
    Returns:
        生成的日报文本
    """
    prompt = f"""
请根据以下 AI 分析结果，生成一份专业的客服质检日报：

分析结果：
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

日报格式要求：
# 客服质检日报
## 📊 总体概况
- 分析对话数：X 条
- Bad Case 数：X 条
- 平均置信度：X%

## 🎯 意图分布
（列出主要意图及占比）

## ⚠️ Bad Case 分析
（详细分析每个 Bad Case）

## 🔍 根因分析
（分析问题的根本原因）

## 💡 改进建议
（提供具体的优化建议）

请生成专业、详细的日报内容。
"""
    
    return call_deepseek_api(prompt)


# 测试函数
if __name__ == '__main__':
    # 测试 API 调用
    test_dialogues = [
        "用户：我想退款\n客服：好的，请问订单号是多少？",
        "用户：物流怎么还没到\n客服：我帮您查询一下"
    ]
    
    result = analyze_dialogues_with_api(test_dialogues)
    print("分析结果:", result)
