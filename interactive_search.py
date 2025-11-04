"""
Interactive Search - Superconductor Search v2
==============================================

Interactive command-line search interface for testing queries.
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os

# Configuration
MODEL_PATH = 'models/superconductor-search-v2'
INDEX_DIR = 'search_index'
TOP_K = 10  # Number of results to return

class InteractiveSearch:
    """Interactive search interface."""

    def __init__(self, model_path: str, index_dir: str):
        print("=" * 70)
        print("🔍 SUPERCONDUCTOR SEARCH ENGINE V2 - INTERACTIVE MODE")
        print("=" * 70)
        print("\n🔧 Initializing search engine...")

        # Load model
        print(f"   Loading model: {model_path}")
        self.model = SentenceTransformer(model_path)

        # Load FAISS index
        index_path = os.path.join(index_dir, 'faiss_index.bin')
        print(f"   Loading index: {index_path}")
        self.index = faiss.read_index(index_path)

        # Load metadata
        metadata_path = os.path.join(index_dir, 'document_metadata.json')
        print(f"   Loading metadata: {metadata_path}")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        print(f"\n✅ Search engine ready!")
        print(f"   📚 {len(self.metadata):,} documents indexed")
        print(f"   🧠 {self.index.d}-dimensional embeddings")
        print("=" * 70)

    def search(self, query: str, k: int = TOP_K) -> List[Dict]:
        """Search for documents matching the query."""
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)

        # Search
        scores, indices = self.index.search(query_embedding, k)

        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(score)
                result['rank'] = i + 1
                results.append(result)

        return results

    def print_results(self, query: str, results: List[Dict], num_to_show: int = 10):
        """Print search results in a readable format."""
        print(f"\n{'=' * 70}")
        print(f"🔍 Query: \"{query}\"")
        print(f"{'=' * 70}")
        print(f"Found {len(results)} results. Showing top {num_to_show}:")
        print()

        for result in results[:num_to_show]:
            rank = result['rank']
            score = result['score']
            title = result['title']
            source = result['source']
            difficulty = result['difficulty']
            doc_id = result['id']

            # Difficulty labels
            diff_labels = ['Unspecified', 'Beginner', 'Intermediate', 'Advanced', 'Expert', 'Cutting-edge']
            diff_label = diff_labels[difficulty] if difficulty < len(diff_labels) else 'Unknown'

            # Format source
            source_emoji = {
                'arxiv': '📄',
                'youtube': '📺',
                'wikipedia': '📖',
                'simple_wikipedia': '📖',
                'mit_ocw': '🎓',
            }
            emoji = source_emoji.get(source, '📋')

            print(f"{rank}. [{score:.4f}] {emoji} {title}")
            print(f"   Source: {source} | Difficulty: {diff_label}")

            # Show URL if available
            url = result.get('url', '')
            if url:
                if source == 'youtube':
                    full_url = f"https://youtube.com/watch?v={url}" if not url.startswith('http') else url
                    print(f"   URL: {full_url}")
                elif url.startswith('http'):
                    print(f"   URL: {url}")

            # Show preview
            preview = result.get('text_preview', '')[:150]
            if preview:
                print(f"   Preview: {preview}...")

            print()

    def run(self):
        """Run interactive search loop."""
        print("\n💡 Type your search query and press Enter.")
        print("   Commands:")
        print("   - Type 'quit' or 'exit' to exit")
        print("   - Type 'help' for suggestions")
        print("   - Type a number (e.g., '5') to change number of results shown")
        print()

        num_results = 10

        while True:
            try:
                query = input("🔍 Search: ").strip()

                if not query:
                    continue

                # Check for commands
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                if query.lower() == 'help':
                    print("\n💡 Suggested queries to try:")
                    print("   Generic queries:")
                    print("   - what is superconductivity")
                    print("   - cooper pairs")
                    print("   - BCS theory")
                    print()
                    print("   Material-specific:")
                    print("   - iron-based superconductors")
                    print("   - cuprate superconductors")
                    print("   - MgB2 superconductor")
                    print()
                    print("   Phenomena:")
                    print("   - meissner effect")
                    print("   - flux pinning")
                    print("   - quantum levitation")
                    print()
                    print("   People:")
                    print("   - Brian Josephson contributions")
                    print("   - who discovered BCS theory")
                    print()
                    continue

                # Check if it's a number (change results count)
                if query.isdigit():
                    num_results = int(query)
                    print(f"✅ Now showing {num_results} results per query")
                    continue

                # Perform search
                results = self.search(query, k=TOP_K)
                self.print_results(query, results, num_to_show=num_results)

                # Quick analysis
                youtube_count = sum(1 for r in results[:num_results] if 'youtube' in r['source'])
                arxiv_count = sum(1 for r in results[:num_results] if 'arxiv' in r['source'])

                print(f"📊 Quick stats:")
                print(f"   YouTube videos: {youtube_count}/{num_results}")
                print(f"   arXiv papers: {arxiv_count}/{num_results}")
                print(f"   Top score: {results[0]['score']:.4f}")
                print()

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.\n")

def main():
    """Main function."""
    search = InteractiveSearch(MODEL_PATH, INDEX_DIR)
    search.run()

if __name__ == "__main__":
    main()
