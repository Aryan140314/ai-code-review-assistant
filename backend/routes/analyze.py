from fastapi import APIRouter
from services.analyzer import analyze_code

router = APIRouter()

@router.post("/analyze")
def analyze(data: dict):
    code = data.get("code", "")
    result = analyze_code(code)
    return result