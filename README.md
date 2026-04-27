# AI Code Review Assistant

## Overview
A full-stack AI-powered code analysis system that combines:
- Rule-based static analysis (pylint)
- Machine learning for bug risk prediction
- FastAPI backend for real-time inference

## Features
- Code quality analysis
- Bug risk prediction using ML
- REST API for integration
- Feature extraction from source code

## Tech Stack
- FastAPI
- Python
- Scikit-learn
- Pylint

## API Endpoint

POST /analyze

```json
{
  "code": "print('hello')"
}

Future Work
Real dataset integration (GitHub code)
Deep learning (CodeBERT)
Frontend dashboard
Database integration

---
