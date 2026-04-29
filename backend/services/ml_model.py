import os
import pickle
import numpy as np

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../ml/saved_models/bug_risk_model.pkl"
)

_model = None  # Loaded once on first call, not at import time


def _load_model():
    global _model
    if _model is None:
        path = os.path.abspath(MODEL_PATH)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Model file not found at: {path}\n"
                "Run: python ml/training/train_model.py"
            )
        with open(path, "rb") as f:
            _model = pickle.load(f)
    return _model


def predict_bug_risk(features: dict) -> float:
    """
    Takes features dict from feature_extractor.py
    Returns bug risk probability between 0.0 and 1.0
    """
    try:
        model = _load_model()

        # Feature order MUST match train_model.py exactly
        vector = np.array([[
            features["num_lines"],
            features["num_chars"],
            features["num_loops"],
            features["num_conditions"],
            features["num_functions"],
            features["num_classes"],
            features["avg_line_length"],
            features["nesting_depth"],
            features["num_try_except"],
            features["num_returns"],
            features["code_density"],
        ]])

        prob = model.predict_proba(vector)[0][1]
        return round(float(prob), 2)

    except FileNotFoundError as e:
        print(f"MODEL NOT FOUND: {e}")
        return 0.5  # Neutral fallback

    except Exception as e:
        print(f"ML ERROR: {e}")
        return 0.5