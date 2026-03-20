from __future__ import annotations

import os
import matplotlib.pyplot as plt
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """项目配置类"""
    # DeepSeek API 配置
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, description="DeepSeek API Key")
    DEEPSEEK_API_URL: str = Field(default="https://api.deepseek.com/v1", description="DeepSeek API 基础 URL")
    
    # OpenAI 配置（保留兼容）
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", description="OpenAI API 基础 URL")
    MODEL_NAME: str = Field(default="gpt-3.5-turbo", description="使用的模型名称")
    
    # API 开关配置
    USE_REAL_API: bool = Field(default=False, description="是否使用真实 API 分析（True=使用 DeepSeek，False=使用模拟数据）")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    
    # 输出目录配置
    OUTPUT_DIR: str = Field(default="./output", description="输出目录")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 初始化配置
settings = Settings()

# 确保输出目录存在
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

# 配置 Matplotlib 字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
