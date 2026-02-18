import requests
from bs4 import BeautifulSoup
import re

def scrape_url(url: str) -> str:
    """
    Fetches content from a URL and returns clean text.
    """
    import time
    
    # Modern headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Referer': 'https://www.google.com/'
    }

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            print(f"DEBUG: Requesting {url} (Attempt {attempt+1}/{max_retries+1})...")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                break
                
            print(f"DEBUG: Failed to retrieve {url}. Status Code: {response.status_code}")
            if attempt == max_retries:
                raise Exception(f"HTTP Error {response.status_code}")
            
            # Simple backoff
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Network Error: {e}")
            if attempt == max_retries:
                raise Exception(f"Network error accessing URL: {str(e)}")
            time.sleep(1)
            
    try:    
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts, styles, and other non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "meta", "noscript", "iframe", "svg", "form", "button", "link"]):
            element.extract()
            
        # Get text
        text = soup.get_text(separator=' ')
        
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text or len(text) < 50:
             # Sometimes anti-bot pages have very little text
            print("DEBUG: Very little text extracted. Possible bot block or empty page.")
            if "captcha" in response.text.lower() or "security check" in response.text.lower():
                 raise Exception("Access Denied: Security Check / CAPTCHA detected.")
            if not text:
                 return ""

        # Specific Cleaning for Wikipedia/MediaWiki style artifacts
        # Remove citation marks like [1], [12], [edit]
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[edit\]', '', text)
        
        # Remove "Retrieved from..." lines
        text = re.sub(r'Retrieved from ".*?"', '', text)
        
        # Remove excess whitespace again after cleaning
        text = re.sub(r'\s+', ' ', text).strip()
            
        return text

    except Exception as e:
        print(f"DEBUG: Scraping Error: {e}")
        raise Exception(f"Failed to scrape URL: {str(e)}")

def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Sentence-aware overlapping chunker.
    Splits text into chunks of approximately `chunk_size` words, 
    attempting to break at sentence boundaries, with `overlap` words.
    """
    # Split into sentences (simple regex for punctuation)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_length = len(sentence_words)
        
        # If adding this sentence doesn't exceed chunk size significantly, add it
        if current_length + sentence_length <= chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            # Chunk is full, finalize it
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            # Start new chunk with overlap
            # Try to keep the last few sentences as overlap
            overlap_words = []
            overlap_len = 0
            
            # Work backwards to find overlap
            for prev_sent in reversed(current_chunk):
                prev_len = len(prev_sent.split())
                if overlap_len + prev_len <= overlap:
                    overlap_words.insert(0, prev_sent)
                    overlap_len += prev_len
                else:
                    break
            
            current_chunk = overlap_words + [sentence]
            current_length = overlap_len + sentence_length
            
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
