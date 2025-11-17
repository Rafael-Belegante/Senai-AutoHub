
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class MaterialType(str, Enum):
    DOCUMENT = "DOCUMENT"
    VIDEO = "VIDEO"


class MaterialSourceType(str, Enum):
    UPLOAD = "UPLOAD"
    URL = "URL"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(SAEnum(MaterialType), nullable=False, index=True)
    source_type = Column(SAEnum(MaterialSourceType), nullable=False)
    file_path = Column(String(512), nullable=True)
    external_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="materials")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
