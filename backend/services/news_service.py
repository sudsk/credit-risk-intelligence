import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

DATA_DIR = Path(__file__).parent.parent.parent / "data"
NEWS_CSV = DATA_DIR / "news_events.csv"
EVENTS_CSV = DATA_DIR / "predicted_events.csv"

class NewsService:
    async def get_news_intelligence(
        self,
        sme_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        df = pd.read_csv(NEWS_CSV)
        if sme_id:
            df = df[df['sme_id'] == sme_id.replace('#', '')]
        if severity:
            df = df[df['severity'] == severity]
        df = df.sort_values('timestamp', ascending=False).head(limit)
        return {"items": df.fillna('').to_dict('records'), "count": len(df)}

    async def get_predicted_events(self) -> Dict[str, Any]:
        df = pd.read_csv(EVENTS_CSV)
        df = df.sort_values('days_until', ascending=True)
        return {"events": df.fillna('').to_dict('records'), "count": len(df)}

_news_service = None
def get_news_service() -> NewsService:
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
    return _news_service