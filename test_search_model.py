"""
Test Search Model - Superconductor Search v2
============================================

Comprehensive testing of the trained search model.

Tests:
1. Previously failing queries (should be fixed)
2. Generic vs specific query discrimination
3. YouTube video inclusion in results
4. Material-specific queries
5. Person-specific queries
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import os

# Configuration
MODEL_PATH = 'models/superconductor-search-v2'
INDEX_DIR = 'search_index'
TOP_K = 5  # Number of results to return

class SearchEngine:
    """Semantic search engine using trained model."""

    def __init__(self, model_path: str, index_dir: str):
        print("🔧 Initializing Search Engine...")

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

        print(f"✅ Search engine initialized ({len(self.metadata):,} documents)")

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

    def print_results(self, query: str, results: List[Dict]):
        """Print search results in a readable format."""
        print(f"\n🔍 Query: \"{query}\"")
        print("─" * 70)

        for result in results:
            rank = result['rank']
            score = result['score']
            title = result['title'][:60]
            source = result['source']
            difficulty = result['difficulty']
            doc_id = result['id']

            # Difficulty labels
            diff_labels = ['Unspecified', 'Beginner', 'Intermediate', 'Advanced', 'Expert', 'Cutting-edge']
            diff_label = diff_labels[difficulty] if difficulty < len(diff_labels) else 'Unknown'

            print(f"\n{rank}. [{score:.4f}] {title}")
            print(f"   Source: {source} | Difficulty: {diff_label} | ID: {doc_id}")

            # Show preview
            preview = result.get('text_preview', '')[:100]
            if preview:
                print(f"   Preview: {preview}...")

def run_test_suite():
    """Run comprehensive test suite."""
    print("=" * 70)
    print("🧪 COMPREHENSIVE MODEL TESTING")
    print("=" * 70)

    # Initialize search engine
    search_engine = SearchEngine(MODEL_PATH, INDEX_DIR)

    # Define test queries
    test_cases = {
        "Previously Failing Queries": [
            "what is superconductivity",
            "iron-based superconductors",
            "cooper pairs",
        ],
        "Generic vs Specific": [
            "superconductivity basics",
            "BCS theory derivation",
            "high temperature superconductor mechanisms",
        ],
        "Material-Specific": [
            "cuprate superconductors",
            "MgB2 superconductor",
            "iron pnictides",
        ],
        "Person-Specific": [
            "Brian Josephson contributions",
            "Leon Cooper research",
            "who discovered BCS theory",
        ],
        "Phenomenon-Specific": [
            "meissner effect",
            "flux pinning",
            "quantum levitation",
        ],
    }

    # Run tests
    for category, queries in test_cases.items():
        print("\n" + "=" * 70)
        print(f"📋 {category.upper()}")
        print("=" * 70)

        for query in queries:
            results = search_engine.search(query, k=5)
            search_engine.print_results(query, results)

            # Check for issues
            print("\n   📊 Analysis:")

            # Check YouTube inclusion
            youtube_count = sum(1 for r in results if 'youtube' in r['source'])
            print(f"      - YouTube videos: {youtube_count}/5")

            # Check for biographical content in generic queries
            if any(word in query.lower() for word in ['what is', 'basics', 'explain']):
                # Generic query - should NOT return biographical content
                bio_keywords = ['biography', 'life', 'born', 'died', 'career', 'award']
                bio_count = 0
                for r in results:
                    title_lower = r['title'].lower()
                    if any(kw in title_lower for kw in bio_keywords):
                        bio_count += 1
                        print(f"      ⚠️  Biographical result detected: {r['title'][:50]}")

                if bio_count == 0:
                    print(f"      ✅ No biographical content (good for generic query)")

            # Check relevance for specific queries
            if any(material in query.lower() for material in ['iron', 'cuprate', 'mgb2', 'pnictide']):
                # Material-specific query - check if results match material
                print(f"      - Material-specific query detected")
                for r in results[:3]:  # Check top 3
                    title_lower = r['title'].lower()
                    if any(word in title_lower for word in query.lower().split()):
                        print(f"      ✅ Relevant match: {r['title'][:50]}")

    # Summary statistics
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    all_queries = [q for queries in test_cases.values() for q in queries]
    print(f"\n✅ Tested {len(all_queries)} queries across {len(test_cases)} categories")

    print("\n🎯 Key Improvements to Verify:")
    print("   1. Generic queries should NOT return biographical content")
    print("   2. Material-specific queries should return relevant materials")
    print("   3. YouTube videos should appear in search results")
    print("   4. Semantic matching (not just keyword matching)")

    print("\n" + "=" * 70)
    print("✅ TESTING COMPLETE")
    print("=" * 70 + "\n")

def test_specific_case():
    """Test the specific failing case mentioned by user."""
    print("=" * 70)
    print("🎯 SPECIFIC TEST: Previously Failing Query")
    print("=" * 70)

    search_engine = SearchEngine(MODEL_PATH, INDEX_DIR)

    # The query that was returning Brian Josephson biographical content
    query = "what is superconductivity"

    print(f"\n📝 Original Problem:")
    print(f"   Query: \"{query}\"")
    print(f"   Expected: Generic explanation of superconductivity")
    print(f"   Previously got: Brian Josephson biographical videos")
    print(f"   Should be fixed: Hard negatives prevent bio content matching generic queries")

    results = search_engine.search(query, k=10)
    search_engine.print_results(query, results)

    # Check if Brian Josephson appears
    print("\n🔍 Checking for biographical content...")
    josephson_found = False
    for r in results:
        if 'josephson' in r['title'].lower() and 'brian' in r['title'].lower():
            josephson_found = True
            print(f"   ❌ Found Brian Josephson at rank {r['rank']}: {r['title']}")

    if not josephson_found:
        print(f"   ✅ No Brian Josephson biographical content in top 10!")
        print(f"   ✅ ISSUE FIXED!")
    else:
        print(f"   ⚠️  Still finding biographical content - may need more training")

    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    # Run specific test case first
    print("\n🚀 Running specific test case...\n")
    test_specific_case()

    # Run full test suite
    print("\n🚀 Running full test suite...\n")
    run_test_suite()
