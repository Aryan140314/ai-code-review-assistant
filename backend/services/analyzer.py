import subprocess
import json
import sys
import ast

from services.feature_extractor import extract_features
from services.ml_model import predict_bug_risk
from services.suggestion_engine import generate_suggestions


def detect_nested_loops(code: str) -> bool:
    """AST-based nested loop detection — not string matching."""
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if isinstance(child, (ast.For, ast.While)):
                        return True
    except SyntaxError:
        pass
    return False


def detect_bad_function_names(code: str) -> list:
    bad = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.name) <= 2:
                bad.append(node.name)
    except SyntaxError:
        pass
    return bad


def detect_missing_docstring(code: str) -> bool:
    return '"""' not in code and "'''" not in code


def run_pylint(code: str) -> list:
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pylint",
                "--from-stdin", "submitted_code.py",
                "--output-format=json",
                "--disable=C0114,C0115,C0116,C0301",
                "--score=no",
            ],
            input=code,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        raw = result.stdout.strip()
        if not raw:
            return []
        return json.loads(raw)
    except subprocess.TimeoutExpired:
        return []
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"PYLINT ERROR: {e}")
        return []


def analyze_code(code: str) -> dict:
    # Fresh list every call — fixes issue leakage bug
    issues = []
    severity_score = 0.0

    # 1. Extract features
    features = extract_features(code)

    # 2. Custom rules
    bad_names = detect_bad_function_names(code)
    if bad_names:
        issues.append(f"Poor function naming: {', '.join(bad_names)}")
        severity_score += 1.5   # reduced from 2.5

    if detect_nested_loops(code):
        issues.append("High complexity: nested loops detected")
        severity_score += 2.0   # reduced from 4.0

    if detect_missing_docstring(code):
        issues.append("Missing documentation (docstring)")
        severity_score += 1.0   # reduced from 2.0

    # 3. Pylint
    pylint_results = run_pylint(code)
    for item in pylint_results:
        message   = item.get("message", "").strip()
        item_type = item.get("type", "")
        if message:
            issues.append(message)
        # Reduced weights — was causing over-aggressive scoring
        if item_type == "error":
            severity_score += 2.5
        elif item_type == "warning":
            severity_score += 1.5
        elif item_type == "refactor":
            severity_score += 1.0
        else:
            severity_score += 0.5

    # 4. Quality score — clamped [0, 1]
    # Max tolerable severity before score hits 0 = 20 (was 10 — too harsh)
    quality_score = round(max(0.0, min(1.0, (20.0 - severity_score) / 20.0)), 2)

    # 5. Bug risk from ML
    bug_risk = predict_bug_risk(features)

    # 6. Suggestions
    suggestions = generate_suggestions(issues, features)

    return {
        "quality_score": quality_score,
        "bug_risk":      bug_risk,
        "issues":        issues[:10],
        "suggestions":   suggestions,
        "features":      features,
    }