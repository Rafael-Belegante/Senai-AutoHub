
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.security import clear_session_cookie, create_session_cookie, verify_password
from app.db.session import get_db
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == email, User.is_active == True)
        .first()
    )

    if not user or not verify_password(password, user.password_hash):
        # Mensagem genérica para evitar enumeração de usuários
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Credenciais inválidas."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Atualiza metadados de login
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.client.host if request.client else None
    user.last_login_ua = request.headers.get("user-agent", "")[:255]
    db.add(user)
    db.commit()

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    create_session_cookie({"uid": user.id, "role": user.role.value}, response)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    clear_session_cookie(response)
    return response
