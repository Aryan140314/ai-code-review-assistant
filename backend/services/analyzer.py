import subprocess
import tempfile
import json

from services.feature_extractor import extract_features
from services.ml_model import predict_bug_risk


def run_pylint(file_path):
    result = subprocess.run(
        ["pylint", file_path, "--output-format=json"],
        capture_output=True,
        text=True
    )

    try:
        return json.loads(result.stdout)
    except:
        return []


def analyze_code(code: str):
    # 1. Feature extraction
    features = extract_features(code)

    if features is None:
        return {
            "error": "Invalid Python code"
        }

    # 2. Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp_path = tmp.name

    # 3. Run pylint
    pylint_output = run_pylint(tmp_path)

    issues = []
    score = 10.0

    if isinstance(pylint_output, list):
        for issue in pylint_output:
            issues.append(issue.get("message", ""))

        # Approximate score
        error_count = len(pylint_output)
        score = max(0, 10 - error_count * 0.5)

    quality_score = round(score / 10, 2)

    # 4. ML prediction
    bug_risk = predict_bug_risk(features)

    return {
        "quality_score": quality_score,
        "bug_risk": bug_risk,
        "issues": issues[:10]  # limit output
    }