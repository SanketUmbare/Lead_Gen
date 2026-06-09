"""
Lead service — orchestrates the business logic.

WHY: The service layer sits between API routes and repositories.
Routes handle HTTP; services handle business rules; repositories handle SQL.
This separation means you can:
- Test business logic without HTTP
- Reuse logic across API + CLI + webhooks
- Change storage without touching API contracts
"""

from uuid import UUID

from app.db.models import LeadStatus
from app.db.repositories.lead_repository import LeadRepository
from app.schemas.lead import LeadCreate, LeadDetailResponse, LeadResponse, LeadUpdate
from app.tasks.lead_processing import process_lead_task


class LeadService:
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    def create_lead(self, owner_id: UUID, data: LeadCreate) -> LeadResponse:
        lead = self.lead_repo.create_lead(
            owner_id=owner_id,
            name=data.name,
            email=data.email,
            company=data.company,
            role=data.role,
            website=data.website,
            notes=data.notes,
        )
        self.lead_repo.log_activity(
            lead.id, "lead_created", f"Lead {data.name} from {data.company} captured"
        )
        process_lead_task.delay(str(lead.id))
        return LeadResponse.model_validate(lead)

    def list_leads(
        self, owner_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[LeadResponse], int]:
        leads, total = self.lead_repo.list_by_owner(owner_id, page, page_size)
        return [LeadResponse.model_validate(l) for l in leads], total

    def get_lead_detail(self, lead_id: UUID, owner_id: UUID) -> LeadDetailResponse | None:
        lead = self.lead_repo.get_detail(lead_id, owner_id)
        if not lead:
            return None
        return LeadDetailResponse.model_validate(lead)

    def update_lead(
        self, lead_id: UUID, owner_id: UUID, data: LeadUpdate
    ) -> LeadResponse | None:
        lead = self.lead_repo.get_detail(lead_id, owner_id)
        if not lead:
            return None
        if data.status:
            self.lead_repo.update_status(lead, data.status)
            self.lead_repo.log_activity(
                lead.id, "status_changed", f"Status updated to {data.status.value}"
            )
        if data.notes is not None:
            lead.notes = data.notes
            self.lead_repo.update(lead)
        return LeadResponse.model_validate(lead)

    def reprocess_lead(self, lead_id: UUID, owner_id: UUID) -> bool:
        lead = self.lead_repo.get_detail(lead_id, owner_id)
        if not lead:
            return False
        self.lead_repo.update_status(lead, LeadStatus.NEW)
        self.lead_repo.log_activity(lead.id, "reprocess_requested", "AI reprocessing queued")
        process_lead_task.delay(str(lead.id))
        return True
