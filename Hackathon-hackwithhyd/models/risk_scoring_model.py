import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "cve_2025_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "risk_model.joblib")

# ---------------------------
# Step 1: Load Dataset
# ---------------------------
df = pd.read_csv(DATA_PATH)

# Handle missing values
df["cvss_score"] = df["cvss_score"].fillna(0.0)
df["exploitability_score"] = df["exploitability_score"].fillna(0.0)

# ---------------------------
# Step 2: Define Risk Score
# ---------------------------
# Formula: 70% CVSS + 30% Exploitability
df["risk_score"] = 0.7 * df["cvss_score"] + 0.3 * df["exploitability_score"]

# ---------------------------
# Step 3: Train/Test Split
# ---------------------------
X = df[["cvss_score", "exploitability_score"]]
y = df["risk_score"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------
# Step 4: Train Model
# ---------------------------
risk_model = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=3,
    learning_rate=0.1,
    random_state=42
)

risk_model.fit(X_train, y_train)

# ---------------------------
# Step 5: Evaluate
# ---------------------------
r2 = risk_model.score(X_test, y_test)
print(f"[INFO] Risk Model R^2 Score: {r2:.2f}")

# ---------------------------
# Step 6: Save Model
# ---------------------------
joblib.dump(risk_model, MODEL_PATH)
print(f"[INFO] ✅ Risk model saved as {MODEL_PATH}")    