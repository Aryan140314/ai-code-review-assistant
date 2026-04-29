# AI Code Review Assistant

## Overview
AI Code Review Assistant is a FastAPI-based backend for automated source code analysis. It combines static quality checks, extracted code features, and a machine learning classifier to estimate bug risk and provide improvement suggestions.

## Features
- Code quality scoring and issue detection
- Bug risk prediction using an ML model
- Code feature extraction for analysis
- Human-readable suggestions from detected issues and code metrics
- SQLite history storage for past analysis results
- API routes for analysis, history retrieval, and record deletion

## Architecture
- `backend/main.py` — FastAPI application entry point
- `backend/routes/analyze.py` — `/analyze`, `/history`, and delete history endpoints
- `backend/services/analyzer.py` — code analysis orchestration
- `backend/services/feature_extractor.py` — extracts code metrics for ML and guidance
- `backend/services/suggestion_engine.py` — generates suggestions from issues and features
- `backend/database/` — SQLAlchemy models and DB session support
- `ml/train_model.py` — synthetic dataset training for bug risk classification
- `ml/convert_dataset.py` — dataset preparation and conversion utilities

## API Endpoints

POST `/analyze`

Request body:
```json
{
  "code": "print('hello')"
}
```

Response includes:
- `quality_score`
- `bug_risk`
- `issues`
- `suggestions`
- `features`
- `created_at`

GET `/history`
- Returns recent analysis records from the SQLite database

DELETE `/history/{analysis_id}`
- Removes a saved analysis record

## Getting Started
1. Create and activate your Python environment.
2. Install dependencies from `requirements.txt`.
3. Run the app:
   ```bash
   uvicorn backend.main:app --reload
   ```
4. Call `/analyze` with Python code to receive insights.

## ML Training
Train or refresh the bug risk model with:
```bash
python ml/train_model.py
```
The trained model is saved to `backend/ml/saved_models/bug_risk_model.pkl`.

## Notes
- SQLite is used for local analysis persistence.
- The current bug risk classifier is trained on synthetic features.
- Large files such as `ml/CodeXGLUE-main.zip` are excluded from source control.

---
