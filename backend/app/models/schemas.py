from enum import Enum
from pydantic import BaseModel, HttpUrl, Field, field_validator


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class Verdict(str, Enum):
    LIKELY_REAL = "likely_real"
    UNCERTAIN = "uncertain"
    LIKELY_FAKE = "likely_fake"


class AnalyzeRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the news article to analyze")

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: HttpUrl) -> HttpUrl:
        if str(v).startswith("file://"):
            raise ValueError("File URLs are not allowed")
        return v


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str = "Analysis started"


class EvidenceItem(BaseModel):
    claim_text: str
    matched_fact_check: str
    source: str
    source_url: str
    verdict: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)


class ClaimResult(BaseModel):
    text: str
    fake_probability: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: list[EvidenceItem] = []


class AnalysisResult(BaseModel):
    url: str
    title: str
    credibility_score: float = Field(..., ge=0.0, le=100.0)
    verdict: Verdict
    claims: list[ClaimResult]
    article_summary: str
    processing_time_seconds: float


class ResultResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: AnalysisResult | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    environment: str
