"""
FastAPI dependency injection.

WHY: Dependencies wire up services per-request with proper DB session lifecycle.
This is FastAPI's answer to Spring's @Autowired — testable, explicit, scoped.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.repositories.lead_repository import LeadRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.lead_service import LeadService

security = HTTPBearer()


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_lead_repo(db: Session = Depends(get_db)) -> LeadRepository:
    return LeadRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repo)


def get_lead_service(
    lead_repo: LeadRepository = Depends(get_lead_repo),
) -> LeadService:
    return LeadService(lead_repo)


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UUID:
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return UUID(payload["sub"])
