
import shutil
from datetime import datetime
from hashlib import sha256
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_FILE = BASE_DIR / "senai_autohub.db"
UPLOADS_DIR = BASE_DIR / "uploads" / "materials"
BACKUP_DIR = BASE_DIR / "backups"


def create_backup() -> str:
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_DIR / f"backup-{timestamp}"
    backup_dir.mkdir()

    # copia banco
    if DB_FILE.exists():
        shutil.copy2(DB_FILE, backup_dir / "senai_autohub.db")

    # copia uploads
    if UPLOADS_DIR.exists():
        shutil.copytree(UPLOADS_DIR, backup_dir / "materials")

    # checksum simples dos arquivos de material
    hasher = sha256()
    materials_dir = backup_dir / "materials"
    if materials_dir.exists():
        for f in materials_dir.rglob("*"):
            if f.is_file():
                hasher.update(f.read_bytes())
    (backup_dir / "checksum.txt").write_text(hasher.hexdigest())

    return backup_dir.name
