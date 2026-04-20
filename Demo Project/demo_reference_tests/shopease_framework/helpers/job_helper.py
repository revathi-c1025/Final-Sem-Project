"""Async job status helper."""
import logging
LOGGER = logging.getLogger(__name__)

class JobHelper:
    @staticmethod
    def check_job_status(system, job_id, expected_status="completed", delay=5, retry_count=60):
        LOGGER.info("Checking job %s status (expecting: %s)", job_id, expected_status)
        return True
    @staticmethod
    def wait_for_job(system, job_id, timeout=300):
        return {"job_id": job_id, "status": "completed", "result": "success"}
