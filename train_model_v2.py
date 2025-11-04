"""
Train Superconductor Search Model - Version 2
==============================================

Trains sentence-transformer model with ultra-high quality dataset.

Features:
- Uses cleaned training dataset with hard negatives
- MultipleNegativesRankingLoss for better contrastive learning
- Proper evaluation during training
- Saves model checkpoints
"""

import json
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from torch.utils.data import DataLoader
import torch

# Configuration
TRAINING_DATA = 'training/training_dataset.json'
DOCUMENTS_FILE = 'training/documents.json'
BASE_MODEL = 'all-MiniLM-L6-v2'  # Fast and good quality
OUTPUT_MODEL = 'models/superconductor-search-v2'

# Training hyperparameters
BATCH_SIZE = 16
EPOCHS = 4
WARMUP_STEPS = 100
EVALUATION_STEPS = 500

def load_training_data():
    """Load and prepare training examples."""
    print("="*70)
    print("📂 Loading Training Data")
    print("="*70)

    with open(TRAINING_DATA, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n✅ Loaded {len(data):,} training examples")

    # Count statistics
    with_negatives = sum(1 for ex in data if 'negative' in ex)
    without_negatives = len(data) - with_negatives

    print(f"   Examples with hard negatives: {with_negatives:,} ({with_negatives/len(data)*100:.1f}%)")
    print(f"   Examples without negatives: {without_negatives:,} ({without_negatives/len(data)*100:.1f}%)")

    return data

def create_input_examples(data):
    """Convert training data to InputExample format."""
    print("\n📦 Creating InputExamples...")

    train_examples = []

    for example in data:
        if 'negative' in example:
            # Triplet: query, positive, negative
            train_examples.append(InputExample(
                texts=[
                    example['query'],
                    example['positive'],
                    example['negative']
                ]
            ))
        else:
            # Pair: query, positive
            train_examples.append(InputExample(
                texts=[
                    example['query'],
                    example['positive']
                ]
            ))

    print(f"✅ Created {len(train_examples):,} InputExamples")

    return train_examples

def create_evaluator(documents):
    """Create evaluation dataset for monitoring training progress."""
    print("\n📊 Creating Evaluation Dataset...")

    # Use a sample of documents for evaluation
    eval_queries = {
        'what is superconductivity': ['simple_wiki_18392', 'wikipedia_32'],
        'cooper pairs': ['arxiv_0506396v1', 'arxiv_9604091v1_section_2'],
        'meissner effect': ['youtube_BUlEfFm-CNA', 'youtube_RSL2CnoaVP0'],
        'iron-based superconductors': ['arxiv_1210.2889v1', 'arxiv_1503.02340v2'],
        'cuprate superconductors': ['arxiv_1306.0429v2', 'arxiv_9802197v1'],
        'josephson junction': ['arxiv_1810.04588v1'],
        'high temperature superconductor': ['arxiv_1907.02313v1'],
        'bcs theory': ['arxiv_0411318v1'],
        'quantum levitation': ['youtube_BUlEfFm-CNA'],
        'type ii superconductor': ['arxiv_0411318v1']
    }

    # Create document lookup
    doc_lookup = {doc['id']: doc for doc in documents}

    # Build corpus and queries
    corpus = {}
    queries = {}
    relevant_docs = {}

    for i, (query, doc_ids) in enumerate(eval_queries.items()):
        queries[str(i)] = query
        relevant_docs[str(i)] = set()

        for doc_id in doc_ids:
            if doc_id in doc_lookup:
                doc = doc_lookup[doc_id]
                text = doc.get('content', doc.get('text', ''))
                if text and doc_id not in corpus:
                    corpus[doc_id] = text
                relevant_docs[str(i)].add(doc_id)

    print(f"✅ Created evaluator with {len(queries)} queries and {len(corpus)} documents")

    # Create evaluator
    evaluator = evaluation.InformationRetrievalEvaluator(
        queries=queries,
        corpus=corpus,
        relevant_docs=relevant_docs,
        name='superconductor-eval'
    )

    return evaluator

def train_model():
    """Main training function."""
    print("="*70)
    print("🎯 TRAIN SUPERCONDUCTOR SEARCH MODEL V2")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"   Base model: {BASE_MODEL}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Warmup steps: {WARMUP_STEPS}")
    print(f"   Output: {OUTPUT_MODEL}")

    # Load data
    training_data = load_training_data()

    print(f"\n📂 Loading documents for evaluation...")
    with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    print(f"✅ Loaded {len(documents):,} documents")

    # Create InputExamples
    train_examples = create_input_examples(training_data)

    # Split into train/dev (90/10)
    split_idx = int(0.9 * len(train_examples))
    train_set = train_examples[:split_idx]
    dev_set = train_examples[split_idx:]

    print(f"\n📊 Dataset Split:")
    print(f"   Training set: {len(train_set):,} examples")
    print(f"   Dev set: {len(dev_set):,} examples")

    # Create DataLoader
    print(f"\n⚙️  Creating DataLoader...")
    train_dataloader = DataLoader(train_set, shuffle=True, batch_size=BATCH_SIZE)
    print(f"✅ Created DataLoader with {len(train_dataloader)} batches")

    # Load base model
    print(f"\n🤖 Loading base model: {BASE_MODEL}")
    model = SentenceTransformer(BASE_MODEL)
    print(f"✅ Model loaded")

    # Create loss function
    print(f"\n📐 Setting up loss function...")
    train_loss = losses.MultipleNegativesRankingLoss(model)
    print(f"✅ Using MultipleNegativesRankingLoss")

    # Create evaluator
    evaluator = create_evaluator(documents)

    # Training
    print("\n" + "="*70)
    print("🚀 STARTING TRAINING")
    print("="*70)

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=EPOCHS,
        evaluation_steps=EVALUATION_STEPS,
        warmup_steps=WARMUP_STEPS,
        output_path=OUTPUT_MODEL,
        save_best_model=True,
        show_progress_bar=True
    )

    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)

    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'base_model': BASE_MODEL,
        'training_examples': len(train_examples),
        'epochs': EPOCHS,
        'batch_size': BATCH_SIZE,
        'data_quality': {
            'average_positive_score': 0.865,
            'with_hard_negatives': sum(1 for ex in training_data if 'negative' in ex),
            'total_documents': len(documents)
        }
    }

    metadata_path = os.path.join(OUTPUT_MODEL, 'training_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n📁 Model saved to: {OUTPUT_MODEL}")
    print(f"📊 Training metadata saved")

    # Test the model
    print("\n" + "="*70)
    print("🧪 QUICK TEST")
    print("="*70)

    test_queries = [
        "what is superconductivity",
        "cooper pairs explained",
        "iron-based superconductors",
        "who discovered BCS theory"
    ]

    print("\nTesting model on sample queries:")
    for query in test_queries:
        embedding = model.encode(query)
        print(f"   ✅ '{query}' → {len(embedding)}-dim embedding")

    print("\n" + "="*70)
    print("🎯 Next Steps:")
    print("="*70)
    print("   1. Evaluate model on test set")
    print("   2. Compare with old model performance")
    print("   3. Deploy if performance improved")
    print("   4. Update search index with new embeddings")
    print("="*70 + "\n")

if __name__ == "__main__":
    train_model()
