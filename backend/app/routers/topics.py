from fastapi import APIRouter, Depends, HTTPException
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
    is_active: bool


class TopicCreate(BaseModel):
    name: str
    display_name: str | None = None


class TopicUpdate(BaseModel):
    is_active: bool


@router.get("", response_model=list[TopicOut])
def list_topics(
    include_inactive: bool = False, session: Session = Depends(db_session)
) -> list[Topic]:
    query = select(Topic)
    if not include_inactive:
        query = query.where(Topic.is_active.is_(True))
    return list(session.scalars(query.order_by(Topic.display_name)).all())


@router.post("", response_model=TopicOut)
def create_topic(body: TopicCreate, session: Session = Depends(db_session)) -> Topic:
    name = body.name.strip()
    existing = session.scalar(select(Topic).where(Topic.name == name))
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Topic '{name}' already exists")

    topic = Topic(name=name, display_name=(body.display_name or name).strip())
    session.add(topic)
    session.commit()
    session.refresh(topic)
    return topic


@router.patch("/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, body: TopicUpdate, session: Session = Depends(db_session)) -> Topic:
    topic = session.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic.is_active = body.is_active
    session.commit()
    session.refresh(topic)
    return topic
