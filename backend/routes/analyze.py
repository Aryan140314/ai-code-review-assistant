from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.db import get_db
from database.models import Analysis
from services.analyzer import analyze_code

router = APIRouter()

PIPE = " || "  # separator for storing lists in DB


class CodeInput(BaseModel):
    code: str


@router.post("/analyze")
def analyze(data: CodeInput, db: Session = Depends(get_db)):
    code = data.code.strip()

    if not code:
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    if len(code) > 50_000:
        raise HTTPException(status_code=400, detail="Code too large. Max 50,000 characters.")

    result = analyze_code(code)

    # Save to DB
    record = Analysis(
        code          = code,
        quality_score = result["quality_score"],
        bug_risk      = result["bug_risk"],
        issues        = PIPE.join(result.get("issues", [])),
        suggestions   = PIPE.join(result.get("suggestions", [])),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id":            str(record.id),
        "quality_score": result["quality_score"],
        "bug_risk":      result["bug_risk"],
        "issues":        result.get("issues", []),
        "suggestions":   result.get("suggestions", []),
        "features":      result.get("features", {}),
        "created_at":    record.created_at,
    }


@router.get("/history")
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    records = (
        db.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .limit(min(limit, 100))  # cap at 100
        .all()
    )
    return [
        {
            "id":            str(r.id),
            "quality_score": r.quality_score,
            "bug_risk":      r.bug_risk,
            "issues":        r.issues.split(PIPE) if r.issues else [],
            "suggestions":   r.suggestions.split(PIPE) if r.suggestions else [],
            "created_at":    r.created_at,
        }
        for r in records
    ]


@router.delete("/history/{analysis_id}")
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    record = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    db.delete(record)
    db.commit()
    return {"message": "Deleted."}