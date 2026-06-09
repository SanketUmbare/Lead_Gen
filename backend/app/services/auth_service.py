from uuid import UUID

from app.core.security import create_access_token, hash_password, verify_password
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserCreate, UserResponse


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, data: UserCreate) -> UserResponse:
        existing = self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")
        user = self.user_repo.create_user(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        return UserResponse.model_validate(user)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account disabled")
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token)

    def get_user(self, user_id: UUID) -> UserResponse | None:
        user = self.user_repo.get_by_id(user_id)
        return UserResponse.model_validate(user) if user else None
