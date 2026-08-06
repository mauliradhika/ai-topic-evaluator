import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, ForeignKey, Enum, DateTime, Text
)
from sqlalchemy.orm import relationship

from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=True)

    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")


class Subtopic(Base):
    __tablename__ = "subtopics"

    id = Column(String, primary_key=True, default=gen_uuid)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, default="medium")  # easy | medium | hard
    weight = Column(Float, default=1.0)  # for weighted random draw

    topic = relationship("Topic", back_populates="subtopics")
    references = relationship("Reference", back_populates="subtopic", cascade="all, delete-orphan")


class Reference(Base):
    __tablename__ = "references"

    id = Column(String, primary_key=True, default=gen_uuid)
    subtopic_id = Column(String, ForeignKey("subtopics.id"), nullable=False)
    citation_text = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    source_type = Column(String, default="article")  # article | paper | report | book

    subtopic = relationship("Subtopic", back_populates="references")


class InputMode(str, enum.Enum):
    speak = "speak"
    write = "write"


class Strictness(str, enum.Enum):
    lenient = "lenient"
    moderate = "moderate"
    strict = "strict"


class SessionStatus(str, enum.Enum):
    prep = "prep"
    responding = "responding"
    submitted = "submitted"
    evaluated = "evaluated"


class PracticeSession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=gen_uuid)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    subtopic_id = Column(String, ForeignKey("subtopics.id"), nullable=False)

    mode = Column(Enum(InputMode), nullable=False)
    strictness = Column(Enum(Strictness), nullable=False)
    prep_time_sec = Column(Integer, nullable=False)   # 120 - 900
    response_time_sec = Column(Integer, nullable=False)  # 60 - 600

    status = Column(Enum(SessionStatus), default=SessionStatus.prep)

    user_input = Column(Text, nullable=True)          # transcript or written text
    time_used_sec = Column(Integer, nullable=True)     # actual time taken (closed early?)

    # Evaluation results
    overall_score = Column(Float, nullable=True)
    criteria_scores = Column(Text, nullable=True)      # JSON string: {"grammar": 8, ...}
    feedback = Column(Text, nullable=True)              # personalized narrative feedback

    created_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)

    topic = relationship("Topic")
    subtopic = relationship("Subtopic")
