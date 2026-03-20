from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator
from pydantic.main import IncEx


class FeedbackLabel(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class ErrorCategory(str, Enum):
    LOGICAL_TURN = "Logical_Turn"
    AMBIGUOUS_INTENT = "Ambiguous_Intent"
    NEW_TOPIC = "New_Topic"
    INTENT_MISMATCH = "Intent_Mismatch"
    LOW_CONFIDENCE = "Low_Confidence"
    OTHER = "Other"


class DialogueItem(BaseModel):
    """单条客服对话日志（抽象为一轮）"""

    dialogue_id: str = Field(..., description="对话唯一 ID")
    timestamp: datetime = Field(..., description="对话时间")
    user_query: str = Field(..., description="用户原始问句")
    predicted_intent: str = Field(..., description="模型预测意图")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="意图识别置信度")
    feedback: FeedbackLabel = Field(..., description="人工或系统反馈标签")


class LabeledCase(BaseModel):
    """标注后的用户问题"""

    dialogue_id: str
    user_query: str
    category: str = Field(..., description="问题类别")
    anger_score: int = Field(..., ge=1, le=10, description="用户愤怒指数")
    is_recurring: bool = Field(..., description="是否为重复问题")
    summary: str = Field(..., description="问题摘要")
    urgency: str = Field(..., description="紧急度：高/中/低")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")


class Metrics(BaseModel):
    """统计分析结果"""

    total_dialogues: int
    total_bad_cases: int
    top_pain_points: List[Dict[str, Any]] = Field(
        ..., description="TOP 5 痛点及出现次数"
    )
    avg_anger_level: float = Field(..., ge=1.0, le=10.0, description="平均用户愤怒指数")
    repetition_rate: float = Field(..., ge=0.0, le=1.0, description="重复问题率")
    urgency_distribution: Dict[str, float] = Field(
        ..., description="紧急度分布（高/中/低）"
    )
    generated_at: datetime
    error_dist_image_path: Optional[str] = None
    
    @field_validator('urgency_distribution')
    @classmethod
    def validate_urgency_distribution(cls, v: Dict[str, float]) -> Dict[str, float]:
        """验证紧急度分布的和约为 1"""
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # 允许微小误差
            raise ValueError('紧急度分布的和必须约为 1')
        return v
    
    @field_validator('total_dialogues', 'total_bad_cases')
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """验证非负整数"""
        if v < 0:
            raise ValueError('必须是非负整数')
        return v


class WorkflowState(BaseModel):
    """
    LangGraph 的 State 定义

    使用 BaseModel 替代 TypedDict，以便利用 Pydantic 的默认值和验证功能。
    """
    
    raw_data: List[DialogueItem] = Field(default_factory=list, description="原始对话数据")
    labeled_cases: List[LabeledCase] = Field(default_factory=list, description="标注后的 Bad Case")
    metrics: Optional[Metrics] = Field(default=None, description="统计分析结果")
    final_report: Optional[str] = Field(default=None, description="最终报告")
    
    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """重写 dict 方法，确保与 LangGraph 兼容"""
        return super().dict(*args, **kwargs)
    
    def get(self, key: str, default: Any = None) -> Any:
        """添加 get 方法，确保与 TypedDict 兼容"""
        return getattr(self, key, default)



