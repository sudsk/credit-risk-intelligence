"""
Scenario Job Service
Wraps ScenarioService with an async job pattern so the UI never blocks.

Flow:
  POST /api/v1/scenarios/run  → returns {job_id} immediately
  GET  /api/v1/scenarios/{job_id}/status → polls until status == "completed"

Jobs are kept in memory (fine for POC — single process, no persistence needed).
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from services.scenario_service import get_scenario_service

logger = logging.getLogger(__name__)

# In-memory job store: job_id → job dict
_jobs: Dict[str, Dict[str, Any]] = {}


class ScenarioJobService:
    """Manages async scenario jobs."""

    def __init__(self):
        self.scenario_service = get_scenario_service()

    def create_job(self, scenario_type: str, parameters: Dict[str, Any]) -> str:
        """Create a job record and kick off background execution. Returns job_id."""
        job_id = str(uuid.uuid4())
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "running",
            "scenario_type": scenario_type,
            "parameters": parameters,
            "created_at": datetime.now().isoformat() + "Z",
            "completed_at": None,
            "progress": 0,
            "result": None,
            "error": None,
        }

        # Fire and forget — runs in the event loop without blocking the request
        asyncio.create_task(self._run_job(job_id, scenario_type, parameters))
        logger.info(f"Scenario job created: {job_id} ({scenario_type})")
        return job_id

    async def _run_job(
        self, job_id: str, scenario_type: str, parameters: Dict[str, Any]
    ):
        """Execute the scenario calculation in the background."""
        try:
            _jobs[job_id]["progress"] = 10
            logger.info(f"Running scenario job {job_id}")

            result = await self.scenario_service.run_scenario(scenario_type, parameters)

            _jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "result": result,
                "completed_at": datetime.now().isoformat() + "Z",
            })
            logger.info(f"Scenario job {job_id} completed")

        except Exception as e:
            logger.error(f"Scenario job {job_id} failed: {e}", exc_info=True)
            _jobs[job_id].update({
                "status": "failed",
                "progress": 0,
                "error": str(e),
                "completed_at": datetime.now().isoformat() + "Z",
            })

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Return job status dict, or None if not found."""
        return _jobs.get(job_id)

    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Return the full result for a completed job, or None."""
        job = _jobs.get(job_id)
        if not job or job["status"] != "completed":
            return None
        return job["result"]

    def get_all_jobs(self) -> list:
            """Return all jobs sorted newest first — used by GET /api/v1/scenarios."""
            return sorted(
                _jobs.values(),
                key=lambda j: j["created_at"],
                reverse=True,
            )

_scenario_job_service = None

def get_scenario_job_service() -> ScenarioJobService:
    global _scenario_job_service
    if _scenario_job_service is None:
        _scenario_job_service = ScenarioJobService()
    return _scenario_job_service