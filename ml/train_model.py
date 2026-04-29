"""
Run from project root:
    python ml/train_model.py

Saves to: ml/model.pkl
"""

import os, pickle, numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.calibration import CalibratedClassifierCV

np.random.seed(42)
N = 600

def make_samples(n, low_risk=True):
    if low_risk:
        return np.column_stack([
            np.random.randint(10,   80,   n),
            np.random.randint(200,  2000, n),
            np.random.randint(0,    3,    n),
            np.random.randint(0,    4,    n),
            np.random.randint(1,    6,    n),
            np.random.randint(0,    2,    n),
            np.random.uniform(20,   55,   n),
            np.random.randint(1,    4,    n),
            np.random.randint(0,    3,    n),
            np.random.randint(1,    6,    n),
            np.random.uniform(0.65, 1.0,  n),
            np.random.randint(2,    10,   n),
            np.random.randint(0,    2,    n),
            np.random.randint(0,    3,    n),
            np.random.randint(0,    2,    n),
            np.random.randint(0,    1,    n),
            np.random.uniform(5,    25,   n),
            np.random.randint(0,    2,    n),
            np.random.randint(1,    6,    n),
        ])
    else:
        return np.column_stack([
            np.random.randint(80,   600,  n),
            np.random.randint(2000, 15000,n),
            np.random.randint(5,    20,   n),
            np.random.randint(8,    35,   n),
            np.random.randint(10,   50,   n),
            np.random.randint(2,    10,   n),
            np.random.uniform(55,   130,  n),
            np.random.randint(5,    15,   n),
            np.random.randint(0,    2,    n),
            np.random.randint(5,    30,   n),
            np.random.uniform(0.3,  0.65, n),
            np.random.randint(0,    3,    n),
            np.random.randint(0,    1,    n),
            np.random.randint(5,    20,   n),
            np.random.randint(3,    15,   n),
            np.random.randint(0,    3,    n),
            np.random.uniform(30,   100,  n),
            np.random.randint(1,    8,    n),
            np.random.randint(8,    40,   n),
        ])

def make_medium(n):
    return np.column_stack([
        np.random.randint(40,   150,  n),
        np.random.randint(800,  4000, n),
        np.random.randint(2,    8,    n),
        np.random.randint(3,    12,   n),
        np.random.randint(3,    12,   n),
        np.random.randint(0,    4,    n),
        np.random.uniform(35,   80,   n),
        np.random.randint(3,    8,    n),
        np.random.randint(0,    2,    n),
        np.random.randint(2,    12,   n),
        np.random.uniform(0.5,  0.8,  n),
        np.random.randint(1,    6,    n),
        np.random.randint(0,    2,    n),
        np.random.randint(1,    8,    n),
        np.random.randint(1,    6,    n),
        np.random.randint(0,    2,    n),
        np.random.uniform(10,   50,   n),
        np.random.randint(0,    4,    n),
        np.random.randint(4,    18,   n),
    ])

low  = make_samples(N, low_risk=True)
high = make_samples(N, low_risk=False)
med  = make_medium(N // 2)
med_labels = np.where(np.random.rand(N // 2) > 0.4, 1, 0)

X = np.vstack([low, high, med])
y = np.concatenate([np.zeros(N), np.ones(N), med_labels])

idx = np.random.permutation(len(X))
X, y = X[idx], y[idx]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

base = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8, random_state=42)

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("clf",    CalibratedClassifierCV(base, cv=3, method="sigmoid")),
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
print("Test accuracy :", accuracy_score(y_test, y_pred))
print("CV accuracy   :", f"{cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")
print(classification_report(y_test, y_pred, target_names=["Low Risk", "High Risk"]))

sample_low  = make_samples(3, low_risk=True)
sample_high = make_samples(3, low_risk=False)
print("Low risk proba  :", pipeline.predict_proba(sample_low)[:, 1].round(2))
print("High risk proba :", pipeline.predict_proba(sample_high)[:, 1].round(2))

save_path = os.path.join(os.path.dirname(__file__), "model.pkl")
with open(save_path, "wb") as f:
    pickle.dump(pipeline, f)
print(f"\nModel saved -> {os.path.abspath(save_path)}")