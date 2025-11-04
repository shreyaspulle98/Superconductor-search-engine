"""
Final Dataset Cleanup
=====================

Quick fixes:
1. Remove 1,700 duplicate pairs
2. Remove off-topic content (904 pairs with 'magnet' but not 'superconductor')
3. Keep data as-is otherwise (query diversity is expected for generic queries)
"""

import json
from datetime import datetime
from collections import Counter

INPUT_FILE = 'data/processed/queries_highest_quality_20251104_230133.json'
OUTPUT_FILE = f'data/processed/queries_final_clean_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

def is_off_topic(query_text: str, doc_text: str) -> bool:
    """
    Check if pair is off-topic (not about superconductivity).

    Off-topic if:
    - Contains 'nintendo', 'joy con', 'data science', etc.
    - Contains 'magnet' but NOT 'superconductor'
    """
    query_lower = query_text.lower()
    doc_lower = doc_text[:300].lower() if doc_text else ''

    # Clear off-topic keywords
    clear_off_topic = [
        'nintendo', 'joy con', 'switch console',
        'data science', 'type i error', 'type ii error',
        'gradient symbolic'
    ]

    for keyword in clear_off_topic:
        if keyword in query_lower or keyword in doc_lower:
            return True

    # Magnet-related but NOT superconductor
    has_magnet = 'magnet' in query_lower or 'magnet' in doc_lower
    has_superconductor = ('supercond' in query_lower or 'supercond' in doc_lower or
                          'meissner' in query_lower or 'meissner' in doc_lower)

    if has_magnet and not has_superconductor:
        # Exception: magnetic order/spin dynamics are relevant to superconductors
        magnetic_superconductor_terms = [
            'magnetic order', 'antiferromagnetic', 'spin dynamics',
            'magnetic phase', 'magnetism', 'magnetic properties'
        ]
        if any(term in query_lower or term in doc_lower for term in magnetic_superconductor_terms):
            return False  # Keep it
        return True  # Off-topic magnet content

    return False

def main():
    print("="*70)
    print("🧹 Final Dataset Cleanup")
    print("="*70)

    # Load data
    print("\n📂 Loading data...")
    with open(INPUT_FILE, 'r') as f:
        queries = json.load(f)

    print(f"   ✅ Loaded {len(queries):,} pairs")

    original_positive = sum(1 for q in queries if q['label'] == 1)
    original_negative = sum(1 for q in queries if q['label'] == 0)

    # 1. Remove duplicates
    print("\n1️⃣ Removing duplicate pairs...")
    seen = set()
    deduplicated = []
    duplicates_removed = 0

    for q in queries:
        pair_id = (q['query_text'], q['doc_id'], q['label'])
        if pair_id not in seen:
            seen.add(pair_id)
            deduplicated.append(q)
        else:
            duplicates_removed += 1

    print(f"   ❌ Removed {duplicates_removed:,} duplicate pairs")
    print(f"   ✅ Kept {len(deduplicated):,} unique pairs")

    # 2. Remove off-topic content
    print("\n2️⃣ Removing off-topic content...")
    cleaned = []
    off_topic_removed = 0
    off_topic_examples = []

    for q in deduplicated:
        query_text = q['query_text']
        doc_text = q.get('doc_text', '')

        if is_off_topic(query_text, doc_text):
            off_topic_removed += 1
            if len(off_topic_examples) < 10:
                off_topic_examples.append((query_text, q['doc_id']))
        else:
            cleaned.append(q)

    print(f"   ❌ Removed {off_topic_removed:,} off-topic pairs")
    print(f"   ✅ Kept {len(cleaned):,} on-topic pairs")

    if off_topic_examples:
        print(f"\n   Sample removed off-topic pairs:")
        for query, doc_id in off_topic_examples[:5]:
            print(f"      - \"{query[:50]}\" → {doc_id}")

    # Save
    print(f"\n💾 Saving cleaned dataset to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    # Final stats
    final_positive = sum(1 for q in cleaned if q['label'] == 1)
    final_negative = sum(1 for q in cleaned if q['label'] == 0)

    sep = "="*70
    print(f"\n{sep}")
    print("✅ FINAL CLEANUP COMPLETE!")
    print(sep)
    print(f"📊 Before Cleanup:")
    print(f"   Total: {len(queries):,}")
    print(f"   Positive: {original_positive:,}")
    print(f"   Negative: {original_negative:,}")
    print(f"\n📊 After Cleanup:")
    print(f"   Total: {len(cleaned):,}")
    print(f"   Positive: {final_positive:,}")
    print(f"   Negative: {final_negative:,}")
    print(f"\n📉 Removed:")
    print(f"   Duplicates: {duplicates_removed:,}")
    print(f"   Off-topic: {off_topic_removed:,}")
    print(f"   Total removed: {len(queries) - len(cleaned):,}")
    print(f"\n✨ Dataset is now CLEAN and ready for training!")
    print(f"{sep}\n")

if __name__ == "__main__":
    main()
