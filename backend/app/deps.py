from collections.abc import Generator

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_session


def require_auth(request: Request) -> None:
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")


def db_session() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()
