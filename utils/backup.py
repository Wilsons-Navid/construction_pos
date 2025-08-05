
import os
from datetime import datetime

from database.database import db_manager


def create_backup(directory: str = "backups") -> str:
    """Create a timestamped copy of the database file."""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(directory, f"construction_pos_{timestamp}.db")
    db_manager.backup_database(backup_path)
    return backup_path
