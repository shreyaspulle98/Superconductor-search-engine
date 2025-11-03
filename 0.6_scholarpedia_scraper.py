#!/usr/bin/env python3
"""
Scholarpedia Scraper - Peer-Reviewed Encyclopedia
===================================================

Scholarpedia is a peer-reviewed open-access encyclopedia written by experts.
Higher quality than Wikipedia, more accessible than research papers.

Target: 10-15 high-quality articles on superconductivity
Difficulty level: 3-4 (Advanced)
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict

OUTPUT_FILE = "data/raw/scholarpedia_articles.json"

ARTICLE_URLS = [
    # Direct Scholarpedia articles on superconductivity
    "http://www.scholarpedia.org/article/Superconductivity",
    "http://www.scholarpedia.org/article/BCS_theory_of_superconductivity",
    "http://www.scholarpedia.org/article/High-temperature_superconductivity",
    "http://www.scholarpedia.org/article/Josephson_junction",
    "http://www.scholarpedia.org/article/Josephson_effect",
    "http://www.scholarpedia.org/article/Superconducting_qubits",
    "http://www.scholarpedia.org/article/SQUID",
    "http://www.scholarpedia.org/article/Quantum_vortices",
    "http://www.scholarpedia.org/article/Ginzburg-Landau_theory",
    "http://www.scholarpedia.org/article/Cooper_pairs",
]

def scrape_scholarpedia_article(url: str) -> Dict:
    """Scrape a single Scholarpedia article."""
    try:
        print(f"  Fetching: {url}...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title_elem = soup.find('h1', {'class': 'firstHeading'}) or soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else url.split('/')[-1]

        # Extract main content
        content_div = soup.find('div', {'id': 'mw-content-text'}) or soup.find('div', {'class': 'mw-parser-output'})

        if not content_div:
            print(f"    ⚠️  Could not find content div")
            return None

        # Remove unwanted elements
        for unwanted in content_div.find_all(['script', 'style', 'nav', 'footer']):
            unwanted.decompose()

        # Get text content
        paragraphs = content_div.find_all('p')
        content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        # Extract author info if available
        author_elem = soup.find('div', {'class': 'curators'})
        authors = []
        if author_elem:
            authors = [a.get_text().strip() for a in author_elem.find_all('a')]

        word_count = len(content.split())

        if word_count < 200:
            print(f"    ⏭️  Too short ({word_count} words)")
            return None

        doc = {
            'id': f"scholarpedia_{title.lower().replace(' ', '_')}",
            'source': 'scholarpedia',
            'type': 'peer_reviewed_encyclopedia',
            'title': title,
            'url': url,
            'content': content,
            'authors': authors,
            'word_count': word_count,
            'difficulty_level': 3,  # Advanced encyclopedia
            'collected_at': datetime.now().isoformat()
        }

        print(f"    ✅ {title} ({word_count} words)")
        return doc

    except requests.exceptions.RequestException as e:
        print(f"    ❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"    ❌ Parsing error: {e}")
        return None


def main():
    """Main scraping function."""
    print("\n" + "="*80)
    print("📚 SCHOLARPEDIA SCRAPER - Peer-Reviewed Encyclopedia")
    print("="*80)
    print(f"Target: {len(ARTICLE_URLS)} articles")
    print(f"Output: {OUTPUT_FILE}\n")

    documents = []

    for idx, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{idx}/{len(ARTICLE_URLS)}]", end=" ")

        doc = scrape_scholarpedia_article(url)
        if doc:
            documents.append(doc)

        time.sleep(2)  # Be respectful

    # Save results
    print("\n" + "="*80)
    print(f"✅ Collected {len(documents)}/{len(ARTICLE_URLS)} articles")
    print("="*80)

    if documents:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)

        total_words = sum(d['word_count'] for d in documents)
        print(f"\n💾 Saved to: {OUTPUT_FILE}")
        print(f"   Total words: {total_words:,}")
        print(f"   Average: {total_words // len(documents):,} words/article")
    else:
        print("\n⚠️  No articles collected")

    print()


if __name__ == "__main__":
    main()
