# AI Code Review Assistant

## Overview
AI Code Review Assistant is a full-stack code review project with a FastAPI backend, a simple React frontend, and an ML-driven bug risk predictor. The system analyzes Python code, extracts quality features, generates issues and suggestions, and stores analysis history in SQLite.

## What it does so far
- Accepts Python code via `/analyze`
- Runs AST-based rules and `pylint` checks
- Extracts code metrics like function count, loop count, nesting depth, and docstring usage
- Predicts a bug risk score using a trained ML model
- Stores analysis history in a local SQLite database
- Exposes history retrieval and deletion endpoints
- Includes a basic React + Vite frontend scaffold in `frontend/`

## Project Structure

```
ai-code-review/
├── backend/
│   ├── main.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── routes/
│   │   └── analyze.py
│   └── services/
│       ├── analyzer.py
│       ├── feature_extractor.py
│       ├── ml_model.py
│       └── suggestion_engine.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       └── main.jsx
├── ml/
│   ├── convert_dataset.py
│   ├── dataset.csv
│   ├── model.pkl
│   └── train_model.py
├── README.md
└── requirements.txt
```

- `backend/main.py` — FastAPI application entry point
- `backend/routes/analyze.py` — analysis, history, and delete endpoints
- `backend/services/analyzer.py` — analysis orchestration and scoring logic
- `backend/services/feature_extractor.py` — code feature extraction
- `backend/services/suggestion_engine.py` — user-facing improvement suggestions
- `backend/services/ml_model.py` — loads ML model and predicts bug risk
- `backend/database/db.py` — SQLite database session and engine setup
- `backend/database/models.py` — SQLAlchemy data model for analysis records
- `ml/train_model.py` — trains the bug risk classifier and saves `ml/model.pkl`
- `ml/convert_dataset.py` — dataset conversion utility using pandas
- `frontend/` — React + Vite frontend scaffold

## API Endpoints
- `POST /analyze` — analyze Python source code
- `GET /history` — return recent saved analyses
- `DELETE /history/{analysis_id}` — delete a specific record

### Example Request
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")"}'
```

### Example Response
```json
{
  "id": "...",
  "quality_score": 0.82,
  "bug_risk": 0.37,
  "issues": ["Missing documentation (docstring)", "High complexity: nested loops detected"],
  "suggestions": ["Add docstrings to all public functions and classes.", "Reduce nesting depth by extracting inner blocks into separate functions."],
  "features": { ... },
  "created_at": "..."
}
```

## Setup
### Backend
1. Create and activate a Python virtual environment.
2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend
1. Change into the frontend folder:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the frontend dev server:
   ```bash
   npm run dev
   ```

## ML Model
Train or refresh the ML bug risk model:
```bash
python ml/train_model.py
```
The script saves the model to:
- `ml/model.pkl`

If the model is missing, the API will fall back to a neutral `0.5` bug risk score and print a warning.

## Dependencies
The Python runtime depends on:
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `numpy`
- `scikit-learn`
- `pandas`
- `pylint`

## Notes
- The SQLite database file is created as `codereview.db` in the project root when the app runs.
- Current analysis is based on synthetic ML training data and heuristic rules.
- Frontend is a minimal starter implementation and can be connected to the backend via CORS.
