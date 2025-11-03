#!/usr/bin/env python3
"""
HyperPhysics Scraper - Georgia State University Physics Resource
================================================================

HyperPhysics provides excellent intermediate-level physics explanations
with concept maps and interconnected topics. Perfect for Level 2 content.

Target: 15-20 superconductivity pages
Difficulty level: 2-3 (Intermediate)
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from urllib.parse import urljoin, urlparse

OUTPUT_FILE = "data/raw/hyperphysics_articles.json"
BASE_URL = "http://hyperphysics.phy-astr.gsu.edu/hbase/"

# Starting URLs for superconductivity content
SEED_URLS = [
    "http://hyperphysics.phy-astr.gsu.edu/hbase/Solids/scond.html",
    "http://hyperphysics.phy-astr.gsu.edu/hbase/Solids/coper.html",
    "http://hyperphysics.phy-astr.gsu.edu/hbase/Solids/meis.html",
    "http://hyperphysics.phy-astr.gsu.edu/hbase/Solids/joe.html",
    "http://hyperphysics.phy-astr.gsu.edu/hbase/Solids/squid.html",
    "http://hyperphysics.phy-astr.gsu.edu/hbase/Solids/bcs.html",
]


def scrape_hyperphysics_page(url: str) -> Dict:
    """Scrape a single HyperPhysics page."""
    try:
        print(f"  Fetching: {url.split('/')[-1]}...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title (HyperPhysics pages often have title in first header or filename)
        title_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
        if title_elem:
            title = title_elem.get_text().strip()
        else:
            # Fall back to filename
            title = url.split('/')[-1].replace('.html', '').replace('_', ' ').title()

        # Extract main content
        # HyperPhysics has simple structure, usually in body or main divs
        body = soup.find('body')

        if not body:
            print(f"    ⚠️  Could not find body")
            return None

        # Remove scripts, styles, navigation
        for unwanted in body.find_all(['script', 'style', 'nav', 'footer', 'iframe']):
            unwanted.decompose()

        # Get text content from paragraphs, divs, lists
        text_elements = []

        for elem in body.find_all(['p', 'div', 'li']):
            text = elem.get_text().strip()
            if text and len(text) > 20:  # Meaningful content
                text_elements.append(text)

        content = '\n\n'.join(text_elements)

        # Clean up excessive whitespace
        content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])

        word_count = len(content.split())

        if word_count < 50:
            print(f"    ⏭️  Too short ({word_count} words)")
            return None

        doc = {
            'id': f"hyperphysics_{url.split('/')[-1].replace('.html', '')}",
            'source': 'hyperphysics',
            'type': 'educational',
            'title': title,
            'url': url,
            'content': content,
            'word_count': word_count,
            'difficulty_level': 2,  # Intermediate
            'institution': 'Georgia State University',
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
    print("📚 HYPERPHYSICS SCRAPER - Intermediate Physics Concepts")
    print("="*80)
    print(f"Target: {len(SEED_URLS)} pages")
    print(f"Source: Georgia State University")
    print(f"Output: {OUTPUT_FILE}\n")

    documents = []
    seen_urls = set()

    for idx, url in enumerate(SEED_URLS, 1):
        if url in seen_urls:
            continue

        seen_urls.add(url)
        print(f"[{idx}/{len(SEED_URLS)}]", end=" ")

        doc = scrape_hyperphysics_page(url)
        if doc:
            documents.append(doc)

        time.sleep(1)  # Be respectful

    # Save results
    print("\n" + "="*80)
    print(f"✅ Collected {len(documents)}/{len(SEED_URLS)} articles")
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
