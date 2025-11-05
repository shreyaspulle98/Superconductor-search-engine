"""
Create V7 Training Dataset
===========================

Simple strategy:
1. Take ALL of V6 data (3,726 pairs)
2. Add 560 new targeted Wikipedia pairs for problem queries
3. Result: V7 will have 4,286 total pairs

The new 560 pairs will teach the model to associate:
- "josephson junction" queries → Wikipedia articles
- "cuprate superconductors" queries → Wikipedia articles
- "meissner effect" queries → Wikipedia articles

This should fix the 3 problem queries while keeping everything else working!
"""

import json

# Load V6 training data
print("Loading V6 training data...")
with open('training/training_dataset_v6.json', 'r', encoding='utf-8') as f:
    v6_data = json.load(f)

print(f"✅ V6 data loaded: {len(v6_data)} training pairs")

# Load new targeted Wikipedia pairs
print("\nLoading targeted Wikipedia pairs...")
with open('training/targeted_wiki_pairs_v7.json', 'r', encoding='utf-8') as f:
    targeted_pairs_raw = json.load(f)

print(f"✅ Targeted pairs loaded: {len(targeted_pairs_raw)} pairs")

# Load documents to get content for positive examples
print("\nLoading documents...")
with open('training/documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

# Create a lookup dict
doc_lookup = {doc['id']: doc for doc in documents}
print(f"✅ Documents loaded: {len(documents)} documents")

# ============================================================================
# CONVERT TARGETED PAIRS TO V6 FORMAT
# ============================================================================

print("\nConverting targeted pairs to V6 format...")

converted_pairs = []

for pair in targeted_pairs_raw:
    query = pair['query']
    positive_id = pair['positive_document_id']

    # Get the document
    if positive_id in doc_lookup:
        positive_doc = doc_lookup[positive_id]
        positive_content = positive_doc['content']

        # Create pair in V6 format
        v6_pair = {
            'query': query,
            'positive': positive_content,
            'positive_id': positive_id
        }

        converted_pairs.append(v6_pair)
    else:
        print(f"WARNING: Document {positive_id} not found!")

print(f"✅ Converted {len(converted_pairs)} targeted pairs to V6 format")

# ============================================================================
# CREATE V7 DATASET
# ============================================================================

print("\n" + "="*70)
print("CREATING V7 DATASET")
print("="*70)

# Combine V6 + new targeted pairs
v7_data = v6_data + converted_pairs

print(f"\nV7 Dataset Summary:")
print(f"  V6 pairs: {len(v6_data)}")
print(f"  New targeted pairs: {len(converted_pairs)}")
print(f"  Total V7 pairs: {len(v7_data)}")

# ============================================================================
# ANALYZE SOURCE DISTRIBUTION
# ============================================================================

print("\n" + "="*70)
print("SOURCE DISTRIBUTION ANALYSIS")
print("="*70)

# Count sources in all data
from collections import Counter

v6_sources = []
for pair in v6_data:
    pos_id = pair['positive_id']
    if pos_id in doc_lookup:
        v6_sources.append(doc_lookup[pos_id]['source'])

v7_sources = []
for pair in v7_data:
    pos_id = pair['positive_id']
    if pos_id in doc_lookup:
        v7_sources.append(doc_lookup[pos_id]['source'])

v6_counts = Counter(v6_sources)
v7_counts = Counter(v7_sources)

print("\nSource Distribution Comparison:")
print(f"{'Source':<20} {'V6 Count':<12} {'V6 %':<10} {'V7 Count':<12} {'V7 %':<10} {'Change'}")
print("-" * 85)

for source in ['wikipedia', 'simple_wikipedia', 'youtube', 'arxiv', 'mit_ocw', 'scholarpedia', 'hyperphysics']:
    v6_count = v6_counts.get(source, 0)
    v6_pct = (v6_count / len(v6_sources) * 100) if v6_sources else 0

    v7_count = v7_counts.get(source, 0)
    v7_pct = (v7_count / len(v7_sources) * 100) if v7_sources else 0

    change = v7_pct - v6_pct

    if source == 'wikipedia' and change > 3:
        status = "✅ UP!"
    elif change > 1:
        status = "↑"
    elif change < -1:
        status = "↓"
    else:
        status = "→"

    print(f"{source:<20} {v6_count:<12} {v6_pct:>6.1f}%    {v7_count:<12} {v7_pct:>6.1f}%    {change:>+5.1f}% {status}")

# ============================================================================
# SAVE V7 DATASET
# ============================================================================

output_file = 'training/training_dataset_v7.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(v7_data, f, indent=2, ensure_ascii=False)

print("\n" + "="*70)
print(f"✅ SAVED V7 DATASET: {output_file}")
print("="*70)
print(f"Total pairs: {len(v7_data)}")
print(f"\nV7 is ready for training!")
print("="*70)
