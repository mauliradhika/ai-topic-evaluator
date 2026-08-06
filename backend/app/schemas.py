from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ReferenceOut(BaseModel):
    citation_text: str
    url: Optional[str] = None
    source_type: str

    class Config:
        from_attributes = True


class TopicOut(BaseModel):
    id: str
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class SubtopicOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    difficulty: str

    class Config:
        from_attributes = True


class StartSessionRequest(BaseModel):
    topic_id: str
    mode: str = Field(..., pattern="^(speak|write)$")
    strictness: str = Field(..., pattern="^(lenient|moderate|strict)$")
    prep_time_sec: int = Field(..., ge=120, le=900)       # 2-15 min
    response_time_sec: int = Field(..., ge=60, le=600)    # 1-10 min


class StartSessionResponse(BaseModel):
    session_id: str
    subtopic: SubtopicOut
    references: List[ReferenceOut]
    prep_time_sec: int
    response_time_sec: int
    mode: str
    strictness: str


class SubmitResponseRequest(BaseModel):
    user_input: str
    time_used_sec: int


class CriterionScore(BaseModel):
    score: float          # 0-10
    weight: float          # 0-1, fraction of total
    comment: str


class EvaluationResult(BaseModel):
    session_id: str
    overall_score: float   # 0-100
    criteria: Dict[str, CriterionScore]
    feedback: str
    strengths: List[str]
    improvements: List[str]
