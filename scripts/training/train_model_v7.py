"""
Train Model V7
==============

Improvements over V6:
- Added 560 targeted Wikipedia pairs for problem queries:
  * Josephson junction (180 pairs)
  * Cuprate superconductors (200 pairs)
  * Meissner effect (180 pairs)

- V7 Distribution:
  * Wikipedia: 46.2% (up from 38.1% in V6) ✅
  * YouTube: 23.1% (down from 26.6% in V6) ✅
  * arXiv: 26.4% (down from 30.4% in V6)

Expected improvements:
1. "josephson junction" should return Wikipedia (was 0% in V6)
2. "cuprate superconductors" should return Wikipedia (was 0% in V6)
3. "meissner effect" should prioritize Wikipedia over YouTube (was 60% YouTube in V6)
"""

import json
import torch
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

TRAINING_DATA = 'training/training_dataset_v7.json'
BASE_MODEL = 'all-MiniLM-L6-v2'
OUTPUT_MODEL = 'models/superconductor-search-v7'
BATCH_SIZE = 16
EPOCHS = 4
WARMUP_STEPS = 100
EVALUATION_STEPS = 500

# ============================================================================
# LOAD TRAINING DATA
# ============================================================================

print("="*70)
print("TRAINING MODEL V7")
print("="*70)

print(f"\nLoading training data from {TRAINING_DATA}...")
with open(TRAINING_DATA, 'r', encoding='utf-8') as f:
    training_data = json.load(f)

print(f"✅ Loaded {len(training_data)} training examples")

# ============================================================================
# PREPARE TRAINING EXAMPLES
# ============================================================================

print("\nPreparing training examples...")

train_examples = []

for item in training_data:
    query = item['query']
    positive = item['positive']

    # Create training example
    example = InputExample(texts=[query, positive])
    train_examples.append(example)

    # If there's a negative example, add it as well
    if 'negative' in item and item['negative']:
        negative = item['negative']
        # For hard negatives, we create additional pairs
        neg_example = InputExample(texts=[query, positive], label=1.0)
        train_examples.append(neg_example)

print(f"✅ Created {len(train_examples)} training examples")

# Create DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=BATCH_SIZE)
print(f"✅ Created DataLoader with batch size {BATCH_SIZE}")

# ============================================================================
# LOAD BASE MODEL
# ============================================================================

print(f"\nLoading base model: {BASE_MODEL}...")
model = SentenceTransformer(BASE_MODEL)
print("✅ Model loaded successfully")

# ============================================================================
# CONFIGURE TRAINING
# ============================================================================

print("\nConfiguring training...")

# Use MultipleNegativesRankingLoss
train_loss = losses.MultipleNegativesRankingLoss(model=model)

# Calculate total steps
num_train_steps = len(train_dataloader) * EPOCHS
print(f"Total training steps: {num_train_steps}")
print(f"Warmup steps: {WARMUP_STEPS}")
print(f"Evaluation steps: {EVALUATION_STEPS}")

# ============================================================================
# TRAIN MODEL
# ============================================================================

print("\n" + "="*70)
print("STARTING TRAINING")
print("="*70)

start_time = datetime.now()

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=EPOCHS,
    warmup_steps=WARMUP_STEPS,
    output_path=OUTPUT_MODEL,
    show_progress_bar=True,
    save_best_model=True
)

end_time = datetime.now()
training_time = end_time - start_time

print("\n" + "="*70)
print("TRAINING COMPLETE")
print("="*70)
print(f"Training time: {training_time}")
print(f"Model saved to: {OUTPUT_MODEL}")

# ============================================================================
# SAVE METADATA
# ============================================================================

print("\nSaving training metadata...")

metadata = {
    "version": "v7",
    "training_date": datetime.now().isoformat(),
    "base_model": BASE_MODEL,
    "training_examples": len(training_data),
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
    "training_time": str(training_time),
    "improvements_over_v6": {
        "targeted_pairs_added": 560,
        "josephson_junction_pairs": 180,
        "cuprate_pairs": 200,
        "meissner_effect_pairs": 180,
        "wikipedia_percentage": "46.2% (up from 38.1%)",
        "youtube_percentage": "23.1% (down from 26.6%)",
        "fixes": [
            "josephson junction queries should now return Wikipedia",
            "cuprate superconductors queries should now return Wikipedia",
            "meissner effect queries should prioritize Wikipedia over YouTube"
        ]
    },
    "data_quality": {
        "total_pairs": len(training_data),
        "wikipedia_pairs": 1978,
        "youtube_pairs": 990,
        "arxiv_pairs": 1131,
        "simple_wikipedia_pairs": 183
    }
}

metadata_file = f"{OUTPUT_MODEL}/training_metadata.json"
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"✅ Metadata saved to: {metadata_file}")

print("\n" + "="*70)
print("✅ MODEL V7 TRAINING COMPLETE!")
print("="*70)
print(f"\nNext steps:")
print(f"1. Test Model V7: python scripts/testing/test_model_v7.py")
print(f"2. Compare with V6 on the 3 problem queries")
print(f"3. If results are good, deploy to Hugging Face")
print("="*70)
