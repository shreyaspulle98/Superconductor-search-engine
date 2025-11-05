"""
Create Targeted Wikipedia Training Pairs for V7
================================================

Fixes the 3 problem queries from V6:
1. "josephson junction" - returned 0% Wikipedia in V6
2. "cuprate superconductors" - returned 0% Wikipedia in V6
3. "meissner effect" - returned 60% YouTube in V6

Strategy:
- Create 50-100 query variations for EACH problem topic
- Match them with relevant Wikipedia articles
- Add heavy weighting to these pairs in training
"""

import json
import random
from pathlib import Path

# Load documents
print("Loading documents...")
with open('training/documents.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

# Find Wikipedia articles for each topic
wikipedia_docs = [doc for doc in documents if doc['source'] in ['wikipedia', 'simple_wikipedia']]

print(f"Total Wikipedia articles: {len(wikipedia_docs)}")

# ============================================================================
# TARGETED QUERY GENERATION
# ============================================================================

# Problem 1: Josephson Junction (0% Wikipedia in V6)
JOSEPHSON_QUERIES = [
    # Direct queries
    "josephson junction",
    "what is a josephson junction",
    "josephson effect",
    "explain josephson junction",
    "josephson junction definition",

    # Educational queries
    "how does a josephson junction work",
    "josephson junction tutorial",
    "josephson junction basics",
    "understanding josephson junctions",
    "josephson junction explained simply",
    "josephson junction for beginners",

    # Application queries
    "josephson junction applications",
    "josephson junction uses",
    "josephson junction in squid",
    "josephson junction devices",
    "josephson junction sensors",

    # Technical queries
    "josephson junction physics",
    "josephson junction theory",
    "josephson junction mechanism",
    "josephson junction properties",
    "josephson junction characteristics",
    "josephson junction equations",

    # Specific aspects
    "ac josephson effect",
    "dc josephson effect",
    "josephson voltage",
    "josephson current",
    "josephson oscillations",
    "josephson tunneling",

    # Materials and fabrication
    "josephson junction materials",
    "josephson junction fabrication",
    "josephson junction structure",
    "josephson junction design",

    # Variations
    "josephson junctions",
    "the josephson effect",
    "brian josephson discovery",
    "josephson effect nobel prize",
]

# Problem 2: Cuprate Superconductors (0% Wikipedia in V6)
CUPRATE_QUERIES = [
    # Direct queries
    "cuprate superconductors",
    "what are cuprate superconductors",
    "cuprate superconductivity",
    "cuprate materials",
    "copper oxide superconductors",

    # Educational queries
    "explain cuprate superconductors",
    "cuprate superconductors definition",
    "cuprate superconductors basics",
    "understanding cuprate superconductors",
    "cuprate superconductors for beginners",
    "cuprate superconductors tutorial",

    # High-Tc aspect
    "high temperature cuprate superconductors",
    "cuprate high tc materials",
    "cuprate critical temperature",
    "cuprates above 77k",
    "liquid nitrogen cuprates",

    # Specific materials
    "ybco superconductor",
    "yttrium barium copper oxide",
    "bscco superconductor",
    "bismuth strontium calcium copper oxide",
    "hgbco superconductor",
    "mercury cuprate",
    "lanthanum cuprate",

    # Properties
    "cuprate structure",
    "cuprate properties",
    "cuprate mechanism",
    "cuprate physics",
    "d-wave pairing cuprates",
    "cuprate crystal structure",
    "cuprate layered structure",

    # Applications
    "cuprate applications",
    "cuprate uses",
    "cuprate technology",

    # History
    "cuprate discovery",
    "cuprate history",
    "bednorz muller cuprates",
    "1986 cuprate discovery",

    # Variations
    "cuprate superconductor",
    "copper-oxide superconductors",
    "perovskite cuprates",
]

# Problem 3: Meissner Effect (60% YouTube in V6 - need more Wikipedia)
MEISSNER_QUERIES = [
    # Direct queries
    "meissner effect",
    "what is the meissner effect",
    "meissner effect definition",
    "explain meissner effect",
    "meissner effect explained",

    # Educational queries
    "meissner effect for beginners",
    "understanding meissner effect",
    "meissner effect tutorial",
    "meissner effect basics",
    "meissner effect simply explained",
    "how does meissner effect work",

    # Phenomena
    "meissner effect levitation",
    "magnetic expulsion meissner",
    "flux expulsion superconductors",
    "meissner state",
    "perfect diamagnetism",

    # Theory
    "meissner effect physics",
    "meissner effect theory",
    "meissner effect mechanism",
    "london penetration depth",
    "meissner effect equations",

    # History
    "meissner ochsenfeld effect",
    "meissner effect discovery",
    "meissner 1933 discovery",
    "walther meissner",

    # Related concepts
    "meissner vs lenz law",
    "meissner effect vs perfect conductor",
    "type 1 meissner effect",
    "type 2 meissner effect",
    "vortex state meissner",

    # Applications
    "meissner effect applications",
    "meissner levitation applications",
    "meissner effect demonstrations",

    # Variations
    "the meissner effect",
    "meissner-ochsenfeld effect",
    "meissner effect in superconductors",
]

print(f"Generated {len(JOSEPHSON_QUERIES)} Josephson queries")
print(f"Generated {len(CUPRATE_QUERIES)} Cuprate queries")
print(f"Generated {len(MEISSNER_QUERIES)} Meissner queries")

# ============================================================================
# MATCH QUERIES WITH WIKIPEDIA ARTICLES
# ============================================================================

def find_relevant_wiki_articles(query, topic_keywords):
    """Find Wikipedia articles relevant to a query"""
    relevant = []

    for doc in wikipedia_docs:
        content_lower = doc['content'].lower()
        title_lower = doc['title'].lower()

        # Check if any keyword is in title or content
        match_count = sum(1 for keyword in topic_keywords if keyword.lower() in content_lower or keyword.lower() in title_lower)

        if match_count > 0:
            relevant.append({
                'doc_id': doc['id'],
                'doc_title': doc['title'],
                'match_count': match_count
            })

    # Sort by match count
    relevant.sort(key=lambda x: x['match_count'], reverse=True)
    return relevant

# Find articles for each topic
print("\nFinding relevant Wikipedia articles...")

josephson_articles = find_relevant_wiki_articles("josephson", ["josephson", "junction", "squid", "tunneling"])
print(f"Found {len(josephson_articles)} articles for Josephson: {[a['doc_title'] for a in josephson_articles[:5]]}")

cuprate_articles = find_relevant_wiki_articles("cuprate", ["cuprate", "copper oxide", "ybco", "high-temperature", "perovskite"])
print(f"Found {len(cuprate_articles)} articles for Cuprate: {[a['doc_title'] for a in cuprate_articles[:5]]}")

meissner_articles = find_relevant_wiki_articles("meissner", ["meissner", "magnetic field", "expulsion", "flux", "diamagnetic"])
print(f"Found {len(meissner_articles)} articles for Meissner: {[a['doc_title'] for a in meissner_articles[:5]]}")

# ============================================================================
# CREATE TRAINING PAIRS
# ============================================================================

training_pairs = []

# Helper function to create pairs
def create_pairs(queries, articles, difficulty=2):
    """Create query-document training pairs"""
    pairs = []

    if not articles:
        print(f"WARNING: No articles found for these queries!")
        return pairs

    # Take top 3-5 most relevant articles
    top_articles = articles[:min(5, len(articles))]

    for query in queries:
        # Create pairs with all top articles
        for article in top_articles:
            pair = {
                'query': query,
                'positive_document_id': article['doc_id'],
                'difficulty': difficulty,
                'source': 'wikipedia',
                'weight': 2.0  # Double weight for these important pairs!
            }
            pairs.append(pair)

    return pairs

# Create pairs for each topic
print("\nCreating training pairs...")

josephson_pairs = create_pairs(JOSEPHSON_QUERIES, josephson_articles, difficulty=2)
print(f"Created {len(josephson_pairs)} Josephson pairs")

cuprate_pairs = create_pairs(CUPRATE_QUERIES, cuprate_articles, difficulty=2)
print(f"Created {len(cuprate_pairs)} Cuprate pairs")

meissner_pairs = create_pairs(MEISSNER_QUERIES, meissner_articles, difficulty=2)
print(f"Created {len(meissner_pairs)} Meissner pairs")

# Combine all pairs
training_pairs = josephson_pairs + cuprate_pairs + meissner_pairs

print(f"\nTotal new training pairs: {len(training_pairs)}")

# ============================================================================
# SAVE TRAINING PAIRS
# ============================================================================

output_file = 'training/targeted_wiki_pairs_v7.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(training_pairs, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved {len(training_pairs)} targeted Wikipedia pairs to {output_file}")

# Print summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Josephson junction pairs: {len(josephson_pairs)}")
print(f"Cuprate superconductor pairs: {len(cuprate_pairs)}")
print(f"Meissner effect pairs: {len(meissner_pairs)}")
print(f"\nTotal targeted pairs: {len(training_pairs)}")
print(f"All pairs have 2x weight to prioritize these problem queries")
print("="*70)
