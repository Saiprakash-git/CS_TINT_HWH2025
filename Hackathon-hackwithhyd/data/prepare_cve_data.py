import requests
import zipfile
import io
import json
import pandas as pd

# Step 1: Download CVE-2025 ZIP file (Schema 2.0)
url = "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2025.json.zip"
print("[INFO] Downloading CVE-2025 feed...")
response = requests.get(url)

# Step 2: Unzip
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    json_filename = z.namelist()[0]  # should be nvdcve-2.0-2025.json
    with z.open(json_filename) as f:
        data = json.load(f)

# Step 3: Parse JSON (Schema 2.0 structure)
vulns = data["vulnerabilities"]
records = []

for item in vulns:
    cve = item["cve"]
    cve_id = cve["id"]
    description = cve.get("descriptions", [{}])[0].get("value", "")

    # Default values
    cvss_score, severity, exploitability = None, None, None

    metrics = cve.get("metrics", {})
    if "cvssMetricV31" in metrics:
        metric = metrics["cvssMetricV31"][0]
        cvss_score = metric["cvssData"]["baseScore"]
        severity = metric["cvssData"]["baseSeverity"]
        exploitability = metric.get("exploitabilityScore")
    elif "cvssMetricV30" in metrics:
        metric = metrics["cvssMetricV30"][0]
        cvss_score = metric["cvssData"]["baseScore"]
        severity = metric["cvssData"]["baseSeverity"]
        exploitability = metric.get("exploitabilityScore")

    records.append({
        "cve_id": cve_id,
        "description": description,
        "cvss_score": cvss_score,
        "severity": severity,
        "exploitability_score": exploitability
    })

# Step 4: Create DataFrame
df = pd.DataFrame(records)
print(f"[INFO] Extracted {len(df)} CVEs")

# Step 5: Save CSV
df.to_csv("cve_2025_dataset.csv", index=False)
print("[INFO] Saved dataset as cve_2025_dataset.csv")