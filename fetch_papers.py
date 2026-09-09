import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

# 涵盖 CI/PT2/GPU/QML 交叉方向的逻辑检索表达式
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
        
        # 提取作者
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        author_str = ", ".join(authors[:3]) + (" 等" if len(authors) > 3 else "")
        
        # 提取摘要
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        
        papers.append(
            f"### [{title}]({link})\n"
            f"* **发表日期**: `{published}` | **作者**: {author_str}\n"
            f"* **摘要**: {summary[:350]}...\n"
        )
    return papers

if __name__ == '__main__':
    papers = fetch_arxiv()
    today = datetime.now().strftime('%Y-%m-%d')
    
    header = f"# 🚀 arXiv 定向论文日报 ({today})\n\n" \
             f"> 覆盖方向：量子化学 / CI / PT2 / GPU 加速 / QML\n\n"
    
    if papers:
        content = header + "\n---\n\n".join(papers)
    else:
        content = header + "今日未检索到符合条件的最新论文。\n"
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
