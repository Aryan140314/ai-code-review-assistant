import joblib
import os
import pandas as pd

# ✅ Absolute path (safer)
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../ml/model.pkl")
)

# ✅ Load model once
model = joblib.load(MODEL_PATH)


def predict_bug_risk(features):
    try:
        # ✅ Convert features to DataFrame (fix warning + proper ML input)
        feature_df = pd.DataFrame([{
            "num_lines": features["num_lines"],
            "num_chars": features["num_chars"],
            "num_loops": features["num_loops"],
            "num_conditions": features["num_conditions"],
            "num_functions": features["num_functions"],
            "indentation_issues": features["indentation_issues"]
        }])

        # 🔍 Debug (important for now)
        print("FEATURE INPUT:\n", feature_df)

        # ✅ Predict
        prediction = model.predict(feature_df)[0]

        print("PREDICTION:", prediction)

        # ✅ Convert class → risk score
        if prediction == 1:
            return 0.7   # risky code
        else:
            return 0.2   # safer code

    except Exception as e:
        print("ML ERROR:", str(e))
        return 0.5  # fallback (neutral risk)