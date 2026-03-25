from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.schemas import AnalyzeRequest, JobResponse, ResultResponse, JobStatus
from app.services import analysis_tasks
from app.core.logging import get_logger

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = get_logger(__name__)


@router.post("/analyze", response_model=JobResponse)
@limiter.limit("10/minute")
async def submit_analysis(request: Request, body: AnalyzeRequest) -> JobResponse:
    url_str = str(body.url)
    logger.info(f"Analysis requested: {url_str}")
    task = analysis_tasks.run_analysis.delay(url_str)
    logger.info(f"Job {task.id} queued")
    return JobResponse(job_id=task.id, status=JobStatus.PENDING)


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str) -> ResultResponse:
    task = analysis_tasks.run_analysis.AsyncResult(job_id)

    if task.state == "PENDING":
        return ResultResponse(job_id=job_id, status=JobStatus.PENDING)
    if task.state == "STARTED":
        return ResultResponse(job_id=job_id, status=JobStatus.PROCESSING)
    if task.state == "SUCCESS":
        return ResultResponse(job_id=job_id, status=JobStatus.COMPLETE, result=task.result)
    if task.state == "FAILURE":
        return ResultResponse(job_id=job_id, status=JobStatus.FAILED, error="Analysis failed.")

    raise HTTPException(status_code=500, detail=f"Unknown job state: {task.state}")
