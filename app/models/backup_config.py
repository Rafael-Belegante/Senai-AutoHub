
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer

from app.db.base import Base


class BackupConfig(Base):
    __tablename__ = "backup_config"

    id = Column(Integer, primary_key=True, index=True)
    enabled = Column(Boolean, default=False)
    interval_hours = Column(Integer, default=24)
    last_run_at = Column(DateTime, nullable=True)
