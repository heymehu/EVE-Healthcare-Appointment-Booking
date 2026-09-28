from sqlalchemy.orm import Session

from app.core.exceptions import conflict, unauthorized
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserOut


class AuthService:
    def signup(self, db: Session, payload: UserCreate) -> User:
        existing = db.query(User).filter(User.email == payload.email.lower()).first()
        if existing:
            raise conflict("An account with this email already exists")
        user = User(
            name=payload.name.strip(),
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, payload: LoginRequest) -> TokenResponse:
        user = db.query(User).filter(User.email == payload.email.lower()).first()
        if user is None or not verify_password(payload.password, user.password_hash):
            raise unauthorized("Invalid email or password")
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=UserOut.model_validate(user))


auth_service = AuthService()
