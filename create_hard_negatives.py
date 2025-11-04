"""
Create Smart Hard Negatives for Contrastive Learning
====================================================

Fixes the issue where basic queries match biographical documents.
Creates hard negatives that make semantic sense:
- Historical figures should NOT match "what is superconductivity"
- Generic theory docs should NOT match "who is John Bardeen"
- Papers about specific materials should NOT match queries about other materials
"""

import json
import random
from typing import List, Dict, Set
from datetime import datetime

# Configuration
DOCUMENTS_FILE = 'data/processed/FINAL_ALL_IMPROVED_documents_20251104_223630.json'
QUERIES_FILE = 'data/processed/FINAL_ALL_IMPROVED_queries_with_general_20251104_223630.json'
OUTPUT_FILE = f'data/processed/queries_with_hard_negatives_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

def identify_biographical_docs(documents: List[Dict]) -> Set[str]:
    """
    Identify documents that are primarily biographical/historical.
    These should only match person-specific queries.
    """
    biographical_doc_ids = set()

    bio_indicators = [
        'bardeen', 'cooper', 'schrieffer', 'kamerlingh', 'onnes',
        'ginzburg', 'landau', 'josephson', 'london', 'nobel',
        'biography', 'physicist', 'professor', 'discovered by',
        'invented by', 'life of', 'career', 'born in', 'died'
    ]

    for doc in documents:
        text = doc.get('text', '').lower()
        title = doc.get('title', '').lower()

        # Check for biographical content
        bio_score = sum(1 for indicator in bio_indicators if indicator in text or indicator in title)

        # If multiple biographical indicators, likely biographical
        if bio_score >= 3:
            biographical_doc_ids.add(doc['id'])

    return biographical_doc_ids

def identify_material_specific_docs(documents: List[Dict]) -> Dict[str, Set[str]]:
    """
    Identify documents about specific materials.
    E.g., cuprate papers should NOT match "iron-based superconductors" queries.
    """
    material_docs = {
        'cuprate': set(),
        'pnictide': set(),
        'iron-based': set(),
        'nickelate': set(),
        'mgb2': set(),
        'ybco': set(),
        'graphene': set(),
        'organic': set()
    }

    for doc in documents:
        text = doc.get('text', '').lower()
        title = doc.get('title', '').lower()

        if 'cuprate' in text or 'cuprate' in title:
            material_docs['cuprate'].add(doc['id'])
        if 'pnictide' in text or 'iron-based' in text or 'iron pnictide' in text:
            material_docs['pnictide'].add(doc['id'])
            material_docs['iron-based'].add(doc['id'])
        if 'nickelate' in text or 'nickelate' in title:
            material_docs['nickelate'].add(doc['id'])
        if 'mgb2' in text or 'magnesium diboride' in text:
            material_docs['mgb2'].add(doc['id'])
        if 'ybco' in text or 'yttrium barium' in text:
            material_docs['ybco'].add(doc['id'])
        if 'graphene' in text or 'graphene' in title:
            material_docs['graphene'].add(doc['id'])
        if 'organic superconductor' in text or 'fullerene' in text:
            material_docs['organic'].add(doc['id'])

    return material_docs

def is_generic_query(query_text: str) -> bool:
    """Check if query is generic/broad."""
    generic_patterns = [
        'what is',
        'how do',
        'explain',
        'introduction to',
        'basics of',
        'superconductivity',
        'superconductor',
        'superconducting materials',
        'superconducting properties',
        'how superconductors work'
    ]

    query_lower = query_text.lower()
    return any(pattern in query_lower for pattern in generic_patterns)

def is_person_specific_query(query_text: str) -> bool:
    """Check if query is about a specific person."""
    person_indicators = [
        'bardeen', 'cooper', 'schrieffer', 'josephson', 'ginzburg',
        'landau', 'onnes', 'kamerlingh', 'nobel prize', 'who discovered',
        'who invented', 'physicist', 'professor'
    ]

    query_lower = query_text.lower()
    return any(indicator in query_lower for indicator in person_indicators)

def get_material_from_query(query_text: str) -> str:
    """Extract material type from query."""
    query_lower = query_text.lower()

    if 'cuprate' in query_lower:
        return 'cuprate'
    elif 'pnictide' in query_lower or 'iron-based' in query_lower or 'iron pnictide' in query_lower:
        return 'pnictide'
    elif 'nickelate' in query_lower:
        return 'nickelate'
    elif 'mgb2' in query_lower or 'magnesium diboride' in query_lower:
        return 'mgb2'
    elif 'ybco' in query_lower:
        return 'ybco'
    elif 'graphene' in query_lower:
        return 'graphene'
    elif 'organic' in query_lower or 'fullerene' in query_lower:
        return 'organic'

    return None

def create_hard_negatives(queries: List[Dict], documents: List[Dict]) -> List[Dict]:
    """
    Create smart hard negatives for contrastive learning.

    Rules:
    1. Generic queries should have biographical docs as hard negatives
    2. Person-specific queries should have generic theory docs as hard negatives
    3. Material-specific queries should have docs about OTHER materials as hard negatives
    """
    print("="*70)
    print("🔍 Creating Smart Hard Negatives")
    print("="*70)

    # Identify document types
    print("\n1️⃣ Identifying document types...")
    biographical_docs = identify_biographical_docs(documents)
    material_docs = identify_material_specific_docs(documents)

    print(f"   ✅ Found {len(biographical_docs)} biographical documents")
    print(f"   ✅ Found material-specific documents:")
    for material, docs in material_docs.items():
        if docs:
            print(f"      - {material}: {len(docs)} docs")

    # Create document lookup
    doc_lookup = {doc['id']: doc for doc in documents}

    # Get all doc IDs by type
    all_doc_ids = set(doc['id'] for doc in documents)
    generic_theory_docs = all_doc_ids - biographical_docs

    # Process queries and add hard negatives
    print("\n2️⃣ Creating hard negatives...")
    new_queries = []
    hard_neg_stats = {
        'generic_query_bio_negative': 0,
        'person_query_theory_negative': 0,
        'material_query_other_material': 0
    }

    for query in queries:
        # Keep original positive pair
        new_queries.append(query)

        query_text = query['query_text']
        positive_doc_id = query['doc_id']

        # Rule 1: Generic queries → biographical docs as negatives
        if is_generic_query(query_text):
            # Sample 2-3 biographical docs as hard negatives
            available_bio_docs = biographical_docs - {positive_doc_id}
            if available_bio_docs:
                num_negatives = min(2, len(available_bio_docs))
                negative_docs = random.sample(list(available_bio_docs), num_negatives)

                for neg_doc_id in negative_docs:
                    new_queries.append({
                        'query_text': query_text,
                        'query_difficulty': query.get('query_difficulty', 2),
                        'doc_id': neg_doc_id,
                        'doc_text': doc_lookup[neg_doc_id].get('text', ''),
                        'doc_difficulty': doc_lookup[neg_doc_id].get('difficulty_level', 2),
                        'label': 0,  # NEGATIVE
                        'pair_type': 'hard_negative_generic_to_bio'
                    })
                    hard_neg_stats['generic_query_bio_negative'] += 1

        # Rule 2: Person-specific queries → generic theory docs as negatives
        elif is_person_specific_query(query_text):
            # Sample 2-3 generic theory docs as hard negatives
            available_theory_docs = generic_theory_docs - biographical_docs - {positive_doc_id}
            if available_theory_docs:
                num_negatives = min(2, len(available_theory_docs))
                negative_docs = random.sample(list(available_theory_docs), num_negatives)

                for neg_doc_id in negative_docs:
                    new_queries.append({
                        'query_text': query_text,
                        'query_difficulty': query.get('query_difficulty', 2),
                        'doc_id': neg_doc_id,
                        'doc_text': doc_lookup[neg_doc_id].get('text', ''),
                        'doc_difficulty': doc_lookup[neg_doc_id].get('difficulty_level', 2),
                        'label': 0,  # NEGATIVE
                        'pair_type': 'hard_negative_person_to_theory'
                    })
                    hard_neg_stats['person_query_theory_negative'] += 1

        # Rule 3: Material-specific queries → other material docs as negatives
        query_material = get_material_from_query(query_text)
        if query_material:
            # Get docs from OTHER materials
            other_material_docs = set()
            for material, docs in material_docs.items():
                if material != query_material:
                    other_material_docs.update(docs)

            available_other_material = other_material_docs - {positive_doc_id}
            if available_other_material:
                num_negatives = min(2, len(available_other_material))
                negative_docs = random.sample(list(available_other_material), num_negatives)

                for neg_doc_id in negative_docs:
                    new_queries.append({
                        'query_text': query_text,
                        'query_difficulty': query.get('query_difficulty', 2),
                        'doc_id': neg_doc_id,
                        'doc_text': doc_lookup[neg_doc_id].get('text', ''),
                        'doc_difficulty': doc_lookup[neg_doc_id].get('difficulty_level', 2),
                        'label': 0,  # NEGATIVE
                        'pair_type': 'hard_negative_material_mismatch'
                    })
                    hard_neg_stats['material_query_other_material'] += 1

    # Statistics
    print(f"\n✅ Hard negatives created:")
    print(f"   - Generic query → Bio doc: {hard_neg_stats['generic_query_bio_negative']:,}")
    print(f"   - Person query → Theory doc: {hard_neg_stats['person_query_theory_negative']:,}")
    print(f"   - Material query → Other material: {hard_neg_stats['material_query_other_material']:,}")
    print(f"\n📊 Dataset statistics:")
    print(f"   - Original queries: {len(queries):,}")
    print(f"   - Total pairs (with negatives): {len(new_queries):,}")
    print(f"   - Positive pairs: {sum(1 for q in new_queries if q['label'] == 1):,}")
    print(f"   - Negative pairs: {sum(1 for q in new_queries if q['label'] == 0):,}")

    positive_count = sum(1 for q in new_queries if q['label'] == 1)
    negative_count = sum(1 for q in new_queries if q['label'] == 0)
    pos_ratio = positive_count / len(new_queries) * 100
    print(f"   - Positive ratio: {pos_ratio:.1f}%")

    return new_queries

def remove_bad_pairings(queries: List[Dict], documents: List[Dict]) -> List[Dict]:
    """
    Remove positive pairs that don't make sense.
    E.g., biographical docs with generic queries.
    """
    print("\n3️⃣ Removing bad positive pairings...")

    biographical_docs = identify_biographical_docs(documents)

    filtered_queries = []
    removed_count = 0

    for query in queries:
        query_text = query['query_text']
        doc_id = query['doc_id']
        is_positive = query['label'] == 1

        # Remove if: positive pair + generic query + biographical doc
        if is_positive and is_generic_query(query_text) and doc_id in biographical_docs:
            removed_count += 1
            continue

        filtered_queries.append(query)

    print(f"   ❌ Removed {removed_count} bad positive pairs")
    print(f"   ✅ Kept {len(filtered_queries):,} pairs")

    return filtered_queries

def main():
    print("="*70)
    print("🎯 Smart Hard Negative Creation")
    print("="*70)

    # Load data
    print("\n📂 Loading data...")
    with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
        doc_data = json.load(f)
        documents = doc_data['documents']

    with open(QUERIES_FILE, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    print(f"   ✅ Loaded {len(documents):,} documents")
    print(f"   ✅ Loaded {len(queries):,} queries")

    # Create hard negatives
    queries_with_negatives = create_hard_negatives(queries, documents)

    # Remove bad pairings
    final_queries = remove_bad_pairings(queries_with_negatives, documents)

    # Save
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_queries, f, indent=2, ensure_ascii=False)

    # Final statistics
    sep = "="*70
    print(f"\n{sep}")
    print("✅ HARD NEGATIVE CREATION COMPLETE!")
    print(sep)
    print(f"📊 Final Dataset:")
    print(f"   - Total pairs: {len(final_queries):,}")
    print(f"   - Positive pairs: {sum(1 for q in final_queries if q['label'] == 1):,}")
    print(f"   - Negative pairs: {sum(1 for q in final_queries if q['label'] == 0):,}")

    pos_count = sum(1 for q in final_queries if q['label'] == 1)
    neg_count = sum(1 for q in final_queries if q['label'] == 0)
    print(f"   - Ratio: {pos_count:,} positive : {neg_count:,} negative")
    print(f"   - Positive %: {pos_count/len(final_queries)*100:.1f}%")

    print(f"\n🎯 Next steps:")
    print(f"   1. Review sample hard negatives")
    print(f"   2. Retrain model with new dataset")
    print(f"   3. Evaluate against test queries")
    print(f"{sep}\n")

if __name__ == "__main__":
    random.seed(42)  # Reproducibility
    main()
