import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from rq.job import Job

from auth import User, auth_dependency
from config import get_settings
from rate_limiter import check_rate_limit
from queue import get_queue, get_redis
from schemas import GenerateRequest, AnalyzeRequest, JobResponse, JobStatus
from jobs.generate import enqueue_generate
from jobs.analyze import enqueue_analyze


settings = get_settings()

app = FastAPI(title=settings.api_name, version=settings.api_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "*"] if settings.debug else [settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.api_version}


@app.post("/generate", response_model=JobResponse)
def generate_ad(request: GenerateRequest, user: User = Depends(auth_dependency)):
    check_rate_limit(user.sub)
    job_id = enqueue_generate(request, user)
    return JobResponse(job_id=job_id)


@app.post("/analyze", response_model=JobResponse)
def analyze(request: AnalyzeRequest, user: User = Depends(auth_dependency)):
    check_rate_limit(user.sub)
    job_id = enqueue_analyze(request, user)
    return JobResponse(job_id=job_id)


@app.get("/jobs/{job_id}", response_model=JobStatus)
def job_status(job_id: str, user: User = Depends(auth_dependency)):
    conn = get_redis()
    try:
        job = Job.fetch(job_id, connection=conn)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    status_str = job.get_status()
    result = job.result if status_str == "finished" else None
    error = job.meta.get("error") if job.meta else None

    return JobStatus(status=status_str, result_url=result, error=error)

