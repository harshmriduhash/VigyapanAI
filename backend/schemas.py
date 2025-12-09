from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class GenerateRequest(BaseModel):
    productName: str = Field(..., min_length=2, max_length=120)
    tagline: str = Field(..., min_length=2, max_length=160)
    duration: int = Field(ge=4, le=60, default=8)
    callToAction: str = Field(..., min_length=2, max_length=120)
    logoUrl: Optional[HttpUrl] = None
    targetAudience: Optional[str] = None
    campaignGoal: Optional[str] = None
    brandColors: Optional[str] = None


class AnalyzeRequest(BaseModel):
    productName: str
    brandName: str
    tagline: str
    colorPalette: Optional[str] = None
    videoUrl: HttpUrl


class JobResponse(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    status: str
    result_url: Optional[str] = None
    error: Optional[str] = None

