
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_session_data
from app.db.session import engine, get_db, SessionLocal
from app.db.base import Base
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.models.user import User
from app.models.material import Material
from app.models.backup_config import BackupConfig
from app.services.backup_service import create_backup

import asyncio
from datetime import datetime


# Garante que as tabelas existam (para execução em ambiente simples).
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Carrega usuário logado em request.state.user para uso nos templates."""

    async def dispatch(self, request, call_next):
        request.state.user = None
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            session_data = get_session_data(request)
            if session_data:
                uid = session_data.get("uid")
                if uid:
                    user = db.query(User).filter(User.id == uid).first()
                    request.state.user = user
        except Exception:
            pass
        finally:
            db.close()
        response = await call_next(request)
        return response


app.add_middleware(AuthContextMiddleware)

@app.on_event("startup")
async def start_backup_loop():
    async def backup_loop():
        while True:
            db = SessionLocal()
            try:
                cfg = db.query(BackupConfig).first()
                if cfg and cfg.enabled:
                    now = datetime.utcnow()
                    due = (
                        not cfg.last_run_at
                        or (now - cfg.last_run_at).total_seconds() >= cfg.interval_hours * 3600
                    )
                    if due:
                        backup_name = create_backup()
                        cfg.last_run_at = now
                        db.add(cfg)
                        db.commit()
                        print(f"[BACKUP] Executado automaticamente: {backup_name}")
            finally:
                db.close()

            await asyncio.sleep(60)  # checa a cada 60s

    asyncio.create_task(backup_loop())


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    q: str | None = None,
    types: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Material).filter(Material.is_active == True)

    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (Material.title.ilike(like)) | (Material.description.ilike(like))
        )

    if types:
        selected = [t for t in types.split(",") if t]
        if selected:
            query = query.filter(Material.type.in_(selected))

    materials = query.order_by(Material.created_at.desc()).limit(20).all()
    total_items = query.count()

    # Mapeia dados mínimos para o template
    view_models = []
    for m in materials:
        view_models.append({
            "id": m.id,
            "title": m.title,
            "description": m.description or "",
            "type": m.type.value,
            "author_name": m.author.name if m.author else "Desconhecido",
            "created_at": m.created_at,
        })

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "materials": view_models,
            "total_items": total_items,
            "page": 1,
            "q": q or "",
            "types": types or "",
        },
    )


from app.routes import admin, auth, materials, students

# Rotas especializadas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(materials.router, prefix="/materials", tags=["materials"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
