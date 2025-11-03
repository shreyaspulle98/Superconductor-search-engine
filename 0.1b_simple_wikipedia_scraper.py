#!/usr/bin/env python3
"""
Simple Wikipedia Scraper for Beginner-Level Superconductor Content
===================================================================

Simple Wikipedia uses simpler language and is perfect for beginner-level
educational content about superconductors.

Features:
- Scrapes Simple Wikipedia articles about superconductors
- Auto-categorizes as beginner level (difficulty 1-2)
- Extracts clean text content
- Provides metadata for semantic search
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import re


class SimpleWikipediaScraper:
    """Scraper for Simple Wikipedia articles on superconductors."""

    def __init__(self):
        self.base_url = "https://simple.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SuperconductorSearchBot/1.0 (Educational Research)'
        })

    def search_articles(self, query: str, limit: int = 20) -> List[str]:
        """
        Search Simple Wikipedia for articles.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of article titles
        """
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': limit,
            'format': 'json'
        }

        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            titles = [
                result['title']
                for result in data.get('query', {}).get('search', [])
            ]

            print(f"  Found {len(titles)} articles for '{query}'")
            return titles

        except Exception as e:
            print(f"  ❌ Error searching for '{query}': {e}")
            return []

    def get_article_content(self, title: str) -> Optional[Dict]:
        """
        Get full content of a Simple Wikipedia article.

        Args:
            title: Article title

        Returns:
            Dict with article content and metadata, or None if error
        """
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|info|categories',
            'explaintext': True,  # Plain text, no HTML
            'inprop': 'url',
            'format': 'json'
        }

        try:
            time.sleep(0.5)  # Rate limiting - be respectful

            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            page = list(pages.values())[0]

            if 'missing' in page:
                print(f"  ⚠️  Article '{title}' not found")
                return None

            # Extract content
            content = page.get('extract', '')

            # Clean up content
            content = self._clean_text(content)

            # Skip very short articles
            if len(content.split()) < 100:
                print(f"  ⚠️  Article '{title}' too short ({len(content.split())} words)")
                return None

            # Get categories
            categories = [
                cat.get('title', '').replace('Category:', '')
                for cat in page.get('categories', [])
            ]

            article_data = {
                'id': f'simple_wiki_{page["pageid"]}',
                'source': 'simple_wikipedia',
                'type': 'educational_article',
                'title': page.get('title', ''),
                'content': content,
                'url': page.get('fullurl', ''),
                'categories': categories,
                'word_count': len(content.split()),
                'difficulty_level': 1  # Simple Wikipedia = beginner level
            }

            return article_data

        except Exception as e:
            print(f"  ❌ Error fetching '{title}': {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove references like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)

        # Remove "== Section ==" markers
        text = re.sub(r'==+\s*', '', text)

        return text.strip()

    def scrape_superconductor_articles(self) -> List[Dict]:
        """
        Main scraping function - collects Simple Wikipedia articles.

        Returns:
            List of article data dictionaries
        """
        print("\n" + "="*80)
        print("🚀 SIMPLE WIKIPEDIA SCRAPER - BEGINNER CONTENT")
        print("="*80)
        print("Target: Beginner-friendly superconductor articles\n")

        # Search queries optimized for Simple Wikipedia
        search_queries = [
            'superconductor',
            'superconductivity',
            'electrical resistance',
            'electricity conductor',
            'magnetic levitation',
            'liquid nitrogen',
            'quantum mechanics',
            'BCS theory',
            'Meissner effect',
            'critical temperature',
            'type I superconductor',
            'type II superconductor',
            'high temperature superconductor',
            'room temperature superconductor',
            'YBCO',
            'liquid helium',
            'cryogenics',
            'quantum physics',
            'condensed matter physics',
            'materials science',
        ]

        all_titles = set()

        print("📊 PHASE 1: Searching for articles")
        print("="*80)

        for query in search_queries:
            titles = self.search_articles(query, limit=10)
            all_titles.update(titles)
            time.sleep(1)  # Rate limiting

        print(f"\n✅ Found {len(all_titles)} unique articles")

        print("\n📥 PHASE 2: Downloading article content")
        print("="*80)

        articles = []
        for idx, title in enumerate(all_titles, 1):
            print(f"[{idx}/{len(all_titles)}] Fetching: {title}")

            article = self.get_article_content(title)
            if article:
                articles.append(article)
                print(f"  ✅ Saved ({article['word_count']} words)")

        print(f"\n✅ Successfully scraped {len(articles)} articles")

        return articles

    def save_results(self, articles: List[Dict], output_file: str):
        """Save scraped articles to JSON file."""
        # Calculate statistics
        total_words = sum(a['word_count'] for a in articles)
        avg_words = total_words // len(articles) if articles else 0

        output_data = {
            'metadata': {
                'source': 'simple_wikipedia',
                'scrape_date': datetime.now().isoformat(),
                'total_articles': len(articles),
                'total_words': total_words,
                'average_words_per_article': avg_words,
                'difficulty_level': 1,
                'target_audience': 'beginners'
            },
            'articles': articles
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("✅ SCRAPING COMPLETE!")
        print("="*80)
        print(f"📊 Statistics:")
        print(f"   Articles collected: {len(articles)}")
        print(f"   Total words: {total_words:,}")
        print(f"   Average words/article: {avg_words:,}")
        print(f"   Difficulty level: 1 (Beginner)")
        print(f"\n💾 Saved to: {output_file}")


def main():
    """Main execution."""
    print("="*80)
    print("🚀 Simple Wikipedia Scraper - Beginner Superconductor Content")
    print("="*80)
    print()

    # Initialize scraper
    scraper = SimpleWikipediaScraper()

    # Scrape articles
    articles = scraper.scrape_superconductor_articles()

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/raw/simple_wikipedia_{timestamp}.json'
    scraper.save_results(articles, output_file)

    print("\n🎉 SUCCESS!")
    print(f"✅ Collected {len(articles)} beginner-friendly articles")
    print("✅ Ready for merging with main dataset\n")


if __name__ == "__main__":
    main()
