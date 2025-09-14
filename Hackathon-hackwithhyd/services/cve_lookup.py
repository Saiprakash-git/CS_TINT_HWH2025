import pandas as pd
import os

# Load CVE dataset once
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "cve_2025_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "risk_model.joblib")

CVE_DF = pd.read_csv(DATA_PATH)

def find_cves_for_tech(tech_name: str):
    results = CVE_DF[CVE_DF["description"].str.contains(tech_name, case=False, na=False)]
    return results[["cve_id", "cvss_score", "exploitability_score", "severity", "description"]].to_dict(orient="records")