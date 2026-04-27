from fastapi import APIRouter, HTTPException
from services.analyzer import analyze_code

router = APIRouter()

@router.post("/analyze")
def analyze(data: dict):
    code = data.get("code", "")

    if not code.strip():
        raise HTTPException(status_code=400, detail="Code is empty")

    return analyze_code(code)