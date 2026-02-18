import json
from pathlib import Path
from datetime import datetime


class UserRegistry:
    """Tracks known users for multi-user session management."""

    def __init__(self, file_path: str = "data/users/index.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"users": {}}

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def ensure_user(self, user_id: str) -> None:
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow().isoformat()
            }
        else:
            self.data["users"][user_id]["last_active"] = datetime.utcnow().isoformat()
        self._save()

    def list_users(self) -> list[str]:
        return sorted(self.data["users"].keys())

    def has_user(self, user_id: str) -> bool:
        return user_id in self.data["users"]
