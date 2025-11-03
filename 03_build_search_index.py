"""
Build FAISS search index from merged documents
===============================================

This script:
1. Loads the merged documents
2. Loads the trained sentence transformer model
3. Generates embeddings for all documents
4. Builds a FAISS index for fast similarity search
5. Saves the index and document mappings
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

print("\n" + "="*80)
print("🔍 BUILDING SEMANTIC SEARCH INDEX")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    # Paths
    MERGED_DOCS_PATH = "data/processed/merged_all_20251103_124240.json"
    MODEL_PATH = "models/superconductor-search-v1"

    # Output
    INDEX_DIR = "data/search_index"
    FAISS_INDEX_FILE = "faiss_index.bin"
    DOCUMENTS_FILE = "documents.json"
    METADATA_FILE = "index_metadata.json"

    # Processing
    BATCH_SIZE = 32  # For embedding generation

config = Config()

# Create output directory
Path(config.INDEX_DIR).mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n📂 Loading documents...")
with open(config.MERGED_DOCS_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

documents = data['documents']
metadata = data.get('metadata', {})

print(f"✓ Loaded {len(documents)} documents")
print(f"  Total words: {metadata.get('total_words', 'N/A'):,}")
print(f"  Sources: {', '.join(metadata.get('source_breakdown', {}).keys())}")

# ============================================================================
# LOAD MODEL
# ============================================================================

print(f"\n🤖 Loading model from {config.MODEL_PATH}...")
model = SentenceTransformer(config.MODEL_PATH)
embedding_dim = model.get_sentence_embedding_dimension()

print(f"✓ Model loaded")
print(f"  Embedding dimension: {embedding_dim}")

# ============================================================================
# PREPARE DOCUMENTS FOR INDEXING
# ============================================================================

print("\n📝 Preparing documents for indexing...")

# Extract text and prepare metadata
doc_texts = []
doc_metadata = []

for i, doc in enumerate(documents):
    # Get the main text content
    content = doc.get('content', '')
    title = doc.get('title', '')
    summary = doc.get('summary', '')

    # Combine title + summary + content for better search
    if summary:
        text = f"{title}. {summary}. {content}"
    else:
        text = f"{title}. {content}"

    doc_texts.append(text)

    # Store metadata for later retrieval
    doc_metadata.append({
        'id': doc.get('id'),
        'title': title,
        'source': doc.get('source'),
        'type': doc.get('type'),
        'url': doc.get('url'),
        'difficulty_level': doc.get('difficulty_level'),
        'word_count': doc.get('word_count'),
        'focus_area': doc.get('focus_area')
    })

print(f"✓ Prepared {len(doc_texts)} documents")

# ============================================================================
# GENERATE EMBEDDINGS
# ============================================================================

print("\n🧠 Generating embeddings...")
print(f"  Processing in batches of {config.BATCH_SIZE}")

embeddings = []
for i in tqdm(range(0, len(doc_texts), config.BATCH_SIZE), desc="Encoding"):
    batch = doc_texts[i:i + config.BATCH_SIZE]
    batch_embeddings = model.encode(
        batch,
        show_progress_bar=False,
        convert_to_numpy=True
    )
    embeddings.append(batch_embeddings)

# Concatenate all embeddings
embeddings = np.vstack(embeddings).astype('float32')

print(f"\n✓ Generated embeddings")
print(f"  Shape: {embeddings.shape}")
print(f"  Size: {embeddings.nbytes / (1024*1024):.2f} MB")

# ============================================================================
# BUILD FAISS INDEX
# ============================================================================

print("\n🗂️  Building FAISS index...")

# Normalize embeddings for cosine similarity
faiss.normalize_L2(embeddings)

# Create index (IndexFlatIP for inner product = cosine similarity with normalized vectors)
index = faiss.IndexFlatIP(embedding_dim)

# Add embeddings to index
index.add(embeddings)

print(f"✓ FAISS index built")
print(f"  Total vectors: {index.ntotal}")
print(f"  Dimension: {embedding_dim}")

# ============================================================================
# SAVE INDEX AND METADATA
# ============================================================================

print("\n💾 Saving index and metadata...")

# Save FAISS index
index_path = Path(config.INDEX_DIR) / config.FAISS_INDEX_FILE
faiss.write_index(index, str(index_path))
print(f"  ✓ FAISS index: {index_path}")

# Save document metadata
docs_path = Path(config.INDEX_DIR) / config.DOCUMENTS_FILE
with open(docs_path, 'w', encoding='utf-8') as f:
    json.dump(doc_metadata, f, indent=2, ensure_ascii=False)
print(f"  ✓ Documents: {docs_path}")

# Save index metadata
index_metadata = {
    'created_at': datetime.now().isoformat(),
    'model_path': config.MODEL_PATH,
    'merged_docs_path': config.MERGED_DOCS_PATH,
    'num_documents': len(documents),
    'embedding_dim': embedding_dim,
    'index_type': 'IndexFlatIP',
    'source_breakdown': metadata.get('source_breakdown', {}),
    'difficulty_breakdown': metadata.get('difficulty_breakdown', {}),
    'type_breakdown': metadata.get('type_breakdown', {})
}

metadata_path = Path(config.INDEX_DIR) / config.METADATA_FILE
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(index_metadata, f, indent=2)
print(f"  ✓ Metadata: {metadata_path}")

# ============================================================================
# TEST SEARCH
# ============================================================================

print("\n🧪 Testing search functionality...")

test_queries = [
    "What is a superconductor?",
    "Explain the Meissner effect",
    "BCS theory of superconductivity"
]

for query in test_queries:
    print(f"\n  🔍 Query: '{query}'")

    # Encode query
    query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(query_embedding)

    # Search
    k = 3  # Top 3 results
    scores, indices = index.search(query_embedding, k)

    # Display results
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
        doc = doc_metadata[idx]
        print(f"    {rank}. [{score:.3f}] {doc['source']}: {doc['title'][:60]}...")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("✅ SEARCH INDEX BUILT SUCCESSFULLY!")
print("="*80)

print(f"""
Index Statistics:
  📊 Total documents: {len(documents):,}
  📊 Total words: {metadata.get('total_words', 0):,}
  📊 Embedding dimension: {embedding_dim}
  📊 Index size: {index_path.stat().st_size / (1024*1024):.2f} MB

Sources:
{chr(10).join(f'  • {source}: {count}' for source, count in metadata.get('source_breakdown', {}).items())}

Difficulty Levels:
{chr(10).join(f'  • Level {level}: {count}' for level, count in sorted(metadata.get('difficulty_breakdown', {}).items()))}

Output Files:
  • FAISS index: {index_path}
  • Documents: {docs_path}
  • Metadata: {metadata_path}

🎉 Your semantic search system is ready!

To use it:
  1. Load the FAISS index: faiss.read_index('{index_path}')
  2. Load documents: json.load(open('{docs_path}'))
  3. Encode queries with: SentenceTransformer('{config.MODEL_PATH}')
  4. Search with: index.search(query_embedding, k=10)
""")
