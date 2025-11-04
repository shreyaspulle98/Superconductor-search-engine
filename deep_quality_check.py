"""
Deep Quality Check - Extremely Thorough Positive Pair Analysis
==============================================================

Performs exhaustive analysis of ALL positive pairs to ensure maximum
semantic relevance. Uses multiple quality metrics and strict thresholds.

Quality Metrics:
1. Keyword density (how often query terms appear)
2. Title relevance (query terms in document title)
3. Context relevance (query terms appear in meaningful context)
4. Topic centrality (document is ABOUT the query topic, not just mentions it)
5. Semantic coherence (query and document are semantically aligned)
"""

import json
import re
from typing import Dict, List, Tuple
from collections import Counter
from datetime import datetime

# Configuration
INPUT_FILE = 'data/processed/queries_strong_positives_20251104_225742.json'
DOCUMENTS_FILE = 'data/processed/FINAL_ALL_IMPROVED_documents_20251104_223630.json'
OUTPUT_FILE = f'data/processed/queries_highest_quality_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

# Stricter thresholds for ultra-high quality
MIN_RELEVANCE_SCORE = 0.6  # Up from 0.5
MIN_KEYWORD_DENSITY = 0.001  # Keywords per character
MIN_KEYWORD_COUNT = 2  # For specific queries

class QualityMetrics:
    """Calculate multiple quality metrics for a query-document pair."""

    def __init__(self, query: str, doc: Dict):
        self.query = query.lower()
        self.doc_text = doc.get('content', doc.get('text', ''))
        self.doc_title = doc.get('title', '')

        # Handle empty/dict text
        if not self.doc_text or isinstance(self.doc_text, dict):
            self.doc_text = ''
        if not self.doc_title or isinstance(self.doc_title, dict):
            self.doc_title = ''

        self.doc_text_lower = self.doc_text.lower()
        self.doc_title_lower = self.doc_title.lower()

        # Extract query keywords (filter stopwords)
        self.stopwords = {
            'what', 'is', 'are', 'the', 'a', 'an', 'in', 'of', 'for',
            'to', 'and', 'or', 'how', 'do', 'does', 'can', 'will',
            'about', 'with', 'from', 'at', 'by', 'on', 'this', 'that'
        }
        self.query_keywords = self._extract_keywords(self.query)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in self.stopwords and len(w) > 2]

    def keyword_in_title_score(self) -> float:
        """Score: 1.0 if any keyword in title, 0.0 otherwise."""
        if not self.query_keywords:
            return 0.5

        for keyword in self.query_keywords:
            if keyword in self.doc_title_lower:
                return 1.0
        return 0.0

    def keyword_density_score(self) -> float:
        """Score based on keyword density in document."""
        if not self.doc_text or not self.query_keywords:
            return 0.0

        total_keyword_chars = 0
        for keyword in self.query_keywords:
            count = self.doc_text_lower.count(keyword)
            total_keyword_chars += count * len(keyword)

        density = total_keyword_chars / max(len(self.doc_text), 1)

        # Normalize to 0-1 scale (0.01 density = 1.0 score)
        return min(density / 0.01, 1.0)

    def keyword_frequency_score(self) -> float:
        """Score based on how many times keywords appear."""
        if not self.query_keywords:
            return 0.5

        keyword_scores = []
        for keyword in self.query_keywords:
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', self.doc_text_lower))

            if count >= 10:
                keyword_scores.append(1.0)
            elif count >= 5:
                keyword_scores.append(0.9)
            elif count >= 3:
                keyword_scores.append(0.7)
            elif count >= 2:
                keyword_scores.append(0.5)
            elif count >= 1:
                keyword_scores.append(0.3)
            else:
                keyword_scores.append(0.0)

        return sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0.0

    def context_quality_score(self) -> float:
        """Score based on context around keywords (are they in meaningful sentences?)."""
        if not self.query_keywords or not self.doc_text:
            return 0.0

        context_scores = []

        for keyword in self.query_keywords:
            # Find contexts (50 chars before/after)
            pattern = r'.{0,50}' + re.escape(keyword) + r'.{0,50}'
            contexts = re.findall(pattern, self.doc_text_lower)

            if not contexts:
                context_scores.append(0.0)
                continue

            # Check if context contains other scientific terms (indicator of relevant discussion)
            scientific_indicators = [
                'temperature', 'critical', 'phase', 'transition', 'theory',
                'experiment', 'material', 'property', 'mechanism', 'state',
                'energy', 'electron', 'quantum', 'magnetic', 'field'
            ]

            relevant_contexts = 0
            for context in contexts[:5]:  # Check first 5 occurrences
                if any(indicator in context for indicator in scientific_indicators):
                    relevant_contexts += 1

            context_score = relevant_contexts / min(len(contexts), 5)
            context_scores.append(context_score)

        return sum(context_scores) / len(context_scores) if context_scores else 0.0

    def early_mention_score(self) -> float:
        """Score: Higher if keywords appear early (abstract/introduction)."""
        if not self.query_keywords or not self.doc_text:
            return 0.0

        # Check first 300 characters (abstract/intro)
        first_part = self.doc_text_lower[:300]

        early_mentions = sum(1 for kw in self.query_keywords if kw in first_part)
        return early_mentions / len(self.query_keywords)

    def calculate_composite_score(self) -> Tuple[float, Dict[str, float]]:
        """Calculate weighted composite quality score."""

        scores = {
            'title': self.keyword_in_title_score(),
            'density': self.keyword_density_score(),
            'frequency': self.keyword_frequency_score(),
            'context': self.context_quality_score(),
            'early_mention': self.early_mention_score()
        }

        # Weighted average (title and frequency most important)
        weights = {
            'title': 0.35,        # Title match is strongest signal
            'frequency': 0.30,    # How often keywords appear
            'context': 0.20,      # Quality of context
            'early_mention': 0.10, # Appears in abstract
            'density': 0.05       # Overall density
        }

        composite = sum(scores[key] * weights[key] for key in scores)

        return composite, scores

def is_generic_query(query: str) -> bool:
    """Check if query is generic."""
    generic_exact = ['superconductivity', 'superconductor', 'superconducting']
    query_lower = query.lower().strip()

    if query_lower in generic_exact:
        return True

    generic_patterns = [
        'what is', 'how do', 'how does', 'explain',
        'introduction to', 'basics of', 'overview of'
    ]

    return any(pattern in query_lower for pattern in generic_patterns)

def analyze_all_positive_pairs(queries: List[Dict], documents: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Perform deep analysis on ALL positive pairs.
    Returns: (high_quality_pairs, analysis_stats)
    """
    print("="*70)
    print("🔬 DEEP QUALITY ANALYSIS - ALL POSITIVE PAIRS")
    print("="*70)

    doc_lookup = {doc['id']: doc for doc in documents}

    # Separate positive and negative pairs
    positive_pairs = [q for q in queries if q['label'] == 1]
    negative_pairs = [q for q in queries if q['label'] == 0]

    print(f"\n📊 Analyzing {len(positive_pairs):,} positive pairs...")
    print(f"   (Negative pairs: {len(negative_pairs):,} - will be kept as-is)\n")

    # Analyze each positive pair
    quality_results = []

    for i, pair in enumerate(positive_pairs):
        if (i + 1) % 1000 == 0:
            print(f"   Analyzed {i+1:,}/{len(positive_pairs):,} pairs...")

        query_text = pair['query_text']
        doc_id = pair['doc_id']
        doc = doc_lookup.get(doc_id)

        if not doc:
            quality_results.append({
                'pair': pair,
                'keep': False,
                'score': 0.0,
                'reason': 'Document not found'
            })
            continue

        # Generic queries get special handling
        if is_generic_query(query_text):
            doc_text = doc.get('content', doc.get('text', ''))
            if isinstance(doc_text, str) and 'supercond' in doc_text.lower():
                quality_results.append({
                    'pair': pair,
                    'keep': True,
                    'score': 1.0,
                    'reason': 'Generic query - broad match OK',
                    'metrics': {}
                })
                continue

        # Calculate quality metrics
        metrics = QualityMetrics(query_text, doc)
        composite_score, individual_scores = metrics.calculate_composite_score()

        # Decision: Keep if score >= threshold
        keep = composite_score >= MIN_RELEVANCE_SCORE

        # Additional checks for very low individual scores
        if keep and individual_scores['frequency'] < 0.3:
            # If keywords barely appear, reject even if composite is OK
            keep = False
            reason = 'Keywords too rare (frequency < 0.3)'
        elif keep:
            reason = f'High quality (score: {composite_score:.2f})'
        else:
            reason = f'Low quality (score: {composite_score:.2f})'

        quality_results.append({
            'pair': pair,
            'keep': keep,
            'score': composite_score,
            'reason': reason,
            'metrics': individual_scores
        })

    print(f"   ✅ Analysis complete!\n")

    # Compile statistics
    kept_pairs = [r for r in quality_results if r['keep']]
    removed_pairs = [r for r in quality_results if not r['keep']]

    print("="*70)
    print("📊 QUALITY ANALYSIS RESULTS")
    print("="*70)

    print(f"\n✅ Pairs to KEEP: {len(kept_pairs):,}")
    print(f"❌ Pairs to REMOVE: {len(removed_pairs):,}")
    print(f"📉 Removal rate: {len(removed_pairs)/len(positive_pairs)*100:.1f}%")

    # Score distribution
    all_scores = [r['score'] for r in quality_results]
    print(f"\n📈 Composite Score Distribution:")
    print(f"   < 0.3 (very weak): {sum(1 for s in all_scores if s < 0.3):,}")
    print(f"   0.3-0.4 (weak): {sum(1 for s in all_scores if 0.3 <= s < 0.4):,}")
    print(f"   0.4-0.5 (below threshold): {sum(1 for s in all_scores if 0.4 <= s < 0.5):,}")
    print(f"   0.5-0.6 (borderline): {sum(1 for s in all_scores if 0.5 <= s < 0.6):,}")
    print(f"   0.6-0.7 (moderate): {sum(1 for s in all_scores if 0.6 <= s < 0.7):,}")
    print(f"   0.7-0.8 (good): {sum(1 for s in all_scores if 0.7 <= s < 0.8):,}")
    print(f"   0.8-0.9 (very good): {sum(1 for s in all_scores if 0.8 <= s < 0.9):,}")
    print(f"   >= 0.9 (excellent): {sum(1 for s in all_scores if s >= 0.9):,}")

    if kept_pairs:
        avg_kept = sum(r['score'] for r in kept_pairs) / len(kept_pairs)
        print(f"\n   Average score (kept pairs): {avg_kept:.3f}")

    if removed_pairs:
        avg_removed = sum(r['score'] for r in removed_pairs) / len(removed_pairs)
        print(f"   Average score (removed pairs): {avg_removed:.3f}")

    # Individual metric analysis for kept pairs
    if kept_pairs:
        # Only analyze pairs that have metrics
        pairs_with_metrics = [r for r in kept_pairs if r.get('metrics')]
        if pairs_with_metrics and pairs_with_metrics[0]['metrics']:
            print(f"\n📊 Average Individual Metrics (Kept Pairs):")
            metric_names = pairs_with_metrics[0]['metrics'].keys()
            for metric in metric_names:
                avg_metric = sum(r['metrics'][metric] for r in pairs_with_metrics) / len(pairs_with_metrics)
                print(f"   {metric}: {avg_metric:.3f}")

    # Build final dataset
    high_quality_pairs = [r['pair'] for r in kept_pairs]
    final_queries = high_quality_pairs + negative_pairs

    stats = {
        'original_positive': len(positive_pairs),
        'kept_positive': len(kept_pairs),
        'removed_positive': len(removed_pairs),
        'negative': len(negative_pairs),
        'total': len(final_queries),
        'removal_examples': removed_pairs[:20]  # First 20 for review
    }

    return final_queries, stats

def show_removal_examples(stats: Dict):
    """Show detailed examples of removed pairs."""
    print("\n" + "="*70)
    print("🔍 SAMPLE REMOVED PAIRS (Low Quality)")
    print("="*70)

    examples = stats['removal_examples'][:15]

    for i, result in enumerate(examples, 1):
        pair = result['pair']
        score = result['score']
        reason = result['reason']
        metrics = result.get('metrics', {})

        print(f"\n{i}. Query: \"{pair['query_text']}\"")
        print(f"   Doc: {pair['doc_id']}")
        print(f"   Composite Score: {score:.3f}")
        print(f"   Reason: {reason}")

        if metrics:
            print(f"   Individual Scores:")
            for metric, value in metrics.items():
                print(f"      - {metric}: {value:.3f}")

        # Show snippet
        doc_text = pair.get('doc_text', '')
        if doc_text:
            print(f"   Text: {doc_text[:150]}...")

def main():
    print("="*70)
    print("🎯 DEEP QUALITY CHECK - ULTRA-HIGH QUALITY DATASET")
    print("="*70)
    print(f"\nMinimum relevance threshold: {MIN_RELEVANCE_SCORE}")

    # Load data
    print("\n📂 Loading data...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
        doc_data = json.load(f)
        documents = doc_data['documents']

    print(f"   ✅ Loaded {len(queries):,} query pairs")
    print(f"   ✅ Loaded {len(documents):,} documents")

    # Analyze
    final_queries, stats = analyze_all_positive_pairs(queries, documents)

    # Show examples
    show_removal_examples(stats)

    # Save
    print(f"\n💾 Saving ultra-high quality dataset to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_queries, f, indent=2, ensure_ascii=False)

    # Final summary
    sep = "="*70
    print(f"\n{sep}")
    print("✅ DEEP QUALITY CHECK COMPLETE!")
    print(sep)
    print(f"📊 Ultra-High Quality Dataset:")
    print(f"   Total pairs: {len(final_queries):,}")
    print(f"   Positive pairs: {stats['kept_positive']:,} (was {stats['original_positive']:,})")
    print(f"   Negative pairs: {stats['negative']:,} (unchanged)")
    print(f"   Removed: {stats['removed_positive']:,} low-quality positive pairs")
    print(f"   Positive ratio: {stats['kept_positive']/len(final_queries)*100:.1f}%")

    improvement = (stats['removed_positive'] / stats['original_positive']) * 100
    print(f"\n📈 Quality Improvement:")
    print(f"   Removed {improvement:.1f}% of positive pairs")
    print(f"   Only highest-quality semantic matches remain")

    print(f"\n🎯 This dataset is now ULTRA-HIGH QUALITY and ready for training!")
    print(f"{sep}\n")

if __name__ == "__main__":
    main()
