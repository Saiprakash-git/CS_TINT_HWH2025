# services/page_source_analyser.py

from .Page_Source_Analyser import fetch_full_page, analyze_html

def scan_page(url: str):
    """Wrapper for FastAPI usage. Returns analysis JSON."""
    fetched = fetch_full_page(url)
    html = fetched['html']
    analysis = analyze_html(html, fetched['final_url'])

    return {
        "url_submitted": url,
        "final_url": fetched['final_url'],
        "fetched_by": fetched['method'],
        "fetched_at": fetched['fetched_at'],
        "analysis": analysis
    }
