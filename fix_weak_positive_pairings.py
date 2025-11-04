"""
Fix Weak Positive Pairings
===========================

Remove positive query-document pairs where the document only tangentially
mentions the query topic. Ensures strong semantic relevance.

Criteria for STRONG positive pairing:
1. Material-specific query → Document must be PRIMARILY about that material
2. Keyword query → Keyword must appear multiple times OR be in title
3. Topic query → Topic must be a main focus, not just mentioned
"""

import json
import re
from typing import Dict, List, Set
from datetime import datetime
from collections import Counter

# Configuration
INPUT_FILE = 'data/processed/queries_with_hard_negatives_20251104_224640.json'
DOCUMENTS_FILE = 'data/processed/FINAL_ALL_IMPROVED_documents_20251104_223630.json'
OUTPUT_FILE = f'data/processed/queries_strong_positives_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

def count_keyword_occurrences(text: str, keyword: str) -> int:
    """Count how many times a keyword appears in text."""
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    return len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text_lower))

def is_primary_topic(text: str, title: str, keyword: str, min_occurrences: int = 3) -> bool:
    """
    Check if keyword is a PRIMARY topic (not just mentioned in passing).

    Strong indicators:
    - Appears in title
    - Appears multiple times in text
    - Appears in first 200 characters (likely in abstract/intro)
    """
    text_lower = text.lower()
    title_lower = title.lower()
    keyword_lower = keyword.lower()

    # Check title (strongest signal)
    if keyword_lower in title_lower:
        return True

    # Count occurrences
    count = count_keyword_occurrences(text, keyword)

    # Check if appears early (in abstract/intro)
    appears_early = keyword_lower in text_lower[:200]

    # Primary topic if: appears early AND appears multiple times
    if appears_early and count >= min_occurrences:
        return True

    # Or if appears many times throughout
    if count >= 5:
        return True

    return False

def is_material_specific_strong(query: str, doc: Dict) -> bool:
    """
    Check if material-specific query is strongly relevant to document.

    Material queries: cuprate, pnictide, iron-based, nickelate, etc.
    """
    material_keywords = {
        'cuprate': ['cuprate', 'ybco', 'bscco'],
        'pnictide': ['pnictide', 'iron-based', 'iron pnictide'],
        'iron-based': ['iron-based', 'pnictide', 'fese', 'febas'],
        'nickelate': ['nickelate', 'nickel'],
        'mgb2': ['mgb2', 'magnesium diboride'],
        'ybco': ['ybco', 'yttrium barium'],
        'graphene': ['graphene'],
        'organic': ['organic superconductor', 'fullerene']
    }

    query_lower = query.lower()
    text = doc.get('content', doc.get('text', ''))
    title = doc.get('title', '')

    # Identify which material is being queried
    material = None
    for mat, keywords in material_keywords.items():
        if any(kw in query_lower for kw in keywords):
            material = mat
            break

    if not material:
        return True  # Not a material query, skip this check

    # Check if document is primarily about this material
    material_kws = material_keywords[material]

    for kw in material_kws:
        if is_primary_topic(text, title, kw, min_occurrences=3):
            return True

    return False

def is_concept_specific_strong(query: str, doc: Dict) -> bool:
    """
    Check if concept-specific query is strongly relevant.

    Concepts: cooper pairs, meissner effect, josephson junction, etc.
    """
    concept_keywords = {
        'cooper pair': 3,
        'meissner effect': 2,
        'josephson': 2,
        'bcs theory': 2,
        'flux pinning': 2,
        'critical current': 3,
        'vortex': 4,  # Common word, needs more occurrences
        'pairing mechanism': 2,
        'd-wave': 2,
        's-wave': 2,
        'pseudogap': 2
    }

    query_lower = query.lower()
    text = doc.get('content', doc.get('text', ''))
    title = doc.get('title', '')

    # Check if query is about a specific concept
    for concept, min_count in concept_keywords.items():
        if concept in query_lower:
            # Check if document focuses on this concept
            if is_primary_topic(text, title, concept, min_occurrences=min_count):
                return True
            else:
                return False  # Weak pairing

    return True  # Not a concept query, skip

def is_generic_query(query: str) -> bool:
    """Check if query is generic (should match many documents)."""
    generic_patterns = [
        'what is',
        'how do',
        'explain',
        'introduction',
        'basics',
        'superconductivity',
        'superconductor',
        'superconducting materials',
        'superconducting properties',
        'how superconductors work'
    ]

    query_lower = query.lower()

    # Exact matches for very generic queries
    if query_lower in ['superconductivity', 'superconductor', 'superconducting']:
        return True

    return any(pattern in query_lower for pattern in generic_patterns)

def calculate_relevance_score(query: str, doc: Dict) -> float:
    """
    Calculate relevance score (0-1) for query-document pair.

    Returns:
        1.0 = Very strong match
        0.5-0.9 = Moderate match
        0.0-0.5 = Weak match (should be removed)
    """
    text = doc.get('content', doc.get('text', ''))
    title = doc.get('title', '')

    # Handle empty or dict text
    if not text or isinstance(text, dict):
        text = ''
    if not title or isinstance(title, dict):
        title = ''

    query_lower = query.lower()
    score = 0.0

    # Generic queries should match most documents
    if is_generic_query(query):
        # As long as doc is about superconductivity, it's fine
        if 'supercond' in text.lower():
            return 1.0
        return 0.3

    # Extract main keywords from query (ignore stopwords)
    stopwords = {'what', 'is', 'are', 'the', 'a', 'an', 'in', 'of', 'for', 'to', 'and'}
    query_words = [w for w in query_lower.split() if w not in stopwords and len(w) > 2]

    if not query_words:
        return 0.5  # Can't assess

    # Check each keyword
    keyword_scores = []
    for keyword in query_words:
        # Title match (strongest)
        if keyword in title.lower():
            keyword_scores.append(1.0)
            continue

        # Count occurrences in text
        count = count_keyword_occurrences(text, keyword)

        if count >= 5:
            keyword_scores.append(1.0)
        elif count >= 3:
            keyword_scores.append(0.8)
        elif count >= 1:
            keyword_scores.append(0.5)
        else:
            keyword_scores.append(0.0)

    # Average keyword scores
    if keyword_scores:
        score = sum(keyword_scores) / len(keyword_scores)

    return score

def filter_weak_positive_pairings(queries: List[Dict], documents: List[Dict]) -> List[Dict]:
    """
    Remove weak positive pairings from dataset.
    Keep only STRONG positive matches.
    """
    print("="*70)
    print("🔍 Filtering Weak Positive Pairings")
    print("="*70)

    # Create document lookup
    doc_lookup = {doc['id']: doc for doc in documents}

    filtered_queries = []
    weak_pairings_removed = 0
    relevance_stats = []

    print("\n1️⃣ Analyzing positive pairs...")

    for query in queries:
        # Keep all negative pairs as-is
        if query['label'] == 0:
            filtered_queries.append(query)
            continue

        # For positive pairs, check relevance
        doc_id = query['doc_id']
        doc = doc_lookup.get(doc_id)

        if not doc:
            weak_pairings_removed += 1
            continue

        query_text = query['query_text']

        # Calculate relevance score
        relevance_score = calculate_relevance_score(query_text, doc)
        relevance_stats.append(relevance_score)

        # STRICT THRESHOLD: Only keep if relevance >= 0.5
        if relevance_score >= 0.5:
            filtered_queries.append(query)
        else:
            weak_pairings_removed += 1

    # Statistics
    print(f"\n✅ Filtering complete:")
    print(f"   - Weak positive pairings removed: {weak_pairings_removed:,}")
    print(f"   - Strong positive pairings kept: {sum(1 for q in filtered_queries if q['label'] == 1):,}")
    print(f"   - Negative pairings kept: {sum(1 for q in filtered_queries if q['label'] == 0):,}")

    if relevance_stats:
        avg_relevance = sum(relevance_stats) / len(relevance_stats)
        print(f"\n📊 Relevance scores (before filtering):")
        print(f"   - Average: {avg_relevance:.2f}")
        print(f"   - < 0.3 (very weak): {sum(1 for s in relevance_stats if s < 0.3):,}")
        print(f"   - 0.3-0.5 (weak): {sum(1 for s in relevance_stats if 0.3 <= s < 0.5):,}")
        print(f"   - 0.5-0.7 (moderate): {sum(1 for s in relevance_stats if 0.5 <= s < 0.7):,}")
        print(f"   - 0.7-0.9 (strong): {sum(1 for s in relevance_stats if 0.7 <= s < 0.9):,}")
        print(f"   - >= 0.9 (very strong): {sum(1 for s in relevance_stats if s >= 0.9):,}")

    return filtered_queries

def show_sample_removed_pairs(queries_before: List[Dict], queries_after: List[Dict],
                              documents: List[Dict], num_samples: int = 5):
    """Show examples of removed weak pairings."""
    doc_lookup = {doc['id']: doc for doc in documents}

    # Find removed positive pairs
    before_pos = {(q['query_text'], q['doc_id']) for q in queries_before if q['label'] == 1}
    after_pos = {(q['query_text'], q['doc_id']) for q in queries_after if q['label'] == 1}
    removed = before_pos - after_pos

    print("\n2️⃣ Sample removed weak pairings:")
    print("="*70)

    for i, (query_text, doc_id) in enumerate(list(removed)[:num_samples], 1):
        doc = doc_lookup.get(doc_id)
        if not doc:
            continue

        text = doc.get('content', doc.get('text', ''))
        title = doc.get('title', '')

        # Calculate why it was removed
        score = calculate_relevance_score(query_text, doc)

        print(f"\n{i}. Query: \"{query_text}\"")
        print(f"   Doc: {doc_id}")
        print(f"   Title: {title[:80]}...")
        print(f"   Relevance score: {score:.2f}")
        print(f"   Text snippet: {text[:150]}...")
        print(f"   ❌ Removed: Score below 0.5 threshold")

def main():
    print("="*70)
    print("🎯 Fix Weak Positive Pairings")
    print("="*70)

    # Load data
    print("\n📂 Loading data...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
        doc_data = json.load(f)
        documents = doc_data['documents']

    print(f"   ✅ Loaded {len(queries):,} query pairs")
    print(f"   ✅ Loaded {len(documents):,} documents")

    original_positives = sum(1 for q in queries if q['label'] == 1)
    original_negatives = sum(1 for q in queries if q['label'] == 0)

    print(f"\n📊 Original dataset:")
    print(f"   - Positive pairs: {original_positives:,}")
    print(f"   - Negative pairs: {original_negatives:,}")

    # Filter weak pairings
    filtered_queries = filter_weak_positive_pairings(queries, documents)

    # Show samples
    show_sample_removed_pairs(queries, filtered_queries, documents, num_samples=10)

    # Save
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(filtered_queries, f, indent=2, ensure_ascii=False)

    # Final statistics
    final_positives = sum(1 for q in filtered_queries if q['label'] == 1)
    final_negatives = sum(1 for q in filtered_queries if q['label'] == 0)

    sep = "="*70
    print(f"\n{sep}")
    print("✅ WEAK PAIRING REMOVAL COMPLETE!")
    print(sep)
    print(f"📊 Final Dataset:")
    print(f"   - Total pairs: {len(filtered_queries):,}")
    print(f"   - Positive pairs: {final_positives:,} (was {original_positives:,})")
    print(f"   - Negative pairs: {final_negatives:,} (unchanged)")
    print(f"   - Removed: {original_positives - final_positives:,} weak positive pairs")
    print(f"   - Positive ratio: {final_positives/len(filtered_queries)*100:.1f}%")

    print(f"\n🎯 Next steps:")
    print(f"   1. Review sample removed pairs above")
    print(f"   2. Regenerate hard negatives with clean positive pairs")
    print(f"   3. Retrain model with high-quality dataset")
    print(f"{sep}\n")

if __name__ == "__main__":
    main()
