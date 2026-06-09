from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    AISummary,
    ActivityLog,
    CompanyResearch,
    Lead,
    LeadIntelligence,
    LeadScore,
    LeadStatus,
    OutreachMessage,
)
from app.db.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, db: Session):
        super().__init__(db, Lead)

    def create_lead(
        self,
        owner_id: UUID,
        name: str,
        email: str,
        company: str,
        role: str | None = None,
        website: str | None = None,
        notes: str | None = None,
    ) -> Lead:
        lead = Lead(
            owner_id=owner_id,
            name=name,
            email=email,
            company=company,
            role=role,
            website=website,
            notes=notes,
        )
        return self.create(lead)

    def list_by_owner(
        self, owner_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Lead], int]:
        offset = (page - 1) * page_size
        stmt = (
            select(Lead)
            .where(Lead.owner_id == owner_id)
            .order_by(Lead.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        count_stmt = select(func.count()).select_from(Lead).where(Lead.owner_id == owner_id)
        leads = list(self.db.execute(stmt).scalars().all())
        total = self.db.execute(count_stmt).scalar_one()
        return leads, total

    def get_detail(self, lead_id: UUID, owner_id: UUID) -> Lead | None:
        stmt = (
            select(Lead)
            .where(Lead.id == lead_id, Lead.owner_id == owner_id)
            .options(
                joinedload(Lead.company_research),
                joinedload(Lead.lead_intelligence),
                joinedload(Lead.lead_score),
                joinedload(Lead.outreach_messages),
                joinedload(Lead.ai_summary),
                joinedload(Lead.activity_logs),
            )
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def update_status(self, lead: Lead, status: LeadStatus) -> Lead:
        lead.status = status
        return self.update(lead)

    def log_activity(
        self,
        lead_id: UUID,
        action: str,
        details: str | None = None,
        metadata: dict | None = None,
    ) -> ActivityLog:
        log = ActivityLog(
            lead_id=lead_id,
            action=action,
            details=details,
            metadata_=metadata,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def save_company_research(self, lead_id: UUID, data: dict) -> CompanyResearch:
        research = CompanyResearch(lead_id=lead_id, **data)
        self.db.add(research)
        self.db.commit()
        self.db.refresh(research)
        return research

    def save_lead_intelligence(self, lead_id: UUID, data: dict) -> LeadIntelligence:
        intelligence = LeadIntelligence(lead_id=lead_id, **data)
        self.db.add(intelligence)
        self.db.commit()
        self.db.refresh(intelligence)
        return intelligence

    def save_lead_score(self, lead_id: UUID, data: dict) -> LeadScore:
        score = LeadScore(lead_id=lead_id, **data)
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def save_outreach_messages(
        self, lead_id: UUID, messages: list[dict]
    ) -> list[OutreachMessage]:
        objs = [OutreachMessage(lead_id=lead_id, **msg) for msg in messages]
        self.db.add_all(objs)
        self.db.commit()
        for obj in objs:
            self.db.refresh(obj)
        return objs

    def save_ai_summary(self, lead_id: UUID, data: dict) -> AISummary:
        summary = AISummary(lead_id=lead_id, **data)
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        return summary
