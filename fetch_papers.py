import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# Primary Category Scope
CATEGORIES = 'cat:physics.chem-ph OR cat:quant-ph'

# Updated strict keywords based on your latest research focus (Case-Insensitive)
MUST_MATCH_KEYWORDS = [
    r'quantum chemistry', 
    r'\bNISQ\b', 
    r'\bVQE\b', 
    r'quantum variational', 
    r'quantum computing', 
    r'\bQML\b', 
    r'quantum machine learning', 
    r'electronic structure'
]

URL = f'http://export.arxiv.org/api/query?search_query={urllib.parse.quote(CATEGORIES)}&sortBy=submittedDate&sortOrder=descending&max_results=60'

def is_relevant(text):
    """Check if the title or abstract contains at least one target keyword."""
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
        
        # Local strict filter against title and abstract
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
             f"> Focus: Quantum Chemistry / NISQ / VQE / Quantum Computing / QML / Electronic Structure\n\n"
    
    if papers:
        content = header + "\n---\n\n".join(papers)
    else:
        content = header + "No relevant papers matching your criteria were found today.\n"
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
