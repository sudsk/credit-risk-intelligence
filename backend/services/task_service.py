import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any

DATA_DIR = Path(__file__).parent.parent.parent / "data"
TASKS_CSV = DATA_DIR / "tasks.csv"

class TaskService:
    def _load(self) -> pd.DataFrame:
        return pd.read_csv(TASKS_CSV)

    def _save(self, df: pd.DataFrame):
        df.to_csv(TASKS_CSV, index=False)

    async def get_tasks(self, status: Optional[str] = None) -> Dict[str, Any]:
        df = self._load()
        if status:
            df = df[df['status'] == status]
        tasks = df.fillna('').to_dict('records')
        return {"tasks": tasks, "count": len(tasks)}

    async def create_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        df = self._load()
        new_row = pd.DataFrame([task])
        df = pd.concat([df, new_row], ignore_index=True)
        self._save(df)
        return task

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        df = self._load()
        mask = df['id'] == task_id
        if not mask.any():
            raise ValueError(f"Task {task_id} not found")
        for key, value in updates.items():
            if key in df.columns:
                df.loc[mask, key] = value
        self._save(df)
        return df[mask].iloc[0].to_dict()

    async def delete_task(self, task_id: str):
        df = self._load()
        df = df[df['id'] != task_id]
        self._save(df)

_task_service = None
def get_task_service() -> TaskService:
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service