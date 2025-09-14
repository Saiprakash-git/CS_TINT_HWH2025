import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, AnyHttpUrl, field_validator
from typing import List, Dict, Optional
import joblib


from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tech_fingerprinter import detect_technologies
from services.cve_lookup import find_cves_for_tech

from services.Page_Source_Analyser import scan_page


# Update model path to be relative to script location
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "risk_model.joblib")
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Cyber Risk Scoring API")

class URLRequest(BaseModel):
    url: str

    @field_validator('url')
    def validate_url(cls, v):
        # Add http:// if not present
        if not v.startswith(('http://', 'https://')):
            v = 'http://' + v
        return v

class VulnerabilityResponse(BaseModel):
    cve_id: str
    cvss_score: float
    exploitability_score: float
    severity: str
    description: str
    tech: str
    predicted_risk: float

class AnalysisResponse(BaseModel):
    url: str
    status: str
    technologies: List[str]
    overall_risk_score: float  # New field
    vulnerabilities: List[VulnerabilityResponse]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_url(request: URLRequest):
    try:
        url = request.url
        techs = detect_technologies(url)
        
        if not techs:
            return {
                "url": url,
                "status": "warning",
                "overall_risk_score": 0.0,
                "message": "No technologies detected",
                "technologies": [],
                "vulnerabilities": [], 
                "page_scanner": scan_page(url)
            }

        all_results = []
        total_risk = 0.0
        vuln_count = 0

        # Step 2: For each tech, lookup CVEs
        for tech in techs:
            try:
                vulns = find_cves_for_tech(tech)
                for v in vulns:
                    risk = float(model.predict([
                        [
                            float(v.get("cvss_score", 0)), 
                            float(v.get("exploitability_score", 0))
                        ]
                    ])[0])
                    v["predicted_risk"] = risk
                    v["tech"] = tech
                    all_results.append(v)
                    total_risk += risk
                    vuln_count += 1
            except Exception as e:
                print(f"Error processing tech {tech}: {str(e)}")
                continue

        # Calculate overall risk score
        overall_risk = total_risk / vuln_count if vuln_count > 0 else 0.0
        print("   ")
        print("   ")
        print("   ")
        print("   ")
        print("   ")
        print(url)
        scanner_result = scan_page(url)
        return {
            "url": url,
            "status": "success",
            "technologies": techs,
            "overall_risk_score": round(overall_risk, 2),
            "vulnerabilities": sorted(
                all_results[:10], 
                key=lambda x: x["predicted_risk"], 
                reverse=True
            ) ,
            "page_scanner": scanner_result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing URL: {str(e)}"
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
