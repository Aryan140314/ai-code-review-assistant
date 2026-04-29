import os, pickle, numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../ml/model.pkl")
_model = None

def _load_model():
    global _model
    if _model is None:
        path = os.path.abspath(MODEL_PATH)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found at: {path}\nRun: python ml/train_model.py")
        with open(path, "rb") as f:
            _model = pickle.load(f)
    return _model

def predict_bug_risk(features: dict) -> float:
    try:
        model = _load_model()
        vector = np.array([[
            features["num_lines"],
            features["num_chars"],
            features["num_loops"],
            features["num_conditions"],
            features["num_functions"],
            features["num_classes"],
            features["avg_line_length"],
            features["max_nesting_depth"],
            features["num_try_except"],
            features["num_returns"],
            features["code_density"],
            features["num_comments"],
            features["has_docstring"],
            features["num_magic_numbers"],
            features["num_print_statements"],
            features["num_bare_except"],
            features["avg_function_length"],
            features["num_global_vars"],
            features["cyclomatic_complexity"],
        ]])
        prob = model.predict_proba(vector)[0][1]
        return round(float(prob), 2)
    except FileNotFoundError as e:
        print(f"MODEL NOT FOUND: {e}")
        return 0.5
    except Exception as e:
        print(f"ML ERROR: {e}")
        return 0.5