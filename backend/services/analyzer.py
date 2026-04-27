import subprocess
import json

from services.feature_extractor import extract_features
from services.ml_model import predict_bug_risk
import sys
import ast

            
def detect_nested_loops(code: str):
    return code.count("for") + code.count("while") >= 2

def detect_bad_function_name(code: str):
    bad = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name
                if len(name) <= 2:
                    bad.append(name)
        return bad
    except:
        return []

def detect_missing_docstring(code: str):
    return '"""' not in code and "'''" not in code

# 🔍 Run pylint safely using stdin (no file issues)
def run_pylint(code: str):
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pylint",
                "--from-stdin",
                "temp.py",
                "-f",
                "json",
                "--enable=all",
                "--disable=C0114,C0115,C0116"
            ],
            input=code,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = result.stdout.strip()

        # fallback to stderr if needed
        if not output:
            output = result.stderr.strip()

        if not output:
            return []

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            print("⚠️ PYLINT RAW OUTPUT:\n", output)
            return []

    except Exception as e:
        print("PYLINT ERROR:", str(e))
        return []


# 🔍 Main analysis function
def analyze_code(code: str):
    # 1. Extract features
    features = extract_features(code)

    if features is None:
        return {
            "quality_score": 0,
            "bug_risk": 0.5,
            "issues": ["Invalid Python code"]
        }

    # 2. Run pylint
    pylint_output = run_pylint(code)

    issues = []
    severity_score = 0
    
    # ✅ CUSTOM RULE 1: detect bad function names
    bad_funcs = detect_bad_function_name(code)
    if bad_funcs:
        issues.append(f"Poor function naming: {', '.join(bad_funcs)}")
        severity_score += 2.5

    # ✅ CUSTOM RULE 2: detect nested loops
    if detect_nested_loops(code):
        issues.append("High complexity: nested loops detected")
        severity_score += 4

    # ✅ CUSTOM RULE 3: detect missing docstrings
    if detect_missing_docstring(code):
        issues.append("Missing documentation (docstring)")
        severity_score += 2

    for issue in pylint_output:
        message = issue.get("message", "")
        issue_type = issue.get("type", "")

        issues.append(message)

        # 🎯 Weighted scoring
        if issue_type == "error":
            severity_score += 4
        elif issue_type == "warning":
            severity_score += 3
        elif issue_type == "refactor":
            severity_score += 2
        else:
            severity_score += 1

    # 3. Compute quality score
    score = max(0, 10 - severity_score)
    quality_score = round(score / 10, 2)

    # 4. ML prediction
    bug_risk = predict_bug_risk(features)

    return {
        "quality_score": quality_score,
        "bug_risk": bug_risk,
        "issues": issues[:10]  # limit output
    }
