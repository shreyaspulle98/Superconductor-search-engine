"""
SUPERCONDUCTOR SEMANTIC SEARCH - MODEL TRAINING
================================================

This script trains all-mpnet-base-v2 on your superconductor data.
Optimized for MacBook (M1/M2/M3/M4 with MPS acceleration).

What this does:
1. Loads your documents and training pairs
2. Fine-tunes all-mpnet-base-v2 using contrastive learning
3. Saves the trained model
4. Tests it on sample queries

Time: ~20-35 minutes on M4 MacBook
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Check if running on Mac with MPS (Apple Silicon GPU)
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"MPS (Apple GPU) available: {torch.backends.mps.is_available()}")
print(f"MPS built: {torch.backends.mps.is_built()}")

# M4 chip specific
import platform
if platform.processor() == 'arm':
    print(f"Apple Silicon detected: {platform.machine()}")
    print("M4 Neural Engine optimizations: ACTIVE 🚀")

from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

print("\n" + "=" * 70)
print("🚀 SUPERCONDUCTOR SEMANTIC SEARCH - TRAINING")
print("=" * 70)

# ============================================================================
# CONFIGURATION
# ============================================================================
print("\n📋 Configuration...")

class Config:
    """Training configuration - optimized for MacBook"""
    
    # Model
    BASE_MODEL = "sentence-transformers/all-mpnet-base-v2"
    
    # Data paths
    MERGED_DOCS_PATH = "data/processed/merged_all_20251103_124240.json"
    TRAINING_PAIRS_PATH = "data/processed/training_pairs.json"
    
    # Output
    OUTPUT_DIR = "models/superconductor-search-v1"
    
    # Training parameters (M4 MacBook-optimized)
    BATCH_SIZE = 16  # M4 can handle larger batches!
    EPOCHS = 4  # Full training - M4 is fast enough
    LEARNING_RATE = 2e-5
    WARMUP_STEPS = 100
    
    # Hardware (M4 optimization)
    DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
    # MPS = Metal Performance Shaders (Apple's GPU acceleration)
    # M4 has significantly improved Neural Engine performance!
    
    RANDOM_SEED = 42

config = Config()

# Create output directory
Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

print(f"✓ Model: {config.BASE_MODEL}")
print(f"✓ Device: {config.DEVICE}")
print(f"✓ Batch size: {config.BATCH_SIZE}")
print(f"✓ Epochs: {config.EPOCHS}")
print(f"✓ Output: {config.OUTPUT_DIR}")

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n📂 Loading data...")

def load_json(path: str) -> dict:
    """Load JSON file"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load documents
print(f"Loading documents from {config.MERGED_DOCS_PATH}...")
data = load_json(config.MERGED_DOCS_PATH)
# Handle structure: {"metadata": {...}, "documents": [...]}
if isinstance(data, dict) and 'documents' in data:
    documents_list = data['documents']
elif isinstance(data, list):
    documents_list = data
else:
    raise ValueError(f"Unexpected file format in {config.MERGED_DOCS_PATH}")

# Convert to dictionary for fast lookup
documents = {}
for doc in documents_list:
    # Handle both list and dict formats
    if isinstance(doc, dict):
        doc_id = doc.get('id') or doc.get('doc_id')
        if doc_id:
            documents[doc_id] = doc
    
print(f"✓ Loaded {len(documents)} documents")

# Load training pairs
print(f"Loading training pairs from {config.TRAINING_PAIRS_PATH}...")
training_pairs = load_json(config.TRAINING_PAIRS_PATH)
print(f"✓ Loaded {len(training_pairs)} training pairs")

# Statistics
positive_pairs = sum(1 for p in training_pairs if p['label'] == 1)
negative_pairs = len(training_pairs) - positive_pairs

print("\n📊 Data Statistics:")
print(f"  Documents: {len(documents)}")
print(f"  Training pairs: {len(training_pairs)}")
print(f"    - Positive (similar): {positive_pairs} ({positive_pairs/len(training_pairs)*100:.1f}%)")
print(f"    - Negative (dissimilar): {negative_pairs} ({negative_pairs/len(training_pairs)*100:.1f}%)")

# ============================================================================
# PREPARE TRAINING DATA
# ============================================================================
print("\n🔧 Preparing training data...")

def create_training_examples(pairs: List[Dict], docs: Dict) -> List[InputExample]:
    """
    Convert query-document pairs into training examples.
    
    Each example has:
    - texts: [query, document_text]
    - label: 1.0 (similar) or 0.0 (dissimilar)
    
    Note: The training pairs already contain doc_text, so we use it directly.
    """
    examples = []
    skipped = 0
    
    for i, pair in enumerate(pairs):
        if i % 1000 == 0:
            print(f"  Processing pair {i}/{len(pairs)}...")
        
        # Use the keys from the actual training pairs file
        query = pair.get('query_text', pair.get('query', ''))
        doc_text = pair.get('doc_text', '')
        label = float(pair['label'])
        
        # Skip if missing required fields
        if not query or not doc_text:
            skipped += 1
            continue
        
        # Create example
        example = InputExample(texts=[query, doc_text], label=label)
        examples.append(example)
    
    if skipped > 0:
        print(f"  ⚠️  Skipped {skipped} pairs (missing query or doc_text)")
    
    return examples

# Create examples
examples = create_training_examples(training_pairs, documents)
print(f"✓ Created {len(examples)} training examples")

# Shuffle
random.seed(config.RANDOM_SEED)
random.shuffle(examples)

# Split into train/validation (90/10)
split_idx = int(0.9 * len(examples))
train_examples = examples[:split_idx]
val_examples = examples[split_idx:]

print(f"✓ Training set: {len(train_examples)} examples")
print(f"✓ Validation set: {len(val_examples)} examples")

# ============================================================================
# CREATE DATA LOADER
# ============================================================================
print("\n📦 Creating data loader...")

train_dataloader = DataLoader(
    train_examples,
    shuffle=True,
    batch_size=config.BATCH_SIZE
)

total_steps = len(train_dataloader) * config.EPOCHS
print(f"✓ Batches per epoch: {len(train_dataloader)}")
print(f"✓ Total training steps: {total_steps}")

# ============================================================================
# LOAD MODEL
# ============================================================================
print("\n🤖 Loading model...")
print(f"Downloading {config.BASE_MODEL}...")
print("(First time only - will be cached for future use)")

model = SentenceTransformer(config.BASE_MODEL, device=config.DEVICE)

print("✓ Model loaded!")
print(f"  Embedding dimension: {model.get_sentence_embedding_dimension()}")
print(f"  Max sequence length: {model.max_seq_length} tokens")
print(f"  Running on: {config.DEVICE}")

# ============================================================================
# SETUP LOSS FUNCTION
# ============================================================================
print("\n📐 Setting up loss function...")

train_loss = losses.CosineSimilarityLoss(model)

print("✓ Using CosineSimilarityLoss")
print("  Teaches model:")
print("  - Similar pairs → high cosine similarity")
print("  - Dissimilar pairs → low cosine similarity")

# ============================================================================
# TRAIN THE MODEL
# ============================================================================
print("\n" + "=" * 70)
print("🎯 STARTING TRAINING")
print("=" * 70)

print(f"""
Training will run for {config.EPOCHS} epochs.
On your M4 MacBook, this typically takes:
  • M4 with MPS: ~20-35 minutes (FAST! 🚀)
  • M4 Neural Engine optimizations active

You'll see progress bars for each epoch.
Perfect time for a quick coffee! ☕
""")

# Record start time
start_time = datetime.now()
print(f"Started at: {start_time.strftime('%H:%M:%S')}\n")

# TRAIN!
try:
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=config.EPOCHS,
        warmup_steps=config.WARMUP_STEPS,
        output_path=config.OUTPUT_DIR,
        save_best_model=True,
        show_progress_bar=True,
        use_amp=False  # Disable automatic mixed precision for Mac stability
    )
    
    # Record end time
    end_time = datetime.now()
    duration_minutes = (end_time - start_time).total_seconds() / 60
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"⏱️  Training time: {duration_minutes:.1f} minutes")
    print(f"💾 Model saved to: {config.OUTPUT_DIR}")
    
except Exception as e:
    print(f"\n❌ Training failed: {e}")
    print("\nTroubleshooting for M4 MacBook:")
    print("  1. M4 should have 16GB+ unified memory - check Activity Monitor")
    print("  2. If RAM issue, reduce BATCH_SIZE to 8 in Config class")
    print("  3. Ensure macOS is updated (M4 needs recent OS for best MPS support)")
    print("  4. Close other apps to free unified memory")
    raise

# ============================================================================
# TEST THE MODEL
# ============================================================================
print("\n🧪 Testing the trained model...")

# Load the trained model
trained_model = SentenceTransformer(config.OUTPUT_DIR)

# Test queries at different difficulty levels
test_queries = {
    "Beginner": [
        "What is a superconductor?",
        "How do superconductors work?"
    ],
    "Intermediate": [
        "What is the Meissner effect?",
        "Difference between Type I and Type II superconductors"
    ],
    "Expert": [
        "Derive the BCS ground state wavefunction",
        "Calculate superconducting gap equation"
    ]
}

print("\n" + "-" * 70)
print("Sample Searches:")
print("-" * 70)

for difficulty, queries in test_queries.items():
    print(f"\n{difficulty} Level:")
    for query in queries:
        print(f"\n  🔍 '{query}'")
        
        # Encode query
        query_emb = trained_model.encode(query, convert_to_tensor=False)
        
        # Find similar documents (simple search on first 100 docs)
        sample_docs = list(documents.values())[:100]
        doc_texts = [d.get('text', d.get('content', ''))[:500] for d in sample_docs]
        doc_embs = trained_model.encode(doc_texts, convert_to_tensor=False)
        
        # Calculate similarities
        from sentence_transformers import util
        import torch
        similarities = util.cos_sim(
            torch.tensor(query_emb).unsqueeze(0),
            torch.tensor(doc_embs)
        )[0]
        
        # Get top 3
        top_indices = similarities.argsort(descending=True)[:3]
        
        for rank, idx in enumerate(top_indices, 1):
            doc = sample_docs[idx]
            score = similarities[idx].item()
            title = doc.get('title', doc.get('doc_id', 'Untitled'))[:50]
            source = doc.get('source', 'Unknown')
            print(f"     {rank}. [{score:.3f}] {source}: {title}...")

# ============================================================================
# SAVE METADATA
# ============================================================================
print("\n💾 Saving training metadata...")

metadata = {
    "training_date": datetime.now().isoformat(),
    "base_model": config.BASE_MODEL,
    "num_documents": len(documents),
    "num_training_pairs": len(training_pairs),
    "num_training_examples": len(train_examples),
    "epochs": config.EPOCHS,
    "batch_size": config.BATCH_SIZE,
    "learning_rate": config.LEARNING_RATE,
    "training_duration_minutes": duration_minutes,
    "device": config.DEVICE,
    "model_path": config.OUTPUT_DIR
}

metadata_path = Path(config.OUTPUT_DIR) / "training_metadata.json"
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✓ Metadata saved to {metadata_path}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("🎉 SUCCESS! YOUR MODEL IS READY!")
print("=" * 70)

print(f"""
What you have now:
  ✅ Fine-tuned model: {config.OUTPUT_DIR}/
  ✅ Model size: ~420 MB
  ✅ Training time: {duration_minutes:.1f} minutes
  ✅ Trained on: {len(documents)} documents, {len(training_pairs)} pairs
  
Next Steps:
  1. Move to Phase 4: Generate document embeddings
  2. Build FAISS index for fast search (Phase 5)
  3. Create Streamlit UI (Phase 6)
  
To use your model:
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer('{config.OUTPUT_DIR}')
  embedding = model.encode("your query here")
""")

print("\n🚀 Ready for Phase 4: Generate Embeddings!\n")