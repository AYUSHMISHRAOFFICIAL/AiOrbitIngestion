import re
from bs4 import BeautifulSoup
from typing import Optional

def strip_html(html_content: str) -> str:
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ")
    return text

def clean_text(text: Optional[str], max_length: int = 2000) -> Optional[str]:
    if text is None:
        return None
        
    # Ensure text is a string
    if not isinstance(text, str):
        text = str(text)
        
    # Strip HTML if any
    if "<" in text and ">" in text:
        text = strip_html(text)
    
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text:
        return None
        
    if len(text) > max_length:
        text = text[:max_length] + "..."
        
    return text
