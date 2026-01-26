
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class Capability(str, Enum):
    CODE = "code"
    IF = "IF"
    MATH = "math"
    EXPERT = "expert"
    SAFETY = "safety"

class CapabilityRanks(BaseModel):
    """模型在各项能力上的排名"""
    math: int = Field(..., ge=1, description="Math capability ranking")
    code: int = Field(..., ge=1, description="Code capability ranking")
    if_rank: int = Field(..., ge=1, description="IF capability ranking")
    expert: int = Field(..., ge=1, description="Expert capability ranking")
    safety: int = Field(..., ge=1, description="Safety capability ranking")
    
    @classmethod
    def from_list(cls, ranks_list):
        """从列表创建CapabilityRanks实例"""
        if isinstance(ranks_list, list) and len(ranks_list) >= 5:
            return cls(
                math=ranks_list[0],
                code=ranks_list[1],
                if_rank=ranks_list[2],
                expert=ranks_list[3],
                safety=ranks_list[4]
            )
        elif isinstance(ranks_list, dict):
            # 处理字典中的键名不匹配问题
            return cls(
                math=ranks_list.get('math'),
                code=ranks_list.get('code'),
                if_rank=ranks_list.get('if_rank'),
                expert=ranks_list.get('expert'),
                safety=ranks_list.get('safety')
            )
        else:
            raise ValueError("Invalid capability ranks format")


class ModelRegistration(BaseModel):
    name: str = Field(..., description="Model name")
    capability_ranks: CapabilityRanks = Field(..., description="Capability rankings for the model")
    max_tokens: int = Field(..., description="Maximum tokens the model can process")
    avg_latency_ms: int = Field(..., description="Average latency in milliseconds")
    cost_per_1k_usd: float = Field(..., description="Cost per 1K tokens in USD")
    stake_eth: float = Field(..., description="Stake in ETH for quality guarantee")

class ModelInfo(BaseModel):
    id: str
    name: str
    capability_ranks: CapabilityRanks
    capability_vector: List[float] = Field(default_factory=list, description="Ability matrix")
    max_tokens: Optional[int] = 8192
    avg_latency_ms: Optional[int] = 1000
    cost_per_1k_usd: Optional[float] = 0.01
    stake_eth: Optional[float] = 10.0
    is_verified: Optional[bool] = False
    trust_score: Optional[float] = 50.0
    registration_time: Optional[datetime] = None
    violations: Optional[int] = 0

class RoutingDecision(BaseModel):
    model_id: str
    model_name: str
    timestamp: datetime
    user_query: str
    selected_reason: str

class RoutingBatch(BaseModel):
    period: str = Field(..., description="Time period (e.g., '2025-01-15-14:00')")
    total_requests: int
    routing_merkle_root: str
    top_models: List[dict]

class PerformanceReport(BaseModel):
    model_id: str
    period: str
    avg_latency_ms: int
    success_rate: float
    uptime_percentage: float
    violations: int = 0

class ViolationReport(BaseModel):
    model_id: str
    issue: str
    severity: str  # HIGH, MEDIUM, LOW
    slash_amount_eth: float

class TrustScoreUpdate(BaseModel):
    model_id: str
    new_score: float
    update_reason: str
