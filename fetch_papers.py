import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

# Logical query covering Quantum Chemistry / CI / PT2 / GPU Acceleration / QML
QUERY = '(cat:physics.chem-ph OR cat:quant-ph OR cat:cs.LG OR cat:physics.comp-ph) AND ' \
        '(ti:"configuration interaction" OR ti:"PT2" OR ti:"CASPT2" OR ti:"NEPT2" OR ' \
        'abs:"GPU" OR abs:"quantum machine learning" OR abs:"QML" OR abs:"electronic structure")'

URL = f'http://export.arxiv.org/api/query?search_query={urllib.parse.quote(QUERY)}&sortBy=submittedDate&sortOrder=descending&max_results=30'

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
        
        # PDF link extraction
        pdf_link = link.replace('/abs/', '/pdf/') + ".pdf"
        
        # Extract authors
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
        
        # Extract summary
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        
        papers.append(
            f"### [{title}]({link})\n"
            f"* **Date**: `{published}` | **Authors**: {author_str} | [[PDF]]({pdf_link})\n"
            f"* **Abstract**: {summary[:350]}...\n"
        )
    return papers

if __name__ == '__main__':
    papers = fetch_arxiv()
    today = datetime.now().strftime('%B %d, %Y')
    
    header = f"# 🚀 Daily arXiv Tracker ({today})\n\n" \
             f"> Focus: Quantum Chemistry / CI / PT2 / GPU Acceleration / QML\n\n"
    
    if papers:
        content = header + "\n---\n\n".join(papers)
    else:
        content = header + "No relevant papers found today.\n"
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
