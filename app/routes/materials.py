
import os
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import require_professor_or_admin, get_current_user
from app.db.session import get_db
from app.models.material import Material, MaterialSourceType, MaterialType
from app.models.access_log import AccessLog
from app.models.user import User, UserRole

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads/materials")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dashboard: lista materiais do usuário (professor) ou todos (admin).
    """
    query = db.query(Material).filter(Material.is_active == True)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Material.author_id == current_user.id)

    materials = query.order_by(Material.created_at.desc()).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "materials": materials},
    )


@router.get("/new", response_class=HTMLResponse)
def new_material_form(
    request: Request,
    current_user: User = Depends(require_professor_or_admin),
):
    return templates.TemplateResponse(
        "materials/form.html",
        {"request": request, "error": None, "material": None},
    )


@router.post("/new")
def create_material(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    type: str = Form(...),
    source_type: str = Form(...),
    external_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    # Validação básica de tipo
    try:
        mat_type = MaterialType(type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tipo de material inválido.")

    try:
        src_type = MaterialSourceType(source_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Origem de material inválida.")

    file_path = None
    url = None

    if src_type == MaterialSourceType.UPLOAD:
        if not file:
            raise HTTPException(status_code=400, detail="Arquivo obrigatório para upload.")
        filename = file.filename or "material"
        safe_name = filename.replace("..", "_").replace("/", "_")
        dest = UPLOAD_DIR / safe_name
        with dest.open("wb") as f:
            f.write(file.file.read())
        file_path = str(dest)
    else:
        if not external_url:
            raise HTTPException(status_code=400, detail="URL obrigatória para material externo.")
        url = external_url.strip()

    material = Material(
        title=title.strip(),
        description=description.strip() if description else "",
        type=mat_type,
        source_type=src_type,
        file_path=file_path,
        external_url=url,
        author_id=current_user.id,
    )
    db.add(material)
    db.commit()

    return RedirectResponse(url="/materials/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{material_id}/edit", response_class=HTMLResponse)
def edit_material_form(
    request: Request,
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    material = (
        db.query(Material)
        .filter(Material.id == material_id, Material.is_active == True)
        .first()
    )
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    if current_user.role != UserRole.ADMIN and material.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para editar este material.")

    return templates.TemplateResponse(
        "materials/form.html",
        {"request": request, "error": None, "material": material},
    )


@router.post("/{material_id}/edit")
def update_material(
    request: Request,
    material_id: int,
    title: str = Form(...),
    description: str = Form(""),
    type: str = Form(...),
    source_type: str = Form(...),
    external_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    material = (
        db.query(Material)
        .filter(Material.id == material_id, Material.is_active == True)
        .first()
    )
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    if current_user.role != UserRole.ADMIN and material.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para editar este material.")

    try:
        mat_type = MaterialType(type)
        src_type = MaterialSourceType(source_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tipo ou origem inválidos.")

    material.title = title.strip()
    material.description = description.strip() if description else ""
    material.type = mat_type
    material.source_type = src_type

    if src_type == MaterialSourceType.UPLOAD:
        if file:
            filename = file.filename or "material"
            safe_name = filename.replace("..", "_").replace("/", "_")
            dest = UPLOAD_DIR / safe_name
            with dest.open("wb") as f:
                f.write(file.file.read())
            material.file_path = str(dest)
    else:
        if not external_url:
            raise HTTPException(status_code=400, detail="URL obrigatória para material externo.")
        material.external_url = external_url.strip()
        material.file_path = None

    db.add(material)
    db.commit()

    return RedirectResponse(url="/materials/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{material_id}/delete")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor_or_admin),
):
    material = (
        db.query(Material)
        .filter(Material.id == material_id, Material.is_active == True)
        .first()
    )
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    if current_user.role != UserRole.ADMIN and material.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para excluir este material.")

    material.is_active = False
    db.add(material)
    db.commit()

    return RedirectResponse(url="/materials/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{material_id}/open")
def open_material(
    request: Request,
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = (
        db.query(Material)
        .filter(Material.id == material_id, Material.is_active == True)
        .first()
    )

    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    # Log de acesso
    access = AccessLog(
        user_id=current_user.id,
        material_id=material.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    db.add(access)
    db.commit()

    if material.source_type == MaterialSourceType.URL:
        return RedirectResponse(url=material.external_url)

    if material.source_type == MaterialSourceType.UPLOAD:
        if not material.file_path or not os.path.exists(material.file_path):
            raise HTTPException(status_code=410, detail="Arquivo não está mais disponível.")
        return FileResponse(
            path=material.file_path,
            filename=os.path.basename(material.file_path),
            media_type="application/octet-stream",
        )

    raise HTTPException(status_code=500, detail="Configuração inválida de material.")
