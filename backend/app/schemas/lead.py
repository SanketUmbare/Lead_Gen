from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.db.models import LeadStatus
from app.schemas.common import ORMBase


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    company: str = Field(min_length=1, max_length=255)
    role: str | None = None
    website: str | None = None
    notes: str | None = None


class LeadUpdate(BaseModel):
    status: LeadStatus | None = None
    notes: str | None = None


class CompanyResearchResponse(ORMBase):
    id: UUID
    company_summary: str | None
    industry: str | None
    estimated_size: str | None
    key_offerings: list[str] | None
    possible_pain_points: list[str] | None
    created_at: datetime


class LeadIntelligenceResponse(ORMBase):
    id: UUID
    probable_goals: list[str] | None
    probable_challenges: list[str] | None
    buying_authority: str | None
    authority_score: float | None
    created_at: datetime


class LeadScoreResponse(ORMBase):
    id: UUID
    score: int
    reasoning: str | None
    factors: dict[str, Any] | None
    created_at: datetime


class OutreachMessageResponse(ORMBase):
    id: UUID
    message_type: str
    subject: str | None
    body: str
    created_at: datetime


class AISummaryResponse(ORMBase):
    id: UUID
    lead_summary: str | None
    opportunity_summary: str | None
    recommended_action: str | None
    created_at: datetime


class ActivityLogResponse(ORMBase):
    id: UUID
    action: str
    details: str | None
    metadata_: dict[str, Any] | None = Field(None, alias="metadata_")
    created_at: datetime


class LeadResponse(ORMBase):
    id: UUID
    name: str
    email: str
    company: str
    role: str | None
    website: str | None
    notes: str | None
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadDetailResponse(LeadResponse):
    company_research: CompanyResearchResponse | None = None
    lead_intelligence: LeadIntelligenceResponse | None = None
    lead_score: LeadScoreResponse | None = None
    outreach_messages: list[OutreachMessageResponse] = []
    ai_summary: AISummaryResponse | None = None
    activity_logs: list[ActivityLogResponse] = []
