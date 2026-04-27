import joblib
import os
import pandas as pd

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../ml/model.pkl")
)

model = joblib.load(MODEL_PATH)

def predict_bug_risk(features):
    try:
        df = pd.DataFrame([features])

        proba = model.predict_proba(df)[0][1]  # probability of class 1

        return float(round(proba, 2))

    except Exception as e:
        print("ML ERROR:", str(e))
        return 0.5