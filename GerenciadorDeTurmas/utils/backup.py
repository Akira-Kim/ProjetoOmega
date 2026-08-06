"""utils/backup.py - Copia o banco para uma pasta de backups."""

from pathlib import Path
from datetime import datetime
import shutil

from database import DB_PATH


def fazer_backup() -> Path:
    origem = Path(DB_PATH)
    if not origem.exists():
        raise FileNotFoundError(f"Banco nao encontrado: {origem}")

    pasta = origem.parent / "backups"
    pasta.mkdir(parents=True, exist_ok=True)

    nome = f"planner_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = pasta / nome
    shutil.copy2(origem, destino)
    return destino