from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import db_session, require_auth
from app.models import Profile

router = APIRouter(prefix="/api/profiles", tags=["profiles"], dependencies=[Depends(require_auth)])


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ProfileCreate(BaseModel):
    name: str


@router.get("", response_model=list[ProfileOut])
def list_profiles(session: Session = Depends(db_session)) -> list[Profile]:
    return list(session.scalars(select(Profile)).all())


@router.post("", response_model=ProfileOut)
def create_profile(body: ProfileCreate, session: Session = Depends(db_session)) -> Profile:
    profile = Profile(name=body.name.strip())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
