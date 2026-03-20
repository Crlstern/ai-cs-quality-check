from __future__ import annotations

import os
import random
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import settings
from models import (
    DialogueItem,
    FeedbackLabel,
    LabeledCase,
    ErrorCategory,
    Metrics,
    WorkflowState,
)


def get_llm_client() -> Optional[ChatOpenAI]:
    """根据环境变量判断是否使用真实的 ChatOpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            return ChatOpenAI(api_key=api_key)
        except Exception as e:
            logging.warning(f"初始化 ChatOpenAI 失败：{e}")
            return None
    return None


def _ensure_output_dir() -> str:
    """确保 output 目录存在，集中管理输出路径。"""
    return settings.OUTPUT_DIR


# ========== 行业数据模板（Demo 专用）==========

# 客服回复模板
CS_RESPONSES = {
    "退款": [
        "您好，理解您的心情。请问您的订单号是多少？我帮您查询一下退款进度。",
        "非常抱歉给您带来不便。根据我们的退款政策，商品使用超过一半会影响退款金额。",
        "您好，退款申请已收到，我们会在 1-3 个工作日内处理，请您耐心等待。"
    ],
    "物流": [
        "您好，我帮您查询物流信息。请问您的订单号是多少？",
        "非常抱歉物流延误了，我帮您联系快递公司核实情况。",
        "您好，您的包裹已发出，预计 2-3 天送达，请您注意查收。"
    ],
    "投诉": [
        "非常抱歉给您带来不好的体验，您的问题我已记录，会有专员在 24 小时内联系您处理。",
        "您好，理解您的心情，我们非常重视这个问题，会立即核实并给您答复。",
        "对不起，这是我们的工作失误。为了表示歉意，我们会为您提供一张优惠券作为补偿。"
    ],
    "账号": [
        "您好，账号问题请您提供注册手机号，我帮您核实。",
        "您好，密码重置链接已发送到您的注册邮箱，请注意查收。",
        "您好，账号注销需要 7 天冷静期，期间您可以随时撤销申请。"
    ],
    "充值": [
        "您好，充错账号的情况我们需要核实交易记录，请您提供充值订单号。",
        "您好，充值成功后一般实时到账，如未到账请您提供交易截图。",
        "抱歉，充错账号无法直接转移，建议您联系对方协商退回。"
    ],
    "default": [
        "您好，请问有什么可以帮您？",
        "您好，理解您的心情，我帮您查询一下。",
        "您好，您的问题我已了解，请稍等，我为您核实。",
        "您好，感谢反馈，我们会持续改进服务质量。"
    ]
}

INDUSTRY_TEMPLATES = {
    "电商": {
        "hard_cases": [
            "我想退款但是已经用过了一半了，还能退吗？",
            "我本来是想问物流信息的，结果你给我推优惠券干嘛？",
            "我不是要退货，我是想换个尺码，你怎么直接给我退款链接？",
            "账号已经注销了但是还一直给我发短信，这个怎么解决？",
            "我说的是充错了账号，不是充错了金额，你能看清楚吗？",
            "我已经按照你说的重启三次了还是不行，还有别的办法吗？",
            "你们发的是假货，我要投诉！",
            "商品描述和实物完全不一样，这是欺诈！",
        ],
        "extreme_bad_cases": [
            "你们的服务太差了，我要投诉你们！",
            "我要退款，否则我就去消费者协会告你们！",
            "你们的产品是垃圾，根本不能用！",
            "我已经等了三个小时了，你们到底有没有人管？",
            "你们这是欺诈，我要报警！",
            "再也不来你们这买东西了，太坑了！",
        ],
        "simple_cases": [
            "你们的客服工作时间是几点到几点？",
            "怎么修改登录密码？",
            "运费是怎么计算的？",
            "帮我查一下当前订单的物流信息。",
            "你们支持花呗支付吗？",
            "多久能发货？",
            "可以开发票吗？",
        ],
        "predicted_intents": [
            "Ask_Refund", "Ask_Exchange", "Ask_Logistics", 
            "Ask_WorkingHours", "Ask_Account_Security", "Ask_Payment_Method"
        ],
        "anger_triggers": ["假货", "欺诈", "太差了", "投诉", "报警", "坑"],
    },
    "金融": {
        "hard_cases": [
            "为什么扣了我两份钱？",
            "我的额度怎么突然被降低了？",
            "我已经还款了为什么还显示逾期？",
            "这个利息是怎么计算的？太高了吧！",
            "你们未经我同意就开通了这个服务！",
            "为什么我的提现一直不到账？",
        ],
        "extreme_bad_cases": [
            "你们这是乱收费，我要去银监会投诉！",
            "欺诈！我要报警！",
            "还我血汗钱！",
            "你们和骗子有什么区别！",
            "我要曝光你们，让所有人都知道！",
        ],
        "simple_cases": [
            "怎么查看我的账单？",
            "如何修改支付密码？",
            "客服电话是多少？",
            "营业网点在哪里？",
            "如何申请信用卡？",
        ],
        "predicted_intents": [
            "Ask_Billing", "Ask_Credit", "Ask_Repayment", 
            "Ask_Interest", "Ask_Withdrawal", "Ask_Service"
        ],
        "anger_triggers": ["乱收费", "欺诈", "投诉", "银监会", "报警", "骗子"],
    },
    "教育": {
        "hard_cases": [
            "课程质量和宣传完全不一样！",
            "我想退费，你们为什么不退？",
            "老师说的内容和课程不符怎么办？",
            "这个证书国家承认吗？",
            "上课一直卡顿，怎么解决？",
            "作业批改太慢了，影响我学习！",
        ],
        "extreme_bad_cases": [
            "虚假宣传！我要退费！",
            "你们就是骗钱的培训机构！",
            "老师一点都不专业，浪费钱！",
            "我要去教育局投诉你们！",
            "退钱！不然我就曝光你们！",
        ],
        "simple_cases": [
            "课程什么时候开始？",
            "怎么查看学习进度？",
            "有教材吗？",
            "考试什么时候报名？",
            "证书多久能拿到？",
        ],
        "predicted_intents": [
            "Ask_Course", "Ask_Refund", "Ask_Teacher", 
            "Ask_Certificate", "Ask_Technical", "Ask_Homework"
        ],
        "anger_triggers": ["虚假宣传", "骗钱", "不专业", "投诉", "曝光", "退钱"],
    },
    "游戏": {
        "hard_cases": [
            "我的账号怎么被封了？",
            "充值的点券为什么没到账？",
            "这个活动是不是有内幕？",
            "匹配机制太不公平了！",
            "游戏 BUG 导致我输了，怎么补偿？",
            "装备强化失败能不能恢复？",
        ],
        "extreme_bad_cases": [
            "你们游戏就是骗氪的垃圾！",
            "我要去消协投诉你们！",
            "退钱！再也不玩了！",
            "这游戏平衡性做给狗吃的？",
            "官方出来挨打！",
        ],
        "simple_cases": [
            "怎么创建角色？",
            "新手礼包怎么领？",
            "等级怎么提升？",
            "怎么加好友？",
            "公会怎么加入？",
        ],
        "predicted_intents": [
            "Ask_Account", "Ask_Payment", "Ask_Event", 
            "Ask_Matchmaking", "Ask_Bug", "Ask_Equipment"
        ],
        "anger_triggers": ["骗氪", "垃圾", "投诉", "退钱", "不公平", "BUG"],
    },
}

# ========== 演示模式配置 ==========

DEMO_MODES = {
    "daily": {
        "name": "日常模式",
        "num_items": 20,
        "bad_ratio": 0.3,
        "include_extreme": False,
        "description": "模拟日常运营数据，适合日常监控"
    },
    "promotion": {
        "name": "大促模式",
        "num_items": 50,
        "bad_ratio": 0.5,
        "include_extreme": False,
        "description": "模拟双 11/618 等大促期间数据，问题量增加"
    },
    "crisis": {
        "name": "危机模式",
        "num_items": 100,
        "bad_ratio": 0.7,
        "include_extreme": True,
        "description": "模拟公关危机/产品故障场景，大量 Bad Case"
    },
}


def generate_mock_dialogues(
    num_items: int = 20, 
    bad_ratio: float = 0.3, 
    include_extreme_bad_cases: bool = False,
    industry: str = "电商"
) -> List[DialogueItem]:
    """
    生成高质量 Mock 客服对话数据（Demo 增强版）。

    设计思路（PM 视角）：
    - 同时覆盖「简单问答」和「带逻辑转折 / 退款 / 投诉」等高难样本；
    - Bad Case 通过「高置信度 + 负反馈」以及"语义转折但被简单意图覆盖"来模拟。
    - 支持多行业数据模板，适配不同演示场景
    """
    now = datetime.now()
    dialogues: List[DialogueItem] = []

    # 获取行业模板
    template = INDUSTRY_TEMPLATES.get(industry, INDUSTRY_TEMPLATES["电商"])
    
    hard_cases = template["hard_cases"].copy()
    extreme_bad_cases = template["extreme_bad_cases"].copy()
    simple_cases = template["simple_cases"].copy()
    predicted_intents_pool = template["predicted_intents"]

    # 如果包含极端 Bad Case，将其添加到 hard_cases 中
    if include_extreme_bad_cases:
        hard_cases.extend(extreme_bad_cases)

    num_bad = int(num_items * bad_ratio)

    for i in range(num_items):
        is_bad = i < num_bad
        if is_bad and hard_cases:
            query = hard_cases[i % len(hard_cases)]
        else:
            # 混合作为"正常样本"或"轻微问题样本"
            pool = hard_cases + simple_cases
            query = random.choice(pool)

        predicted_intent = random.choice(predicted_intents_pool)
        # Bad Case：高置信度但负反馈；否则随机
        if is_bad:
            confidence = round(random.uniform(0.85, 0.99), 2)
            feedback = FeedbackLabel.negative
        else:
            confidence = round(random.uniform(0.6, 0.98), 2)
            feedback = random.choices(
                [FeedbackLabel.positive, FeedbackLabel.neutral, FeedbackLabel.negative],
                weights=[0.6, 0.25, 0.15],
                k=1,
            )[0]

        ts = now - timedelta(minutes=random.randint(0, 24 * 60))
        dialogues.append(
            DialogueItem(
                dialogue_id=f"dlg_{i+1:03d}",
                timestamp=ts,
                user_query=query,
                predicted_intent=predicted_intent,
                confidence_score=confidence,
                feedback=feedback,
            )
        )

    return dialogues


def format_dialogue_with_cs_response(dialogue: DialogueItem) -> str:
    """
    将用户问题格式化为完整的客服对话（包含时间戳和客服回复）
    """
    user_query = dialogue.user_query
    timestamp = dialogue.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    # 根据用户问题内容匹配合适的客服回复
    cs_response = CS_RESPONSES["default"][0]  # 默认回复
    if "退款" in user_query or "退货" in user_query:
        cs_response = random.choice(CS_RESPONSES["退款"])
    elif "物流" in user_query or "快递" in user_query:
        cs_response = random.choice(CS_RESPONSES["物流"])
    elif "投诉" in user_query or "垃圾" in user_query or "欺诈" in user_query:
        cs_response = random.choice(CS_RESPONSES["投诉"])
    elif "账号" in user_query or "密码" in user_query or "登录" in user_query:
        cs_response = random.choice(CS_RESPONSES["账号"])
    elif "充错" in user_query or "充值" in user_query:
        cs_response = random.choice(CS_RESPONSES["充值"])
    
    # 格式化对话
    dialogue_text = f"""[{timestamp}] 用户：{user_query}
[{timestamp}] 客服：{cs_response}
"""
    return dialogue_text


def data_hunter_node(state: WorkflowState) -> WorkflowState:
    """DataHunter：模拟从数据库中抽取昨日日志（Demo 增强版）。"""
    try:
        # 从状态中获取配置参数
        num_items = state.get("num_items", 20)
        include_extreme_bad_cases = state.get("include_extreme_bad_cases", False)
        industry = state.get("industry", "电商")
        
        # 调整 bad_ratio if include_extreme_bad_cases
        bad_ratio = 0.5 if include_extreme_bad_cases else 0.3
        
        dialogues = generate_mock_dialogues(
            num_items=num_items, 
            bad_ratio=bad_ratio, 
            include_extreme_bad_cases=include_extreme_bad_cases,
            industry=industry
        )
        # StateGraph 要求返回"局部更新"，不覆盖整个 state。
        return {"raw_data": dialogues}
    except Exception as e:
        # 如果数据获取失败，为了不中断整体流程，返回空列表并记录异常。
        logging.error(f"[DataHunter] 发生异常，将返回空数据：{e}")
        return {"raw_data": []}


# ========== LabelingSpecialist ==========


def _mock_label_with_cot(dialogue: DialogueItem) -> LabeledCase:
    """
    使用启发式规则模拟 CoT 标注过程，相当于一个本地的"Mock LLM"。

    这样设计的原因：
    - 避免依赖真实 LLM / API Key；
    - 仍然能体现"先分析再给结论"的分析思路；
    - 未来接入 LLM 时，只需要把这块替换成真实调用即可。
    """
    text = dialogue.user_query

    # 意图识别：业务类别
    if "退款" in text or "退货" in text:
        category = "支付/退款"
    elif "物流" in text or "快递" in text or "配送" in text:
        category = "物流/配送"
    elif "账号" in text or "密码" in text or "登录" in text or "注销" in text:
        category = "账号管理"
    elif "充错" in text or "充值" in text:
        category = "支付/充值"
    elif "客服" in text or "服务" in text or "投诉" in text:
        category = "客户服务"
    else:
        category = "其他"

    # 情绪分析：愤怒指数 1-10
    anger_score = 1
    if "垃圾" in text or "欺诈" in text or "报警" in text:
        anger_score = 10
    elif "投诉" in text or "告你们" in text:
        anger_score = 9
    elif "太差了" in text or "到底有没有人管" in text:
        anger_score = 8
    elif "不能" in text or "不行" in text or "看清楚" in text:
        anger_score = 7
    elif "但是" in text or "不过" in text:
        anger_score = 5

    # 去重标记：是否与常见问题语义相似
    recurring_patterns = ["充错账号", "注销后发短信", "重启三次", "退款", "物流信息"]
    is_recurring = any(pattern in text for pattern in recurring_patterns)

    # 紧急度评估
    if "充错" in text or "退款" in text or "欺诈" in text:
        urgency = "高"
    elif "物流" in text or "账号" in text:
        urgency = "中"
    else:
        urgency = "低"

    # 问题摘要
    summary = text[:50] + "..." if len(text) > 50 else text

    return LabeledCase(
        dialogue_id=dialogue.dialogue_id,
        user_query=dialogue.user_query,
        category=category,
        anger_score=anger_score,
        is_recurring=is_recurring,
        summary=summary,
        urgency=urgency,
        metadata={}
    )


async def labeling_specialist_node(state: WorkflowState) -> WorkflowState:
    """
    LabelingSpecialist：对用户问题进行分类和情绪分析。

    如果 LLM 客户端存在，使用真实 LLM 进行标注；否则使用本地启发式逻辑作为 Fallback。
    """
    raw_data: List[DialogueItem] = state.get("raw_data", []) or []
    if not raw_data:
        logging.info("[LabelingSpecialist] 无原始数据，跳过标注。")
        return {"labeled_cases": []}

    # 对所有用户问题进行标注，不再仅针对 Bad Case
    llm_client = get_llm_client()
    labeled: List[LabeledCase] = []

    for dlg in raw_data:
        if llm_client:
            try:
                # 构造标准的 LangChain Prompt Template 调用 LLM 进行标注
                prompt = ChatPromptTemplate.from_template("""
你是一位资深的用户声音 (VoC) 分析专家，需要对以下用户问题进行深度分析。

请按照以下步骤进行分析：
1. 仔细阅读用户问题
2. 确定问题类别（从以下选项中选择：支付/退款、物流/配送、账号管理、支付/充值、客户服务、其他）
3. 评估用户愤怒指数（1-10，1 表示平静，10 表示极度愤怒）
4. 判断该问题是否与常见问题语义高度相似（是否为重复问题）
5. 评估问题紧急度（高/中/低）
6. 提供问题摘要

用户问题：{user_query}

请输出严格的 JSON 格式，包含以下字段：
{{
  "category": "问题类别",
  "anger_score": 1-10,
  "is_recurring": true/false,
  "urgency": "高/中/低",
  "summary": "问题摘要"
}}
""")
                
                chain = prompt | llm_client
                response = await chain.ainvoke({
                    "user_query": dlg.user_query
                })
                
                # 解析 LLM 响应
                import json
                response_text = response.content
                # 提取 JSON 部分
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response_text[json_start:json_end]
                    try:
                        llm_output = json.loads(json_str)
                        category = llm_output.get("category", "其他")
                        anger_score = llm_output.get("anger_score", 1)
                        is_recurring = llm_output.get("is_recurring", False)
                        urgency = llm_output.get("urgency", "低")
                        summary = llm_output.get("summary", dlg.user_query)
                    except json.JSONDecodeError:
                        logging.warning("LLM 输出不是有效的 JSON，使用 fallback 逻辑")
                        labeled_case = _mock_label_with_cot(dlg)
                        labeled.append(labeled_case)
                        continue
                else:
                    logging.warning("LLM 输出中未找到 JSON，使用 fallback 逻辑")
                    labeled_case = _mock_label_with_cot(dlg)
                    labeled.append(labeled_case)
                    continue
                
                labeled_case = LabeledCase(
                    dialogue_id=dlg.dialogue_id,
                    user_query=dlg.user_query,
                    category=category,
                    anger_score=anger_score,
                    is_recurring=is_recurring,
                    summary=summary,
                    urgency=urgency,
                    metadata={}
                )
            except Exception as e:
                logging.warning(f"LLM 标注失败，使用 fallback 逻辑：{e}")
                labeled_case = _mock_label_with_cot(dlg)
        else:
            labeled_case = _mock_label_with_cot(dlg)
        
        labeled.append(labeled_case)

    return {"labeled_cases": labeled}


# ========== StatisticalAnalyst ==========


def statistical_analyst_node(state: WorkflowState) -> WorkflowState:
    """
    StatisticalAnalyst：计算用户声音 (VoC) 分析指标。

    设计要点：
    - 使用 pandas 做简单统计，方便日后扩展到 SQL 结果；
    - 计算 TOP 痛点、用户愤怒指数、重复问题率、紧急度分布和高频关键词；
    - 生成可视化图表。
    """
    raw_data: List[DialogueItem] = state.get("raw_data", []) or []
    labeled_cases: List[LabeledCase] = state.get("labeled_cases", []) or []

    total_dialogues = len(raw_data)
    total_bad_cases = len(labeled_cases)

    if total_dialogues == 0:
        logging.info("[StatisticalAnalyst] 无对话数据，跳过统计。")
        metrics = Metrics(
            total_dialogues=0,
            total_bad_cases=0,
            top_pain_points=[],
            avg_anger_level=0.0,
            repetition_rate=0.0,
            urgency_distribution={},
            generated_at=datetime.now(),
            error_dist_image_path=None,
        )
        return {"metrics": metrics}

    if total_bad_cases == 0:
        # 无标注数据时，返回默认值
        metrics = Metrics(
            total_dialogues=total_dialogues,
            total_bad_cases=0,
            top_pain_points=[],
            avg_anger_level=0.0,
            repetition_rate=0.0,
            urgency_distribution={},
            generated_at=datetime.now(),
            error_dist_image_path=None,
        )
        return {"metrics": metrics}

    try:
        df = pd.DataFrame([c.dict() for c in labeled_cases])
        
        # 1. 计算 TOP 5 痛点
        category_counts = df["category"].value_counts()
        top_pain_points = []
        for category, count in category_counts.head(5).items():
            top_pain_points.append({
                "category": category,
                "count": count,
                "percentage": round(count / total_bad_cases * 100, 1)
            })
        
        # 2. 计算平均愤怒指数
        avg_anger_level = df["anger_score"].mean()
        
        # 3. 计算重复问题率
        repetition_rate = df["is_recurring"].sum() / total_bad_cases if total_bad_cases > 0 else 0.0
        
        # 4. 计算紧急度分布
        urgency_distribution = df["urgency"].value_counts(normalize=True).to_dict()
        # 确保包含所有级别
        for level in ["高", "中", "低"]:
            if level not in urgency_distribution:
                urgency_distribution[level] = 0.0
        
        # 绘制紧急度分布饼图
        import matplotlib
        matplotlib.use('Agg')  # 非交互式后端
        import matplotlib.pyplot as plt
        
        output_dir = _ensure_output_dir()
        img_path = os.path.join(output_dir, "urgency_dist.png")

        plt.figure(figsize=(6, 6))
        labels = list(urgency_distribution.keys())
        sizes = list(urgency_distribution.values())
        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
        )
        plt.title("Urgency Distribution (VoC Analysis)")
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()

        metrics = Metrics(
            total_dialogues=total_dialogues,
            total_bad_cases=total_bad_cases,
            top_pain_points=top_pain_points,
            avg_anger_level=round(float(avg_anger_level), 2),
            repetition_rate=round(float(repetition_rate), 4),
            urgency_distribution=urgency_distribution,
            hot_keywords=hot_keywords,
            generated_at=datetime.now(),
            error_dist_image_path=img_path,
        )
        return {"metrics": metrics}
    except Exception as e:
        logging.error(f"[StatisticalAnalyst] 统计或绘图中出现异常：{e}")
        metrics = Metrics(
            total_dialogues=total_dialogues,
            total_bad_cases=total_bad_cases,
            top_pain_points=[],
            avg_anger_level=0.0,
            repetition_rate=0.0,
            urgency_distribution={},
            generated_at=datetime.now(),
            error_dist_image_path=None,
        )
        return {"metrics": metrics}


# ========== ReportWriter ==========


def _format_sample_snippets(labeled_cases: List[LabeledCase], limit: int = 3) -> str:
    """选取典型样本片段，供报告使用。"""
    snippets = []
    for case in labeled_cases[:limit]:
        snippets.append(
            f"- 对话 ID: {case.dialogue_id}\n"
            f"  - 用户问句：{case.user_query}\n"
            f"  - 预测意图：{case.predicted_intent} (conf={case.confidence_score})\n"
            f"  - 错误类型：{case.error_category.value}\n"
            f"  - 根因分析：{case.root_cause}\n"
            f"  - 优化建议：{case.suggested_fix}\n"
        )
    return "\n".join(snippets)


def _mock_report(metrics: Optional[Metrics], labeled_cases: List[LabeledCase]) -> str:
    """
    使用本地模板 Mock 报告生成逻辑，模拟 LLM 写 VoC 分析报告的效果。

    方便在没有 API Key 的情况下，也能拿到结构化的 Markdown 报告。
    """
    if metrics is None or metrics.total_dialogues == 0:
        return (
            "# 用户声音 (VoC) 分析报告\n\n"
            "## 核心结论\n\n"
            "- 今日无有效用户数据。\n"
        )

    if metrics.total_bad_cases == 0:
        return (
            "# 用户声音 (VoC) 分析报告\n\n"
            "## 核心结论\n\n"
            "- 今日无用户问题数据。\n\n"
            "## 主要指标\n\n"
            f"- 总用户问题数：{metrics.total_dialogues}\n"
            "- 分析问题数：0\n\n"
        )

    # 生成 TOP 痛点文本
    top_pain_points_text = []
    for i, point in enumerate(metrics.top_pain_points, 1):
        top_pain_points_text.append(f"{i}. {point['category']}: {point['count']}次 ({point['percentage']}%)")
    top_pain_points_text = "\n".join(top_pain_points_text)

    # 生成紧急度分布文本
    urgency_dist_text = []
    for level, ratio in metrics.urgency_distribution.items():
        urgency_dist_text.append(f"- {level}：{ratio*100:.1f}%")
    urgency_dist_text = "\n".join(urgency_dist_text)

    # 生成典型问题示例
    samples_md = ""
    for case in labeled_cases[:3]:
        samples_md += f"- 问题：{case.user_query}\n"
        samples_md += f"  - 类别：{case.category}\n"
        samples_md += f"  - 愤怒指数：{case.anger_score}\n"
        samples_md += f"  - 紧急度：{case.urgency}\n"
        samples_md += f"  - 是否重复：{'是' if case.is_recurring else '否'}\n\n"

    return (
        "# 用户声音 (VoC) 分析报告\n\n"
        "## 一、核心指标摘要\n\n"
        f"- 总用户问题数：{metrics.total_dialogues}\n"
        f"- 分析问题数：{metrics.total_bad_cases}\n"
        f"- 平均愤怒指数：{metrics.avg_anger_level}\n"
        f"- 重复问题率：{metrics.repetition_rate * 100:.1f}%\n\n"
        "## 二、TOP 5 痛点\n\n"
        f"{top_pain_points_text}\n\n"
        "## 三、紧急度分布\n\n"
        f"{urgency_dist_text}\n\n"
        "## 四、典型问题示例\n\n"
        f"{samples_md}\n"
        "## 五、分析洞察\n\n"
        "- **用户痛点集中**：TOP 5 痛点占总问题的大部分，建议优先解决这些核心问题；\n"
        "- **情绪分析**：平均愤怒指数较高，说明用户对某些问题的解决不满意；\n"
        "- **重复问题**：重复问题率较高，可能存在系统性问题需要解决；\n"
        "- **紧急度分布**：高紧急度问题占比，需要优先处理涉及资金和核心功能的问题。\n"
    )


async def report_writer_node(state: WorkflowState) -> WorkflowState:
    """
    ReportWriter：生成最终 Markdown VoC 分析报告并落盘。

    如果 LLM 客户端存在，使用真实 LLM 生成报告；否则使用本地模板作为 Fallback。
    """
    labeled_cases: List[LabeledCase] = state.get("labeled_cases", []) or []
    metrics: Optional[Metrics] = state.get("metrics")

    llm_client = get_llm_client()
    if llm_client:
        try:
            # 构造标准的 LangChain Prompt Template 调用 LLM 生成报告
            prompt = ChatPromptTemplate.from_template("""
你是一位专业的用户声音 (VoC) 分析报告撰写专家，需要根据以下数据生成一份详细的分析报告。

请按照以下步骤进行分析和撰写：
1. 分析核心指标数据
2. 解读 TOP 5 痛点
3. 分析用户情绪和紧急度分布
4. 总结典型问题示例
5. 给出针对性的洞察和建议

核心指标：
- 总用户问题数：{total_dialogues}
- 分析问题数：{total_bad_cases}
- 平均愤怒指数：{avg_anger_level}
- 重复问题率：{repetition_rate}
- 紧急度分布：{urgency_distribution}
- 高频关键词：{hot_keywords}

TOP 5 痛点：
{top_pain_points}

典型问题示例：
{problem_examples}

请生成一份结构清晰、内容详实的 Markdown 格式报告，包含以下部分：
1. 核心指标摘要
2. TOP 5 痛点
3. 紧急度分布
4. 高频关键词
5. 典型问题示例
6. 分析洞察
""")
            
            # 准备数据
            total_dialogues = metrics.total_dialogues if metrics else 0
            total_bad_cases = metrics.total_bad_cases if metrics else 0
            avg_anger_level = metrics.avg_anger_level if metrics else 0.0
            repetition_rate = metrics.repetition_rate if metrics else 0.0
            
            urgency_distribution = ""
            if metrics and metrics.urgency_distribution:
                for level, ratio in metrics.urgency_distribution.items():
                    urgency_distribution += f"{level}：{ratio*100:.1f}%\n"
            
            hot_keywords = ", ".join(metrics.hot_keywords) if metrics and metrics.hot_keywords else ""
            
            top_pain_points = ""
            if metrics and metrics.top_pain_points:
                for i, point in enumerate(metrics.top_pain_points, 1):
                    top_pain_points += f"{i}. {point['category']}: {point['count']}次 ({point['percentage']}%)\n"
            
            # 生成典型问题示例
            problem_examples = ""
            for case in labeled_cases[:3]:
                problem_examples += f"- 问题：{case.user_query}\n"
                problem_examples += f"  - 类别：{case.category}\n"
                problem_examples += f"  - 愤怒指数：{case.anger_score}\n"
                problem_examples += f"  - 紧急度：{case.urgency}\n"
                problem_examples += f"  - 是否重复：{'是' if case.is_recurring else '否'}\n\n"
            
            chain = prompt | llm_client
            response = await chain.ainvoke({
                "total_dialogues": total_dialogues,
                "total_bad_cases": total_bad_cases,
                "avg_anger_level": avg_anger_level,
                "repetition_rate": repetition_rate,
                "urgency_distribution": urgency_distribution,
                "hot_keywords": hot_keywords,
                "top_pain_points": top_pain_points,
                "problem_examples": problem_examples
            })
            
            report_md = response.content
        except Exception as e:
            logging.warning(f"LLM 报告生成失败，使用 fallback 逻辑：{e}")
            report_md = _mock_report(metrics, labeled_cases)
    else:
        report_md = _mock_report(metrics, labeled_cases)

    # 写入文件
    try:
        output_dir = _ensure_output_dir()
        report_path = os.path.join(output_dir, "voc_analysis_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        logging.info(f"[ReportWriter] VoC 分析报告已生成：{report_path}")
    except Exception as e:
        logging.error(f"[ReportWriter] 写入报告文件失败：{e}")

    # 同时把报告内容放入 state 方便后续使用 / 测试
    return {"final_report": report_md}
