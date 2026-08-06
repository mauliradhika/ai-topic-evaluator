import json
import random

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db, Base
from .seed_data import seed
from .evaluator import evaluate_response

Base.metadata.create_all(bind=engine)
seed()

app = FastAPI(title="PrepSpeak API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/topics", response_model=list[schemas.TopicOut])
def list_topics(db: Session = Depends(get_db)):
    return db.query(models.Topic).all()


def weighted_random_subtopic(subtopics: list[models.Subtopic]) -> models.Subtopic:
    weights = [s.weight for s in subtopics]
    return random.choices(subtopics, weights=weights, k=1)[0]


@app.post("/session/start", response_model=schemas.StartSessionResponse)
def start_session(req: schemas.StartSessionRequest, db: Session = Depends(get_db)):
    topic = db.query(models.Topic).filter(models.Topic.id == req.topic_id).first()
    if not topic or not topic.subtopics:
        raise HTTPException(404, "Topic not found or has no subtopics")

    subtopic = weighted_random_subtopic(topic.subtopics)

    session = models.PracticeSession(
        topic_id=topic.id,
        subtopic_id=subtopic.id,
        mode=req.mode,
        strictness=req.strictness,
        prep_time_sec=req.prep_time_sec,
        response_time_sec=req.response_time_sec,
        status=models.SessionStatus.prep,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return schemas.StartSessionResponse(
        session_id=session.id,
        subtopic=schemas.SubtopicOut.model_validate(subtopic),
        references=[schemas.ReferenceOut.model_validate(r) for r in subtopic.references],
        prep_time_sec=session.prep_time_sec,
        response_time_sec=session.response_time_sec,
        mode=session.mode.value,
        strictness=session.strictness.value,
    )


@app.post("/session/{session_id}/submit", response_model=schemas.EvaluationResult)
def submit_response(session_id: str, req: schemas.SubmitResponseRequest, db: Session = Depends(get_db)):
    session = db.query(models.PracticeSession).filter(models.PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status == models.SessionStatus.evaluated:
        raise HTTPException(400, "Session already evaluated")

    session.user_input = req.user_input
    session.time_used_sec = req.time_used_sec
    session.status = models.SessionStatus.submitted
    db.commit()

    subtopic = session.subtopic
    references = [{"citation_text": r.citation_text, "url": r.url} for r in subtopic.references]

    try:
        result = evaluate_response(
            subtopic_name=subtopic.name,
            subtopic_description=subtopic.description or "",
            references=references,
            mode=session.mode.value,
            strictness=session.strictness.value,
            user_input=req.user_input,
            time_used_sec=req.time_used_sec,
            response_time_sec=session.response_time_sec,
        )
    except Exception as e:
        raise HTTPException(500, f"Evaluation failed: {e}")

    session.overall_score = result["overall_score"]
    session.criteria_scores = json.dumps(result["criteria"])
    session.feedback = result["feedback"]
    session.status = models.SessionStatus.evaluated
    db.commit()

    return schemas.EvaluationResult(
        session_id=session.id,
        overall_score=result["overall_score"],
        criteria=result["criteria"],
        feedback=result["feedback"],
        strengths=result.get("strengths", []),
        improvements=result.get("improvements", []),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
