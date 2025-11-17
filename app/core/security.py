
from typing import Optional, Dict

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
from fastapi import Request, Response

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_session_cookie(data: Dict, response: Response) -> None:
    """Cria cookie de sessão assinado com ID e papel do usuário."""
    token = serializer.dumps(data)
    max_age = settings.SESSION_EXPIRE_MINUTES * 60

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=False,       # alterar para True em produção com HTTPS
        samesite="Lax",
        path="/",
    )


def get_session_data(request: Request) -> Optional[Dict]:
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        return None
    try:
        data = serializer.loads(token, max_age=settings.SESSION_EXPIRE_MINUTES * 60)
        return data
    except (BadSignature, SignatureExpired):
        return None


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
