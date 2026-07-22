from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Hypothesis(BaseModel):
    rank: int
    title: str
    root_cause_id: str
    confidence: Confidence
    facts: list[str] = Field(default_factory=list)
    inferences: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    suggested_diagnostics: list[str] = Field(default_factory=list)
    dangerous: bool = False


class AssistantRequest(BaseModel):
    incident_id: str
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    telemetry_summary: dict[str, Any] = Field(default_factory=dict)
    deployment: dict[str, Any] = Field(default_factory=dict)
    runbook_excerpts: list[str] = Field(default_factory=list)
    mode: Literal["fixture", "live"] = "fixture"


class AssistantResponse(BaseModel):
    incident_id: str
    mode: str
    hypotheses: list[Hypothesis]
    refused_actions: list[str] = Field(default_factory=list)
    model_provider: Optional[str] = "deterministic-fixture"
    model_version: Optional[str] = "0.1.0"
    latency_ms: int = 0
    token_consumption: int = 0
    estimated_cost_usd: float = 0.0
    notes: list[str] = Field(default_factory=list)
