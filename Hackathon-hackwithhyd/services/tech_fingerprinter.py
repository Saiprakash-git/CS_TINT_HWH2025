import builtwith
import requests
from typing import List

def detect_technologies(url: str) -> List[str]:
    try:
        # Add http:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        # Get technology info
        tech_info = builtwith.parse(url)
        
        # Extract technology names
        technologies = []
        for category, techs in tech_info.items():
            technologies.extend(techs)
            
        return list(set(technologies))  # Remove duplicates
        
    except Exception as e:
        print(f"Error detecting technologies: {str(e)}")
        return []
