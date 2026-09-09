import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# 1. Primary Category Scope
CATEGORIES = 'cat:physics.chem-ph OR cat:quant-ph'

# 2. Strict keywords for local post-filtering (Case-Insensitive)
MUST_MATCH_KEYWORDS = [
    r'\bCI\b', r'configuration interaction', r'PT2', r'CASPT2', r'NEPT2', 
    r'multireference', r'GPU', r'QML', r'quantum machine learning', 
    r'electronic structure', r'tensor network', r'DMRG'
]

URL = f'http://export.arxiv.org/api/query?search_query={urllib.parse.quote(CATEGORIES)}&sortBy=submittedDate&sortOrder=descending&max_results=50'

def is_relevant(text):
    """Check if the title/abstract contains at least one target keyword."""
    for pattern in MUST_MATCH_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def fetch_arxiv():
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Fetch failed: {e}")
        return []

    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        link = entry.find('atom:id', ns).text.strip()
        published = entry.find('atom:published', ns).text[:10]
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        
        # Local strict filter
        full_text = f"{title} {summary}"
        if not is_relevant(full_text):
            continue

        pdf_link = link.replace('/abs/', '/pdf/') + ".pdf"
        
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
        
        papers.append(
            f"### [{title}]({link})\n"
            f"* **Date**: `{published}` | **Authors**: {author_str} | [[PDF]]({pdf_link})\n"
            f"* **Abstract**: {summary[:350]}...\n"
        )
        
        # Limit to top 15 highly relevant papers
        if len(papers) >= 15:
            break

    return papers

if __name__ == '__main__':
    papers = fetch_arxiv()
    today = datetime.now().strftime('%B %d, %Y')
    
    header = f"# 🚀 Daily arXiv Tracker ({today})\n\n" \
             f"> Focus: Quantum Chemistry / CI / PT2 / GPU Acceleration / QML\n\n"
    
    if papers:
        content = header + "\n---\n\n".join(papers)
    else:
        content = header + "No relevant papers matching your criteria were found today.\n"
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
