import subprocess
import tempfile
import re

from services.feature_extractor import extract_features
from services.ml_model import predict_bug_risk


def analyze_code(code):
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp_path = tmp.name

    # Run pylint
    result = subprocess.run(
        ["pylint", tmp_path],
        capture_output=True,
        text=True
    )

    output = result.stdout

    # Extract issues
    issues = []
    for line in output.split("\n"):
        if ":" in line and ("C0" in line or "E0" in line or "W0" in line):
            parts = line.split(":")
            if len(parts) > 3:
                issues.append(parts[-1].strip())

    # Extract score
    score_match = re.search(r"rated at ([\d\.]+)/10", output)
    score = float(score_match.group(1)) if score_match else 0.0

    # Normalize
    quality_score = score / 10
    features = extract_features(code)
    bug_risk = predict_bug_risk(features)

    return {
        "quality_score": round(quality_score, 2),
        "bug_risk": round(bug_risk, 2),
        "issues": issues
    }