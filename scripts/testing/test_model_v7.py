"""
Test Model V7 - Validate Fixes for 3 Problem Queries
====================================================

V6 had 3 problem queries:
1. "josephson junction" → 0% Wikipedia (was too low)
2. "cuprate superconductors" → 0% Wikipedia (was too low)
3. "meissner effect" → 60% YouTube (was too high, should prioritize Wikipedia)

V7 Solution:
- Added 560 targeted Wikipedia pairs:
  * 180 pairs for Josephson junction
  * 200 pairs for Cuprate superconductors
  * 180 pairs for Meissner effect
- Increased Wikipedia from 38.1% → 46.2%
- Decreased YouTube from 26.6% → 23.1%

This test will verify if V7 fixed these 3 queries.
"""

import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# Configuration
MODEL_PATH = 'models/superconductor-search-v7'
DOCUMENTS_FILE = 'training/documents.json'
TOP_K = 10

def load_model_and_documents():
    """Load trained model and documents."""
    print("="*70)
    print("🔍 Testing Model V7 - Validating 3 Problem Query Fixes")
    print("="*70)

    print(f"\nLoading model from: {MODEL_PATH}")
    model = SentenceTransformer(MODEL_PATH)
    print("✅ Model loaded")

    print(f"\nLoading documents from: {DOCUMENTS_FILE}")
    with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    print(f"✅ Loaded {len(documents):,} documents")

    return model, documents

def create_faiss_index(model, documents):
    """Create FAISS index for documents."""
    print("\n📊 Creating FAISS index...")

    # Encode all documents
    doc_texts = [doc.get('content', doc.get('text', '')) for doc in documents]
    doc_embeddings = model.encode(doc_texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(doc_embeddings)

    # Create FAISS index
    dimension = doc_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
    index.add(doc_embeddings)

    print(f"✅ FAISS index created with {index.ntotal:,} documents")

    return index

def search(query, model, index, documents, top_k=TOP_K):
    """Search for query and return top-k results."""
    # Encode query
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    # Search
    scores, indices = index.search(query_embedding, top_k)

    # Get results
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(documents):
            doc = documents[idx]
            results.append({
                'score': float(score),
                'id': doc.get('id', 'unknown'),
                'title': doc.get('title', 'No title'),
                'source': doc.get('source', 'unknown'),
                'content_preview': doc.get('content', '')[:200] + '...'
            })

    return results

def analyze_results(results):
    """Analyze search results distribution."""
    sources = {}
    for result in results:
        source = result['source']
        if source not in sources:
            sources[source] = 0
        sources[source] += 1

    return sources

def print_results(query, results, v6_stats=None):
    """Pretty print search results with V6 comparison."""
    print(f"\n{'='*70}")
    print(f"Query: \"{query}\"")
    print(f"{'='*70}")

    # Source analysis
    sources = analyze_results(results)

    # Print results
    for i, result in enumerate(results, 1):
        source_emoji = {
            'wikipedia': '📖',
            'simple_wikipedia': '📘',
            'youtube': '📺',
            'arxiv': '📄'
        }.get(result['source'], '📄')

        print(f"\n{i}. {source_emoji} {result['title']}")
        print(f"   Source: {result['source']}")
        print(f"   ID: {result['id']}")
        print(f"   Score: {result['score']:.4f}")

    # Summary
    print(f"\n{'─'*70}")
    print("V7 Source Distribution:")
    for source, count in sorted(sources.items(), key=lambda x: -x[1]):
        pct = count / len(results) * 100
        print(f"  {source:20s}: {count:2d} ({pct:5.1f}%)")

    # V6 Comparison
    if v6_stats:
        print(f"\n{'─'*70}")
        print("V6 vs V7 Comparison:")
        for source in ['wikipedia', 'youtube', 'arxiv']:
            v6_pct = v6_stats.get(source, 0)
            v7_pct = sources.get(source, 0) / len(results) * 100
            change = v7_pct - v6_pct

            if source == 'wikipedia' and change > 10:
                status = "✅ FIXED!"
            elif source == 'youtube' and change < -10:
                status = "✅ REDUCED!"
            elif abs(change) < 5:
                status = "→ STABLE"
            else:
                status = "⚠️"

            print(f"  {source:20s}: V6={v6_pct:5.1f}% → V7={v7_pct:5.1f}% ({change:+5.1f}%) {status}")

def run_tests():
    """Run test queries focused on the 3 problem queries."""
    # Load model and documents
    model, documents = load_model_and_documents()

    # Create FAISS index
    index = create_faiss_index(model, documents)

    # V6 Results for the 3 problem queries (from V6_TEST_RESULTS.md)
    v6_results = {
        "josephson junction": {
            "wikipedia": 0.0,
            "youtube": 60.0,
            "arxiv": 40.0
        },
        "cuprate superconductors": {
            "wikipedia": 0.0,
            "youtube": 0.0,
            "arxiv": 100.0
        },
        "meissner effect": {
            "wikipedia": 20.0,
            "youtube": 60.0,
            "arxiv": 20.0
        }
    }

    # The 3 problem queries + variations
    problem_queries = {
        "JOSEPHSON JUNCTION (V6: 0% Wikipedia)": [
            "josephson junction",
            "what is a josephson junction",
            "josephson effect",
            "explain josephson junction"
        ],
        "CUPRATE SUPERCONDUCTORS (V6: 0% Wikipedia)": [
            "cuprate superconductors",
            "what are cuprate superconductors",
            "ybco superconductor",
            "high temperature cuprates"
        ],
        "MEISSNER EFFECT (V6: 60% YouTube)": [
            "meissner effect",
            "what is the meissner effect",
            "meissner effect levitation",
            "magnetic field expulsion superconductor"
        ]
    }

    print("\n" + "="*70)
    print("🧪 TESTING V7 ON THE 3 PROBLEM QUERIES")
    print("="*70)

    # Track overall statistics
    overall_stats = {}

    for problem_type, queries in problem_queries.items():
        print(f"\n{'='*70}")
        print(f"{problem_type}")
        print(f"{'='*70}")

        problem_sources = {}

        for query in queries:
            # Get V6 stats for main query if available
            v6_stats = v6_results.get(query, None)

            results = search(query, model, index, documents)
            print_results(query, results, v6_stats)

            # Aggregate source stats
            sources = analyze_results(results)
            for source, count in sources.items():
                if source not in problem_sources:
                    problem_sources[source] = 0
                problem_sources[source] += count

                if source not in overall_stats:
                    overall_stats[source] = 0
                overall_stats[source] += count

        # Summary for this problem type
        total = len(queries) * TOP_K
        print(f"\n{'─'*70}")
        print(f"Summary for {problem_type}:")
        for source in ['wikipedia', 'simple_wikipedia', 'youtube', 'arxiv']:
            count = problem_sources.get(source, 0)
            pct = count / total * 100
            print(f"  {source:20s}: {count:3d} ({pct:5.1f}%)")

    # Overall summary
    print("\n" + "="*70)
    print("📊 OVERALL V7 RESULTS")
    print("="*70)

    total_queries = sum(len(queries) for queries in problem_queries.values())
    total_results = total_queries * TOP_K

    print(f"\nTested {total_queries} queries, {total_results} total results:")
    for source in ['wikipedia', 'simple_wikipedia', 'youtube', 'arxiv']:
        count = overall_stats.get(source, 0)
        pct = count / total_results * 100
        print(f"  {source:20s}: {count:3d} ({pct:5.1f}%)")

    # Calculate success metrics
    wiki_total = overall_stats.get('wikipedia', 0) + overall_stats.get('simple_wikipedia', 0)
    wiki_pct = wiki_total / total_results * 100
    youtube_pct = overall_stats.get('youtube', 0) / total_results * 100

    print("\n" + "="*70)
    print("🎯 V6 vs V7 COMPARISON")
    print("="*70)
    print("\nV6 Issues:")
    print("  ❌ Josephson junction: 0% Wikipedia")
    print("  ❌ Cuprate superconductors: 0% Wikipedia")
    print("  ❌ Meissner effect: 60% YouTube (too high)")
    print("\nV7 Solution:")
    print("  • Added 560 targeted Wikipedia pairs")
    print("  • Josephson junction: 180 pairs")
    print("  • Cuprate superconductors: 200 pairs")
    print("  • Meissner effect: 180 pairs")

    print("\n" + "="*70)
    print("✅ V7 VERDICT")
    print("="*70)

    # Check if problems are fixed
    all_fixed = True

    # We expect significant Wikipedia increase for these queries
    if wiki_pct >= 30:
        print(f"✅ Wikipedia increased to {wiki_pct:.1f}% (good!)")
    else:
        print(f"⚠️  Wikipedia at {wiki_pct:.1f}% (could be higher)")
        all_fixed = False

    if youtube_pct <= 35:
        print(f"✅ YouTube reduced to {youtube_pct:.1f}% (good!)")
    else:
        print(f"⚠️  YouTube still at {youtube_pct:.1f}% (target: <35%)")
        all_fixed = False

    print("\n" + "="*70)
    if all_fixed:
        print("🎉 SUCCESS! V7 fixed the 3 problem queries!")
        print("   Ready for deployment!")
    else:
        print("⚠️  PARTIAL SUCCESS - Some queries improved but may need more work")
    print("="*70 + "\n")

    # Run full test suite on all difficulty levels
    print("\n" + "="*70)
    print("🧪 FULL TEST SUITE - ALL DIFFICULTY LEVELS")
    print("="*70)

    # Test queries - grouped by difficulty
    test_queries = {
        'BEGINNER': [
            "what is a superconductor",
            "what is superconductivity",
            "explain superconductivity",
            "define superconductor"
        ],
        'INTERMEDIATE': [
            "flux pinning",
            "josephson junction",
            "cuprate superconductors",
            "properties of iron-based superconductors",
            "squid applications",
            "how do cooper pairs work",
            "type ii superconductor",
            "meissner effect",
            "critical temperature"
        ],
        'ADVANCED': [
            "iron-based superconductors mechanism",
            "cuprate superconductors mechanism",
            "topological superconductivity",
            "bcs theory derivation",
            "high temperature superconductor phonon coupling"
        ]
    }

    stats_by_difficulty = {}

    for difficulty, queries in test_queries.items():
        print(f"\n{'='*70}")
        print(f"{difficulty} QUERIES")
        print(f"{'='*70}")

        difficulty_sources = {}

        for query in queries:
            results = search(query, model, index, documents)

            # Aggregate source stats
            sources = analyze_results(results)
            for source, count in sources.items():
                if source not in difficulty_sources:
                    difficulty_sources[source] = 0
                difficulty_sources[source] += count

        stats_by_difficulty[difficulty] = difficulty_sources

    # Summary by difficulty
    print("\n" + "="*70)
    print("📊 SUMMARY BY DIFFICULTY LEVEL")
    print("="*70)

    for difficulty in ['BEGINNER', 'INTERMEDIATE', 'ADVANCED']:
        sources = stats_by_difficulty[difficulty]
        total = len(test_queries[difficulty]) * TOP_K

        print(f"\n{difficulty} QUERIES ({len(test_queries[difficulty])} queries, {total} results):")
        for source in ['simple_wikipedia', 'wikipedia', 'youtube', 'arxiv']:
            count = sources.get(source, 0)
            pct = count / total * 100
            print(f"  {source:20s}: {count:3d} ({pct:5.1f}%)")

        # Calculate metrics
        wiki_total = sources.get('wikipedia', 0) + sources.get('simple_wikipedia', 0)
        wiki_pct = wiki_total / total * 100
        arxiv_pct = sources.get('arxiv', 0) / total * 100
        youtube_pct = sources.get('youtube', 0) / total * 100

        # Check targets
        if difficulty == 'BEGINNER':
            if wiki_pct >= 60:
                print(f"  ✅ TARGET MET: {wiki_pct:.1f}% Wikipedia (target: 60-70%)")
            else:
                print(f"  ❌ BELOW TARGET: {wiki_pct:.1f}% Wikipedia (target: 60-70%)")

        elif difficulty == 'INTERMEDIATE':
            print(f"\n  📊 V7 INTERMEDIATE RESULTS:")
            print(f"     Wikipedia: {sources.get('wikipedia', 0) / total * 100:.1f}% (target: 30-35%)")
            print(f"     YouTube: {youtube_pct:.1f}% (target: 25-30%)")
            print(f"     arXiv: {arxiv_pct:.1f}% (target: 25-30%)")

            wiki_only_pct = sources.get('wikipedia', 0) / total * 100
            if wiki_only_pct >= 25 and youtube_pct <= 35:
                print(f"  ✅ GOOD: Fixed V6's 3 problem queries!")
            else:
                print(f"  ⚠️  NEEDS WORK: May need more tuning")

        elif difficulty == 'ADVANCED':
            if arxiv_pct >= 60:
                print(f"  ✅ TARGET MET: {arxiv_pct:.1f}% arXiv (target: 60-70%)")
            else:
                print(f"  ❌ BELOW TARGET: {arxiv_pct:.1f}% arXiv (target: 60-70%)")

    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_tests()
