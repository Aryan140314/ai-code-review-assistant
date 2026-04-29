import uuid
from sqlalchemy import Column, String, Float, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.db import Base


class Analysis(Base):
    __tablename__ = "analysis"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code          = Column(Text, nullable=False)
    quality_score = Column(Float, nullable=False)
    bug_risk      = Column(Float, nullable=False)
    issues        = Column(Text, nullable=True)       # stored as a single text string with pipe separators
    suggestions   = Column(Text, nullable=True)       # stored as a single text string with pipe separators
    created_at    = Column(DateTime(timezone=True), server_default=func.now())