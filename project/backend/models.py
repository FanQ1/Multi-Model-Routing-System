
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
    if_rank: int = Field(..., ge=1, alias="if", description="IF capability ranking")
    expert: int = Field(..., ge=1, description="Expert capability ranking")
    safety: int = Field(..., ge=1, description="Safety capability ranking")

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
    max_tokens: int
    avg_latency_ms: int
    cost_per_1k_usd: float
    stake_eth: float
    is_verified: bool = False
    trust_score: float = 50.0
    registration_time: datetime
    violations: int = 0

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
