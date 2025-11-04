"""
Build Search Index - Superconductor Search v2
==============================================

Builds FAISS vector index for semantic search using the trained model.

Features:
- Loads trained model from models/superconductor-search-v2
- Generates embeddings for all 1,762 documents
- Creates FAISS index for efficient similarity search
- Saves index and document mapping for search engine
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os
from datetime import datetime

# Configuration
MODEL_PATH = 'models/superconductor-search-v2'
DOCUMENTS_FILE = 'training/documents.json'
INDEX_OUTPUT = 'search_index'
BATCH_SIZE = 32

def load_documents() -> List[Dict]:
    """Load all documents."""
    print("=" * 70)
    print("📂 Loading Documents")
    print("=" * 70)

    with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    print(f"\n✅ Loaded {len(documents):,} documents")

    # Count by source
    sources = {}
    for doc in documents:
        source = doc.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1

    print("\n📊 Document Sources:")
    for source, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"   {source}: {count:,} ({count/len(documents)*100:.1f}%)")

    return documents

def prepare_texts(documents: List[Dict]) -> tuple:
    """Prepare document texts for embedding."""
    print("\n📝 Preparing Document Texts...")

    doc_texts = []
    doc_metadata = []

    for doc in documents:
        # Get text content
        text = doc.get('content', doc.get('text', ''))
        if not text or isinstance(text, dict):
            text = ''

        # Get title
        title = doc.get('title', '')
        if not title or isinstance(title, dict):
            title = ''

        # Combine title and text for better embeddings
        if title:
            full_text = f"{title}\n\n{text[:2000]}"  # Use title + first 2000 chars
        else:
            full_text = text[:2000]

        doc_texts.append(full_text)

        # Store metadata for retrieval
        metadata = {
            'id': doc.get('id', ''),
            'title': title,
            'source': doc.get('source', ''),
            'difficulty': doc.get('difficulty', 0),
            'url': doc.get('url', doc.get('video_id', '')),
            'text_preview': text[:200]  # First 200 chars for preview
        }
        doc_metadata.append(metadata)

    print(f"✅ Prepared {len(doc_texts):,} document texts")

    return doc_texts, doc_metadata

def generate_embeddings(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
    """Generate embeddings for all documents."""
    print("\n🧠 Generating Embeddings...")
    print(f"   Model: {MODEL_PATH}")
    print(f"   Documents: {len(texts):,}")
    print(f"   Batch size: {BATCH_SIZE}")

    # Generate embeddings in batches
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    print(f"\n✅ Generated embeddings: {embeddings.shape}")
    print(f"   Dimensions: {embeddings.shape[1]}")
    print(f"   Total vectors: {embeddings.shape[0]:,}")

    return embeddings

def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """Build FAISS index for similarity search."""
    print("\n🔍 Building FAISS Index...")

    dimension = embeddings.shape[1]

    # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
    # Normalize embeddings first
    faiss.normalize_L2(embeddings)

    # Create index
    index = faiss.IndexFlatIP(dimension)

    # Add vectors
    index.add(embeddings)

    print(f"✅ FAISS Index Built")
    print(f"   Index type: IndexFlatIP (cosine similarity)")
    print(f"   Dimensions: {dimension}")
    print(f"   Total vectors: {index.ntotal:,}")

    return index

def save_index(index: faiss.Index, metadata: List[Dict]):
    """Save index and metadata to disk."""
    print("\n💾 Saving Index and Metadata...")

    # Create output directory
    os.makedirs(INDEX_OUTPUT, exist_ok=True)

    # Save FAISS index
    index_path = os.path.join(INDEX_OUTPUT, 'faiss_index.bin')
    faiss.write_index(index, index_path)
    print(f"   ✅ FAISS index saved: {index_path}")

    # Save metadata
    metadata_path = os.path.join(INDEX_OUTPUT, 'document_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Metadata saved: {metadata_path}")

    # Save index info
    info = {
        'created_at': datetime.now().isoformat(),
        'model_path': MODEL_PATH,
        'total_documents': len(metadata),
        'embedding_dimension': index.d,
        'index_type': 'IndexFlatIP',
        'similarity_metric': 'cosine'
    }

    info_path = os.path.join(INDEX_OUTPUT, 'index_info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)
    print(f"   ✅ Index info saved: {info_path}")

    # Calculate total size
    index_size = os.path.getsize(index_path) / (1024 * 1024)
    metadata_size = os.path.getsize(metadata_path) / (1024 * 1024)
    total_size = index_size + metadata_size

    print(f"\n📊 Index Statistics:")
    print(f"   FAISS index: {index_size:.2f} MB")
    print(f"   Metadata: {metadata_size:.2f} MB")
    print(f"   Total: {total_size:.2f} MB")

def build_index():
    """Main function to build search index."""
    print("=" * 70)
    print("🎯 BUILD SEARCH INDEX - SUPERCONDUCTOR SEARCH V2")
    print("=" * 70)

    # Load documents
    documents = load_documents()

    # Prepare texts
    doc_texts, doc_metadata = prepare_texts(documents)

    # Load trained model
    print("\n🤖 Loading Trained Model...")
    print(f"   Path: {MODEL_PATH}")
    model = SentenceTransformer(MODEL_PATH)
    print(f"✅ Model loaded")

    # Generate embeddings
    embeddings = generate_embeddings(model, doc_texts)

    # Build FAISS index
    index = build_faiss_index(embeddings)

    # Save index and metadata
    save_index(index, doc_metadata)

    print("\n" + "=" * 70)
    print("✅ SEARCH INDEX BUILT SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📁 Output directory: {INDEX_OUTPUT}/")
    print(f"   - faiss_index.bin (FAISS vector index)")
    print(f"   - document_metadata.json (document metadata)")
    print(f"   - index_info.json (index information)")
    print("\n🎯 Ready for testing!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    build_index()
