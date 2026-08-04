from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import db_session, require_auth
from app.models import Topic

router = APIRouter(prefix="/api/topics", tags=["topics"], dependencies=[Depends(require_auth)])


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_name: str


@router.get("", response_model=list[TopicOut])
def list_topics(session: Session = Depends(db_session)) -> list[Topic]:
    return list(session.scalars(select(Topic).where(Topic.is_active.is_(True))).all())
