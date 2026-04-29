"""
Train a simple bug risk model and save it for use by the backend.

Run:
    python ml/train_model.py

The trained model is saved to:
    backend/ml/saved_models/bug_risk_model.pkl

The model uses the same feature set expected by feature_extractor.py.
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

np.random.seed(42)
N = 400  # samples per class

# Low-risk examples are shorter and simpler, with less nesting and fewer loops.
low = np.column_stack([
    np.random.randint(5,   50,  N),      # num_lines
    np.random.randint(10,  500, N),      # num_chars
    np.random.randint(0,   3,   N),      # num_loops
    np.random.randint(0,   3,   N),      # num_conditions
    np.random.randint(1,   5,   N),      # num_functions
    np.random.randint(0,   2,   N),      # num_classes
    np.random.uniform(15,  50,  N),      # avg_line_length
    np.random.randint(1,   4,   N),      # nesting_depth
    np.random.randint(0,   2,   N),      # num_try_except
    np.random.randint(1,   5,   N),      # num_returns
    np.random.uniform(0.7, 1.0, N),     # code_density
])

# High-risk examples are larger, more complex, and use deeper nesting.
high = np.column_stack([
    np.random.randint(100, 600, N),      # num_lines
    np.random.randint(800, 8000, N),     # num_chars
    np.random.randint(6,  20,   N),      # num_loops
    np.random.randint(8,  30,   N),      # num_conditions
    np.random.randint(10, 40,   N),      # num_functions
    np.random.randint(3,  10,   N),      # num_classes
    np.random.uniform(60, 130,  N),      # avg_line_length
    np.random.randint(8,  25,   N),      # nesting_depth
    np.random.randint(0,  3,    N),      # num_try_except
    np.random.randint(8,  40,   N),      # num_returns
    np.random.uniform(0.3, 0.65, N),    # code_density
])

X = np.vstack([low, high])
y = np.array([0] * N + [1] * N)

# Shuffle
idx = np.random.permutation(len(X))
X, y = X[idx], y[idx]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build a pipeline that scales the data and trains a classifier
pipeline = Pipeline([
    ("scaler", MinMaxScaler()),
    ("clf",    RandomForestClassifier(n_estimators=150, random_state=42)),
])

pipeline.fit(X_train, y_train)

# Print evaluation results for the trained model
y_pred = pipeline.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save the trained model to disk
save_path = os.path.join(
    os.path.dirname(__file__),
    "../../backend/ml/saved_models/bug_risk_model.pkl"
)
os.makedirs(os.path.dirname(save_path), exist_ok=True)

with open(save_path, "wb") as f:
    pickle.dump(pipeline, f)

print(f"\nModel saved → {os.path.abspath(save_path)}")