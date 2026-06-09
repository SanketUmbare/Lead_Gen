from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user_id, get_lead_service
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.lead import LeadCreate, LeadDetailResponse, LeadResponse, LeadUpdate
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    data: LeadCreate,
    user_id: UUID = Depends(get_current_user_id),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    Capture a new inbound lead and queue AI processing.

    The lead is stored immediately (status: new) and a Celery task
    begins the research → intelligence → scoring → outreach pipeline.
    """
    return lead_service.create_lead(user_id, data)


@router.get("", response_model=PaginatedResponse[LeadResponse])
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    lead_service: LeadService = Depends(get_lead_service),
):
    leads, total = lead_service.list_leads(user_id, page, page_size)
    return PaginatedResponse(items=leads, total=total, page=page, page_size=page_size)


@router.get("/{lead_id}", response_model=LeadDetailResponse)
def get_lead(
    lead_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    lead_service: LeadService = Depends(get_lead_service),
):
    lead = lead_service.get_lead_detail(lead_id, user_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    user_id: UUID = Depends(get_current_user_id),
    lead_service: LeadService = Depends(get_lead_service),
):
    lead = lead_service.update_lead(lead_id, user_id, data)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.post("/{lead_id}/reprocess", response_model=MessageResponse)
def reprocess_lead(
    lead_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    lead_service: LeadService = Depends(get_lead_service),
):
    success = lead_service.reprocess_lead(lead_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return MessageResponse(message="Lead reprocessing queued")
