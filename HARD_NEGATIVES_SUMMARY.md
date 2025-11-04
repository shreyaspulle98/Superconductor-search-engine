# Hard Negatives Implementation Summary

## Problem Identified

The contrastive learning was not working well because:
1. **Generic queries matched biographical documents** - "what is superconductivity" was returning videos about Brian Josephson
2. **No hard negatives** - The dataset only had positive pairs (label=1), so the model never learned to distinguish between similar but incorrect documents
3. **Bad positive pairings** - Biographical documents had generic queries like "superconductivity explained" attached to them

## Solution Implemented

Created `create_hard_negatives.py` which implements three types of smart hard negatives:

### 1. Generic Query → Biographical Doc (Negative)
**Rule**: Broad superconductivity questions should NOT match biographical content

**Example**:
- Query: "how superconductors work"
- ❌ NEGATIVE: Brian Josephson biographical video
- ✅ POSITIVE: Generic explanation video

**Result**: Created 33,900 hard negatives of this type

### 2. Person-Specific Query → Theory Doc (Negative)
**Rule**: Questions about specific people should NOT match generic theory

**Example**:
- Query: "who is John Bardeen"
- ❌ NEGATIVE: BCS theory paper (generic)
- ✅ POSITIVE: Bardeen biographical content

**Result**: Created 822 hard negatives of this type

### 3. Material-Specific Query → Other Material Doc (Negative)
**Rule**: Queries about specific materials should NOT match docs about different materials

**Example**:
- Query: "cuprate superconductors"
- ❌ NEGATIVE: Iron-based superconductor paper
- ✅ POSITIVE: Cuprate paper

**Result**: Created 2,774 hard negatives of this type

## Removed Bad Positive Pairings

**Removed 93 positive pairs** where:
- Generic queries were paired with biographical documents
- These would have taught the model incorrect associations

## Final Dataset Statistics

### Overall
- **Total pairs**: 58,885
- **Positive pairs**: 21,389 (36.3%)
- **Negative pairs**: 37,496 (63.7%)
- **Ratio**: ~1 positive : 1.75 negatives

### Hard Negative Breakdown
- Generic → Bio: 33,900
- Person → Theory: 822
- Material mismatch: 2,774

### Quality Improvements
1. ✅ Removed generic queries from biographical documents
2. ✅ Added semantically meaningful hard negatives
3. ✅ Balanced positive/negative ratio (36.3% positive)
4. ✅ Created challenging negatives that force fine-grained learning

## Document Classification

### Biographical Documents Identified: 11
Documents primarily about specific people that should only match person-specific queries.

### Material-Specific Documents
- Cuprate: 37 docs
- Pnictide/Iron-based: 6 docs
- Nickelate: 5 docs
- YBCO: 13 docs
- MgB2: 1 doc
- Graphene: 9 docs

## Impact on Model Training

### Before Hard Negatives
- Model only saw positive examples
- No incentive to distinguish between similar documents
- Learned to match any superconductivity query to any superconductivity document
- Result: Overfitting and poor semantic discrimination

### After Hard Negatives
- Model sees both correct (positive) and incorrect (negative) pairs
- Must learn to distinguish between:
  - Generic questions vs. biographical content
  - Person-specific questions vs. theory content
  - Material-specific questions vs. other materials
- Contrastive loss will push similar-but-wrong documents away in embedding space
- Result: Better semantic discrimination and more precise search

## Next Steps

1. ✅ **Dataset created**: `data/processed/queries_with_hard_negatives_20251104_224640.json`
2. ⏳ **Retrain model** with new dataset including hard negatives
3. ⏳ **Evaluate** against test queries like:
   - "what is superconductivity" (should NOT return Brian Josephson)
   - "who discovered BCS theory" (should return Bardeen/Cooper/Schrieffer)
   - "cuprate superconductors" (should NOT return iron-based papers)

## Files Created

- `create_hard_negatives.py` - Script to generate hard negatives
- `data/processed/queries_with_hard_negatives_20251104_224640.json` - Final dataset with hard negatives
- `HARD_NEGATIVES_SUMMARY.md` - This summary document

## Key Takeaways

1. **Hard negatives are essential** for contrastive learning - without them, the model can't learn fine-grained distinctions
2. **Semantic coherence matters** - hard negatives should be topically related but semantically incorrect
3. **Data quality > Data quantity** - Removing 93 bad positive pairs is more important than having more data
4. **Balance is important** - 36.3% positive pairs provides good balance for contrastive learning
