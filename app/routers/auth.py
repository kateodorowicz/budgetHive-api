"""Auth routes: signup, login."""
import uuid
from typing import Annotated

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import User, Profile
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_to_response(user: User, profile: Optional[Profile]) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=profile.full_name if profile else None,
        avatar_url=profile.avatar_url if profile else None,
    )


@router.post("/signup", response_model=TokenResponse)
def signup(body: SignupRequest, db: Annotated[Session, Depends(get_db)]):
    """Create a new user and profile, return JWT."""
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    profile = Profile(id=str(uuid.uuid4()), user_id=user_id, full_name=body.full_name)
    db.add(profile)
    db.commit()
    db.refresh(user)
    db.refresh(profile)
    token = create_access_token(data={"sub": user.id})
    return TokenResponse(
        access_token=token,
        user=_user_to_response(user, profile),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    """Authenticate user, return JWT."""
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    token = create_access_token(data={"sub": user.id})
    return TokenResponse(
        access_token=token,
        user=_user_to_response(user, profile),
    )


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    """Return current user (for verifying token)."""
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    return _user_to_response(user, profile)
