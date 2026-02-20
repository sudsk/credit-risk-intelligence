import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent.parent / "data"
ACTIVITIES_CSV = DATA_DIR / "activities.csv"

class ActivityService:
    def _load(self) -> pd.DataFrame:
        return pd.read_csv(ACTIVITIES_CSV)

    def _save(self, df: pd.DataFrame):
        df.to_csv(ACTIVITIES_CSV, index=False)

    async def get_activities(self, limit: int = 50) -> Dict[str, Any]:
        df = self._load()
        df = df.sort_values('timestamp', ascending=False).head(limit)
        return {"activities": df.fillna('').to_dict('records'), "count": len(df)}

    async def log_activity(self, activity_type: str, message: str):
        """Call this from other services to write audit entries"""
        df = self._load()
        new_row = pd.DataFrame([{
            "id": f"act_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat() + "Z",
            "type": activity_type,
            "message": message,
        }])
        df = pd.concat([new_row, df], ignore_index=True)  # prepend so newest first
        self._save(df)

_activity_service = None
def get_activity_service() -> ActivityService:
    global _activity_service
    if _activity_service is None:
        _activity_service = ActivityService()
    return _activity_service