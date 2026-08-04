from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    pin: str


@router.post("/login")
def login(body: LoginRequest, request: Request) -> dict:
    if body.pin != settings.app_pin:
        raise HTTPException(status_code=401, detail="Incorrect PIN")
    request.session["authenticated"] = True
    return {"ok": True}


@router.post("/logout")
def logout(request: Request) -> dict:
    request.session.clear()
    return {"ok": True}


@router.get("/status")
def status(request: Request) -> dict:
    return {"authenticated": bool(request.session.get("authenticated"))}
