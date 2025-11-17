from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.backup_config import BackupConfig
from app.services.backup_service import create_backup

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/users", response_class=HTMLResponse)
def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "users": users},
    )


@router.get("/users/new", response_class=HTMLResponse)
def new_user_form(
    request: Request,
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        "admin/user_form.html",
        {"request": request, "error": None, "user": None},
    )


@router.post("/users/new", response_class=HTMLResponse)
def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    email = email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request,
                "error": "Já existe um usuário com esse e-mail.",
                "user": {"name": name, "email": email, "role": role},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        role_enum = UserRole(role)
    except ValueError:
        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request,
                "error": "Papel inválido.",
                "user": {"name": name, "email": email, "role": role},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = User(
        name=name.strip(),
        email=email,
        password_hash=hash_password(password),
        role=role_enum,
        is_active=True,
    )
    db.add(user)
    db.commit()

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
def edit_user_form(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/user_form.html",
        {"request": request, "error": None, "user": user},
    )


@router.post("/users/{user_id}/edit", response_class=HTMLResponse)
def update_user(
    request: Request,
    user_id: int,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    password: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

    email = email.strip().lower()
    email_owner = db.query(User).filter(User.email == email).first()
    if email_owner and email_owner.id != user.id:
        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request,
                "error": "Já existe um usuário com esse e-mail.",
                "user": user,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        role_enum = UserRole(role)
    except ValueError:
        return templates.TemplateResponse(
            "admin/user_form.html",
            {
                "request": request,
                "error": "Papel inválido.",
                "user": user,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user.name = name.strip()
    user.email = email
    user.role = role_enum

    if password:
        user.password_hash = hash_password(password)

    db.add(user)
    db.commit()

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

    # Soft delete / reativação
    user.is_active = not user.is_active
    db.add(user)
    db.commit()

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)


# ------------------- Backup config -------------------


@router.get("/backup", response_class=HTMLResponse)
def backup_config_get(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cfg = db.query(BackupConfig).first()
    if not cfg:
        cfg = BackupConfig(enabled=False, interval_hours=24)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)

    return templates.TemplateResponse(
        "admin/backup.html",
        {"request": request, "config": cfg, "message": None},
    )


@router.post("/backup", response_class=HTMLResponse)
def backup_config_post(
    request: Request,
    enabled: bool | None = Form(False),
    interval_hours: int = Form(24),
    run_now: bool | None = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cfg = db.query(BackupConfig).first()
    if not cfg:
        cfg = BackupConfig()
        db.add(cfg)

    cfg.enabled = bool(enabled)
    cfg.interval_hours = max(1, interval_hours)  # pelo menos 1h

    message = "Configuração salva."

    if run_now:
        backup_name = create_backup()
        message = f"Backup executado manualmente: {backup_name}"

    db.commit()
    db.refresh(cfg)

    return templates.TemplateResponse(
        "admin/backup.html",
        {"request": request, "config": cfg, "message": message},
    )
