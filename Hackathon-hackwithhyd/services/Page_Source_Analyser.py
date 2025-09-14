#!/usr/bin/env python3
"""
page_scanner.py

Fetch fully-rendered HTML (Playwright) and analyze for suspicious indicators.
Usage:
    python page_scanner.py https://example.com
"""

import sys
import re
import json
from urllib.parse import urlparse, urljoin

# Optional dependency imports with graceful fallback
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

import requests
from bs4 import BeautifulSoup
import tldextract
from datetime import datetime

# ---------- Fetching ----------

def fetch_with_playwright(url, timeout=15000):
    """Return rendered HTML using Playwright (headless)."""
    if not PLAYWRIGHT_AVAILABLE:
        raise RuntimeError("Playwright not available.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800}, java_script_enabled=True)
        try:
            page.goto(url, timeout=timeout, wait_until="networkidle")
        except Exception:
            # try a less strict wait
            try:
                page.goto(url, timeout=timeout)
            except Exception as e:
                browser.close()
                raise
        html = page.content()
        # capture DOM after rendering; also capture current URL (redirects)
        final_url = page.url
        browser.close()
        return html, final_url

def fetch_with_requests(url, timeout=10):
    """Simple GET fetch (no JS execution)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    return r.text, r.url

def fetch_full_page(url):
    """Try Playwright first, fallback to requests."""
    try:
        if PLAYWRIGHT_AVAILABLE:
            html, final = fetch_with_playwright(url)
            method = "playwright"
        else:
            raise RuntimeError("No playwright")
    except Exception as e:
        html, final = fetch_with_requests(url)
        method = "requests"
    return {"html": html, "final_url": final, "method": method, "fetched_at": datetime.utcnow().isoformat() + "Z"}

# ---------- Analysis ----------

# Helper regexes
BASE64_RE = re.compile(r"(?:[A-Za-z0-9+/]{40,}={0,2})")
EVAL_RE = re.compile(r"\beval\(", re.IGNORECASE)
ATOB_RE = re.compile(r"\batob\(", re.IGNORECASE)
DOCUMENT_WRITE_RE = re.compile(r"\bdocument\.write\(", re.IGNORECASE)
META_REFRESH_RE = re.compile(r'<meta[^>]+http-equiv=["\']refresh["\']', re.IGNORECASE)
SUSPICIOUS_TLDS = { "tk","cn","ru","xyz","top" }  # heuristic TLDs often abused; adjust as needed
CRYPTO_MINER_SIGNATURES = [
    r"WebAssembly\.instantiate",    # wasm miner clues
    r"coinhive",                    # old miner
    r"miner",                       # generic word
    r"wasm", 
    r"cryptonight", 
    r"asmCrypto"
]

def domain_of(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""

def analyze_html(html, original_url):
    findings = []
    score_factors = {"feed_flag": 0, "source_analysis": 0, "url_pattern": 0, "history": 0}
    soup = BeautifulSoup(html, "html.parser")

    # Basic page metrics
    scripts = soup.find_all("script")
    iframes = soup.find_all("iframe")
    forms = soup.find_all("form")
    meta = soup.find_all("meta")
    links = soup.find_all("a")

    # 1) Check meta-refresh
    if META_REFRESH_RE.search(str(meta)):
        findings.append({"type":"meta_refresh", "desc":"Meta refresh / auto-redirect detected"})
        score_factors["source_analysis"] += 15

    # 2) Hidden iframe detection
    hidden_iframes = []
    for ifr in iframes:
        w = (ifr.get("width") or "").strip()
        h = (ifr.get("height") or "").strip()
        style = (ifr.get("style") or "").lower()
        src = ifr.get("src") or ""
        if ("0" in (w+h)) or ("display:none" in style) or ("visibility:hidden" in style):
            hidden_iframes.append(src)
    if hidden_iframes:
        findings.append({"type":"hidden_iframes", "desc":"Hidden iframes found", "count": len(hidden_iframes), "examples": hidden_iframes[:3]})
        score_factors["source_analysis"] += 25

    # 3) JS obfuscation & eval/atob/document.write
    obf_count = 0
    long_base64_found = []
    eval_count = 0
    miner_signatures = []
    for s in scripts:
        text = s.string or ""
        if not text:
            # if external script (src), record it
            src = s.get("src")
            if src:
                # external script tracking could be done separately
                pass
            continue
        if EVAL_RE.search(text) or DOCUMENT_WRITE_RE.search(text) or ATOB_RE.search(text):
            eval_count += 1
        # base64 large string detection
        if BASE64_RE.search(text):
            long_base64_found.append(True)
        # check miner patterns
        for pat in CRYPTO_MINER_SIGNATURES:
            if re.search(pat, text, re.IGNORECASE):
                miner_signatures.append(pat)
    if eval_count > 0:
        findings.append({"type":"obfuscated_js", "desc":f"Use of eval/atob/document.write found in inline scripts ({eval_count} occurrences)"})
        score_factors["source_analysis"] += 25
    if long_base64_found:
        findings.append({"type":"base64_payload", "desc":"Long base64-like strings found in inline scripts (possible encoded payloads)"})
        score_factors["source_analysis"] += 20
    if miner_signatures:
        findings.append({"type":"crypto_miner", "desc":"Crypto-miner-like signatures found in inline scripts", "signatures": list(set(miner_signatures))})
        score_factors["source_analysis"] += 30

    # 4) Forms posting to external domains (phishing indicator)
    phishing_forms = []
    orig_domain = domain_of(original_url)
    for f in forms:
        action = (f.get("action") or "").strip()
        if not action:
            # often forms without action submit to same origin - less suspicious
            continue
        # normalize relative action
        action_full = urljoin(original_url, action)
        action_domain = domain_of(action_full)
        if action_domain and action_domain != orig_domain:
            phishing_forms.append({"form_action": action_full})
    if phishing_forms:
        findings.append({"type":"phishing_forms", "desc":"Forms submit to external / mismatched domains", "examples": phishing_forms[:3]})
        score_factors["source_analysis"] += 35

    # 5) Many external script loads (could be ad/malvertising or trackers)
    external_script_count = 0
    external_script_examples = []
    for s in scripts:
        src = s.get("src")
        if src:
            # consider script external if domain differs from original
            src_domain = domain_of(urljoin(original_url, src))
            if src_domain and src_domain != orig_domain:
                external_script_count += 1
                if len(external_script_examples) < 5:
                    external_script_examples.append(src)
    if external_script_count > 10:
        findings.append({"type":"many_external_scripts", "desc":f"Large number of external scripts ({external_script_count}) loaded; may include trackers/malvertising", "examples": external_script_examples})
        score_factors["source_analysis"] += 15

    # 6) Link / anchor analysis for suspicious patterns (typosquatting, IP in URL)
    suspicious_links = []
    for a in links:
        href = a.get("href") or ""
        if href:
            parsed = urlparse(href)
            # IP address usage
            if re.match(r"^https?://\d+\.\d+\.\d+\.\d+", href):
                suspicious_links.append({"href": href, "reason": "IP in URL"})
            # check for bad TLD
            ext = tldextract.extract(href)
            if ext.suffix and ext.suffix.lower() in SUSPICIOUS_TLDS:
                suspicious_links.append({"href": href, "reason": f"Suspicious TLD .{ext.suffix}"})
    if suspicious_links:
        findings.append({"type":"suspicious_links", "desc":"Suspicious links found in page", "examples": suspicious_links[:5]})
        score_factors["url_pattern"] += 15

    # 7) SSL / certificate cues - we can't inspect cert via HTML, but mention if URL is http
    parsed_orig = urlparse(original_url)
    if parsed_orig.scheme and parsed_orig.scheme.lower() == "http":
        findings.append({"type":"no_tls", "desc":"URL served over HTTP (no TLS) - phishing sites often lack valid TLS"})
        score_factors["url_pattern"] += 10

    # 8) Domain age heuristic via tldextract (we can only infer length of domain string; for real domain age use WHOIS)
    ext = tldextract.extract(original_url)
    domain_name = ".".join(part for part in [ext.domain, ext.suffix] if part)
    if domain_name:
        # heuristic: short-lived-looking domains (random chars) -> increase suspicion
        if re.search(r"[0-9]{4,}", ext.domain) or len(ext.domain) > 25 or len(ext.domain) < 3:
            findings.append({"type":"domain_heuristic", "desc":"Domain name looks suspicious by simple heuristics (very long / numeric)"})
            score_factors["url_pattern"] += 10

    # 9) Content-brand mismatch (very naive): if page references known brand words but domain != brand
    # simple brand keywords list (extend as required)
    brand_keywords = ["paypal", "google", "microsoft", "amazon", "apple", "bankofamerica", "chase", "hsbc"]
    text_lower = soup.get_text(separator=" ").lower()
    brands_found = [b for b in brand_keywords if b in text_lower]
    mismatched_brands = []
    for b in brands_found:
        if b not in orig_domain:
            mismatched_brands.append(b)
    if mismatched_brands:
        findings.append({"type":"brand_mismatch", "desc":"Page contains brand keywords not matching domain (possible credential phishing)", "brands": mismatched_brands[:5]})
        score_factors["source_analysis"] += 30

    # 10) Final scoring: combine factors into a 0-100 score
    # weighted aggregation (tunable)
    # weights:
    weights = {"feed_flag": 0.0, "source_analysis": 0.5, "url_pattern": 0.3, "history": 0.2}
    # normalize factors roughly to max potentials observed
    # For simplicity, cap each factor to 100 then compute weighted sum
    for k in score_factors:
        if score_factors[k] > 100: score_factors[k] = 100
    raw_score = (weights["feed_flag"] * score_factors["feed_flag"]
                 + weights["source_analysis"] * score_factors["source_analysis"]
                 + weights["url_pattern"] * score_factors["url_pattern"]
                 + weights["history"] * score_factors["history"])
    score = int(min(100, round(raw_score)))

    # verdict thresholds (tunable)
    if score >= 70:
        verdict = "Malicious"
    elif score >= 35:
        verdict = "Suspicious"
    else:
        verdict = "Safe"

    result = {
        "verdict": verdict,
        "score": score,
        "score_factors": score_factors,
        "raw_findings_count": len(findings),
        "findings": findings,
        "page_metrics": {
            "num_scripts": len(scripts),
            "num_iframes": len(iframes),
            "num_forms": len(forms),
            "num_links": len(links)
        }
    }
    return result

# ---------- CLI ----------

def scan_page(url: str):
    fetched = fetch_full_page(url)
    html = fetched['html']
    analysis = analyze_html(html, fetched['final_url'])
    print(json.dumps({
        "url_submitted": url,
        "final_url": fetched['final_url'],
        "fetched_by": fetched['method'],
        "fetched_at": fetched['fetched_at'],
        "analysis": analysis
    }, indent=2))
    return {
        "url_submitted": url,
        "final_url": fetched['final_url'],
        "fetched_by": fetched['method'],
        "fetched_at": fetched['fetched_at'],
        "analysis": analysis
    }

