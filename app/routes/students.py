from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import require_professor_or_admin
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/manage", response_class=HTMLResponse)
def manage_students(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    students = db.query(User).filter(User.role == UserRole.STUDENT).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(
        "students/manage.html",
        {"request": request, "students": students},
    )


@router.get("/new", response_class=HTMLResponse)
def new_student_form(
    request: Request,
    current_user: User = Depends(require_professor_or_admin),
):
    return templates.TemplateResponse(
        "students/form.html",
        {"request": request, "error": None, "student": None},
    )


@router.post("/new", response_class=HTMLResponse)
def create_student(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    email = email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "students/form.html",
            {
                "request": request,
                "error": "Já existe um usuário com esse e-mail.",
                "student": {"name": name, "email": email},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    student = User(
        name=name.strip(),
        email=email,
        password_hash=hash_password(password),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db.add(student)
    db.commit()

    return RedirectResponse(url="/students/manage", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{student_id}/edit", response_class=HTMLResponse)
def edit_student_form(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    student = db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()
    if not student:
        return RedirectResponse(url="/students/manage", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "students/form.html",
        {"request": request, "error": None, "student": student},
    )


@router.post("/{student_id}/edit", response_class=HTMLResponse)
def update_student(
    request: Request,
    student_id: int,
    name: str = Form(...),
    email: str = Form(...),
    password: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    student = db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()
    if not student:
        return RedirectResponse(url="/students/manage", status_code=status.HTTP_303_SEE_OTHER)

    email = email.strip().lower()
    email_owner = db.query(User).filter(User.email == email).first()
    if email_owner and email_owner.id != student.id:
        return templates.TemplateResponse(
            "students/form.html",
            {
                "request": request,
                "error": "Já existe um usuário com esse e-mail.",
                "student": student,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    student.name = name.strip()
    student.email = email
    if password:
        student.password_hash = hash_password(password)

    db.add(student)
    db.commit()

    return RedirectResponse(url="/students/manage", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{student_id}/delete")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    student = db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()
    if not student:
        return RedirectResponse(url="/students/manage", status_code=status.HTTP_303_SEE_OTHER)

    student.is_active = False
    db.add(student)
    db.commit()

    return RedirectResponse(url="/students/manage", status_code=status.HTTP_303_SEE_OTHER)
