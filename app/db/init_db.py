
from datetime import datetime

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.material import Material
from app.models.access_log import AccessLog
from app.models.invite_token import InviteToken


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Cria admin padrão se não existir
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                name="Administrador",
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db.add(admin)
            db.commit()
            print(f"Admin padrão criado: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
        else:
            print("Admin padrão já existe.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
