import subprocess
import json
import sys
import ast

from services.feature_extractor import extract_features
from services.ml_model import predict_bug_risk
from services.suggestion_engine import generate_suggestions


# Custom rule checks

def detect_nested_loops(code: str) -> bool:
    """
    Uses AST to detect actual nested loops — not string counting.
    String counting was buggy: 'for' matches 'format', 'before', etc.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    # Skip the node itself
                    if child is node:
                        continue
                    if isinstance(child, (ast.For, ast.While)):
                        return True
    except SyntaxError:
        pass
    return False


def detect_bad_function_names(code: str) -> list:
    """Returns list of function names that are too short (<=2 chars)."""
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


# Run pylint on the submitted code without creating a temporary file.

def run_pylint(code: str) -> list:
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pylint",
                "--from-stdin", "submitted_code.py",
                "--output-format=json",
                "--disable=C0114,C0115,C0116",  # skip missing-docstring warnings for this analysis
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
        print("PYLINT: timed out")
        return []
    except json.JSONDecodeError:
        print("PYLINT: could not parse JSON output")
        return []
    except Exception as e:
        print(f"PYLINT ERROR: {e}")
        return []


# Overall analysis flow for a single code submission

def analyze_code(code: str) -> dict:
    # 1. Pull numeric code metrics from the submitted source
    features = extract_features(code)

    # 2. Apply simple custom rule checks
    issues = []
    severity_score = 0.0

    bad_names = detect_bad_function_names(code)
    if bad_names:
        issues.append(f"Poor function naming: {', '.join(bad_names)}")
        severity_score += 2.5

    if detect_nested_loops(code):
        issues.append("High complexity: nested loops detected")
        severity_score += 4.0

    if detect_missing_docstring(code):
        issues.append("Missing documentation (docstring)")
        severity_score += 2.0

    # 3. Pylint checks
    pylint_results = run_pylint(code)
    for item in pylint_results:
        message   = item.get("message", "").strip()
        item_type = item.get("type", "")

        if message:
            issues.append(message)

        if item_type == "error":
            severity_score += 4.0
        elif item_type == "warning":
            severity_score += 3.0
        elif item_type == "refactor":
            severity_score += 2.0
        else:
            severity_score += 1.0

    # 4. Compute a simple quality score from the issue severity
    raw_score    = max(0.0, 10.0 - severity_score)
    quality_score = round(min(raw_score, 10.0) / 10.0, 2)

    # 5. ML bug risk prediction
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