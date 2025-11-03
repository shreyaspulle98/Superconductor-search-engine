"""
Merge all collected datasets into unified format
Wikipedia + arXiv + MIT OCW → Single JSON
"""

import json
from datetime import datetime

def load_json(filepath):
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def merge_all_datasets():
    """Merge all datasets into unified format."""
    
    print("\n" + "="*80)
    print("🔄 MERGING ALL DATASETS")
    print("="*80)
    
    all_documents = []
    
    # === 1. Load Superconductor Pure (Wikipedia + arXiv) ===
    print("\n📂 Loading superconductor_pure_300.json...")
    pure_data = load_json('data/raw/superconductor_pure_300.json')

    if pure_data:
        # Handle both list and dict formats
        if isinstance(pure_data, list):
            docs = pure_data
            print(f"   Found: {len(docs)} documents (list format)")
            all_documents.extend(docs)
        elif isinstance(pure_data, dict) and 'documents' in pure_data:
            docs = pure_data['documents']
            print(f"   Found: {len(docs)} documents (dict format)")
            all_documents.extend(docs)
        else:
            print("   ⚠️  Unexpected format - not a list or dict with 'documents' field")
    else:
        print("   ⚠️  Failed to load file")
    
    # === 2. Load MIT OCW ===
    print("\n📂 Loading mit_ocw_20251030_162724.json...")
    mit_data = load_json('data/raw/mit_ocw_20251030_162724.json')

    if mit_data and 'documents' in mit_data:
        docs = mit_data['documents']
        print(f"   Found: {len(docs)} documents")
        all_documents.extend(docs)
    else:
        print("   ⚠️  No documents field found")

    # === 3. Load Simple Wikipedia ===
    print("\n📂 Loading simple_wikipedia_20251031_172056.json...")
    simple_wiki_data = load_json('data/raw/simple_wikipedia_20251031_172056.json')

    if simple_wiki_data and 'articles' in simple_wiki_data:
        articles = simple_wiki_data['articles']
        print(f"   Found: {len(articles)} articles")

        # Convert Simple Wikipedia articles to standard document format
        for article in articles:
            doc = {
                'id': article['id'],
                'source': 'simple_wikipedia',
                'type': 'encyclopedia',
                'category': 'fundamentals',
                'focus_area': 'main',
                'title': article['title'],
                'content': article['content'],
                'url': article['url'],
                'word_count': article['word_count'],
                'difficulty_level': 1,  # All Simple Wikipedia is beginner-friendly
                'collected_at': simple_wiki_data.get('metadata', {}).get('scrape_date'),
                'summary': None,
                'tags': article.get('categories', []),
                'source_metadata': {
                    'categories': article.get('categories', [])
                }
            }
            all_documents.append(doc)

        print(f"   ✅ Converted and added {len(articles)} Simple Wikipedia articles")
    else:
        print("   ⚠️  No articles field found")

    # === 4. Load NEW Wikipedia Articles ===
    print("\n📂 Loading wikipedia_articles.json...")
    wiki_data = load_json('data/raw/wikipedia_articles.json')

    if wiki_data:
        if isinstance(wiki_data, list):
            docs = wiki_data
        elif isinstance(wiki_data, dict) and 'documents' in wiki_data:
            docs = wiki_data['documents']
        else:
            docs = []

        if docs:
            print(f"   Found: {len(docs)} Wikipedia articles")
            all_documents.extend(docs)
        else:
            print("   ⚠️  No articles found")
    else:
        print("   ⚠️  File not found or empty")

    # === 5. Load arXiv Full Papers ===
    print("\n📂 Loading arxiv_full_papers.json...")
    arxiv_full_data = load_json('data/raw/arxiv_full_papers.json')

    if arxiv_full_data:
        if isinstance(arxiv_full_data, list):
            docs = arxiv_full_data
        elif isinstance(arxiv_full_data, dict) and 'documents' in arxiv_full_data:
            docs = arxiv_full_data['documents']
        else:
            docs = []

        if docs:
            print(f"   Found: {len(docs)} arXiv full paper sections")
            all_documents.extend(docs)
        else:
            print("   ⚠️  No documents found")
    else:
        print("   ⚠️  File not found or empty")

    # === 6. Load Scholarpedia Articles ===
    print("\n📂 Loading scholarpedia_articles.json...")
    scholarpedia_data = load_json('data/raw/scholarpedia_articles.json')

    if scholarpedia_data:
        if isinstance(scholarpedia_data, list):
            docs = scholarpedia_data
        else:
            docs = []

        if docs:
            print(f"   Found: {len(docs)} Scholarpedia articles")
            all_documents.extend(docs)
        else:
            print("   ⚠️  No articles found")
    else:
        print("   ⚠️  File not found or empty")

    # === 7. Load HyperPhysics Articles ===
    print("\n📂 Loading hyperphysics_articles.json...")
    hyperphysics_data = load_json('data/raw/hyperphysics_articles.json')

    if hyperphysics_data:
        if isinstance(hyperphysics_data, list):
            docs = hyperphysics_data
        else:
            docs = []

        if docs:
            print(f"   Found: {len(docs)} HyperPhysics articles")
            all_documents.extend(docs)
        else:
            print("   ⚠️  No articles found")
    else:
        print("   ⚠️  File not found or empty")

    # === 8. Calculate Statistics ===
    print("\n" + "="*80)
    print("📊 CALCULATING STATISTICS")
    print("="*80)

    source_breakdown = {}
    focus_breakdown = {}
    difficulty_breakdown = {}
    type_breakdown = {}
    total_words = 0

    for doc in all_documents:
        # Source
        source = doc.get('source', 'unknown')
        source_breakdown[source] = source_breakdown.get(source, 0) + 1

        # Focus type (handle both old and new formats)
        focus = doc.get('focus_area', doc.get('categorization', {}).get('focus_type', 'main'))
        if focus:
            focus_breakdown[focus] = focus_breakdown.get(focus, 0) + 1

        # Difficulty level
        difficulty = doc.get('difficulty_level')
        if difficulty:
            difficulty_breakdown[difficulty] = difficulty_breakdown.get(difficulty, 0) + 1

        # Document type
        doc_type = doc.get('type', 'unknown')
        type_breakdown[doc_type] = type_breakdown.get(doc_type, 0) + 1

        # Word count (handle both formats)
        word_count = doc.get('word_count', doc.get('quality_metrics', {}).get('word_count', 0))
        total_words += word_count
    
    # === 9. Save Merged Dataset ===
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/processed/merged_all_{timestamp}.json'
    
    output_data = {
        'metadata': {
            'merge_date': datetime.now().isoformat(),
            'total_documents': len(all_documents),
            'total_words': total_words,
            'average_words_per_doc': total_words // len(all_documents) if all_documents else 0,
            'source_breakdown': source_breakdown,
            'type_breakdown': type_breakdown,
            'focus_breakdown': focus_breakdown,
            'difficulty_breakdown': difficulty_breakdown
        },
        'documents': all_documents
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # === 5. Print Summary ===
    print(f"\n✅ Merged Dataset:")
    print(f"   Total documents: {len(all_documents):,}")
    print(f"   Total words: {total_words:,}")
    print(f"   Average words/doc: {total_words//len(all_documents) if all_documents else 0:,}")

    print(f"\n   By Source:")
    for source, count in sorted(source_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"     {source}: {count}")

    print(f"\n   By Type:")
    for doc_type, count in sorted(type_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"     {doc_type}: {count}")

    print(f"\n   By Focus:")
    for focus, count in sorted(focus_breakdown.items()):
        print(f"     {focus}: {count}")

    if difficulty_breakdown:
        print(f"\n   By Difficulty Level:")
        for difficulty in sorted(difficulty_breakdown.keys()):
            count = difficulty_breakdown[difficulty]
            level_name = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert", 5: "Cutting-edge"}.get(difficulty, f"Level {difficulty}")
            print(f"     {level_name} ({difficulty}): {count}")

    print(f"\n💾 Saved to: {output_file}")
    
    return output_file, all_documents

if __name__ == "__main__":
    output_file, docs = merge_all_datasets()
    print(f"\n✅ Ready for Word2Vec training!")
    print(f"   Use file: {output_file}")