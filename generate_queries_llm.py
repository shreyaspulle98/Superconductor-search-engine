"""
Automated Query Generation using Claude API
============================================

Generates high-quality, domain-specific training queries for semantic search.

Strategy:
- Beginner/Intermediate docs: 10 queries (more short/simple queries)
- Expert docs (arXiv): 15 queries (more detailed technical queries)
- Mix of short keywords, simple questions, and detailed queries

DO NOT RETRAIN MODEL - Just generate queries for review first!

Usage:
    python generate_queries_llm.py --sample 5      # Test on 5 docs
    python generate_queries_llm.py --all           # Generate for all 1,086 docs
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict
import argparse
from anthropic import Anthropic
from tqdm import tqdm

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for query generation"""

    # Paths
    DOCUMENTS_PATH = "data/processed/merged_all_20251103_124240.json"
    OUTPUT_PATH = "data/processed/training_pairs_llm_generated.json"
    OUTPUT_DIR = "data/processed"

    # API
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    MODEL = "claude-3-5-sonnet-20241022"

    # Query generation
    QUERIES_PER_DOC_BASIC = 10      # For beginner/intermediate
    QUERIES_PER_DOC_EXPERT = 15     # For expert (arXiv papers)

    # Rate limiting
    REQUESTS_PER_MINUTE = 50  # Claude API limit
    DELAY_BETWEEN_REQUESTS = 1.2  # seconds (50 req/min = 1.2s delay)

config = Config()

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

def create_prompt(doc: Dict, num_queries: int) -> str:
    """
    Create prompt for Claude to generate queries.

    Adjusted based on difficulty level:
    - Beginner/Intermediate: More short/simple queries
    - Expert (arXiv): More detailed technical queries
    """

    doc_title = doc.get('title', 'Untitled')
    doc_text = doc.get('text', doc.get('content', ''))
    doc_preview = doc_text[:1500]  # More context for better queries
    source = doc.get('source', 'unknown')
    difficulty = doc.get('difficulty_level', 3)

    # Difficulty-specific guidance
    difficulty_info = {
        1: {
            'level': 'Beginner',
            'audience': 'high school students or curious beginners with no physics background',
            'language': 'very simple, avoid jargon, explain like teaching a 15-year-old',
            'query_mix': '4 short keywords, 3 simple questions, 3 explanatory questions'
        },
        2: {
            'level': 'Intermediate',
            'audience': 'undergraduate physics students or science enthusiasts',
            'language': 'clear but can use standard physics terms, assume basic physics knowledge',
            'query_mix': '3 short keywords, 2 simple questions, 5 detailed questions'
        },
        3: {
            'level': 'Advanced',
            'audience': 'physics graduate students or researchers in related fields',
            'language': 'technical, use specialized terminology, assume strong physics background',
            'query_mix': '2 short keywords, 2 simple questions, 6 detailed technical questions'
        },
        4: {
            'level': 'Expert',
            'audience': 'active researchers in superconductivity',
            'language': 'highly technical, use research-level terminology and concepts',
            'query_mix': '2 keywords, 1 simple question, 12 detailed research-level questions'
        },
        5: {
            'level': 'Cutting-edge',
            'audience': 'world experts in this specific subfield',
            'language': 'cutting-edge terminology, assume deep expertise',
            'query_mix': '1 keyword, 1 simple question, 13 highly specific research questions'
        }
    }

    info = difficulty_info.get(difficulty, difficulty_info[3])

    # Determine if arXiv paper (needs more detailed queries)
    is_arxiv = source == 'arxiv'

    # Add research-level guidance for expert docs
    research_level = '\n   - Research-level: "Derive...", "Calculate...", "What is the microscopic mechanism..."' if difficulty >= 4 else ''

    # Add arXiv-specific guidance
    arxiv_guidance = ""
    if is_arxiv:
        arxiv_guidance = """   - Include specific concepts from the paper
   - Reference the exact phenomena/materials/theories discussed
   - Create queries about methodologies, results, implications
   - Make queries that distinguish THIS paper from similar papers"""

    prompt = f"""You are creating training data for a semantic search engine about superconductivity.

DOCUMENT INFORMATION:
Title: {doc_title}
Source: {source}
Difficulty Level: {difficulty}/5 ({info['level']})
Target Audience: {info['audience']}

DOCUMENT EXCERPT (first 1500 chars):
{doc_preview}

YOUR TASK:
Generate {num_queries} diverse search queries that this document would be the BEST answer for.

CRITICAL REQUIREMENTS:

1. DOMAIN SPECIFICITY - Queries MUST be about superconductivity
   ❌ BAD: "what is force", "define resistance", "explain energy"
   ✅ GOOD: "what is the Meissner effect in superconductors", "how do Cooper pairs form", "BCS theory mechanism"

2. QUERY MIX - Generate variety: {info['query_mix']}

   a) SHORT KEYWORDS (1-3 words):
      - "superconductor", "cooper pairs", "meissner effect", "critical temperature"
      - "BCS theory", "Type II superconductor", "cuprate mechanism"

   b) SIMPLE QUESTIONS:
      - "what is a superconductor"
      - "what are cooper pairs"
      - "what is the meissner effect"

   c) DETAILED QUESTIONS:
      - "How do superconductors achieve zero resistance?"
      - "What is the mechanism behind high-temperature superconductivity in cuprates?"
      - "Why does electron-phonon coupling lead to Cooper pair formation?"

3. LANGUAGE LEVEL: {info['language']}

4. NATURAL VARIATION - Use different question structures:
   - Factual: "What is...", "What are...", "Define..."
   - Explanatory: "How does...", "Why...", "Explain..."
   - Comparative: "What is the difference between...", "Compare..."
   - Investigative: "What causes...", "What role does...", "How can..."{research_level}

5. SPECIFICITY FOR arXiv PAPERS:
{arxiv_guidance}

6. ENSURE CROSS-DIFFICULTY MATCHING:
   - Include some simple/general queries even for expert docs (so they appear for broad searches)
   - Include specific queries even for beginner docs (so experts can find them)
   - Example: Even for an expert paper on cuprates, include "cuprate superconductors" as a query

OUTPUT FORMAT (JSON only, no markdown):
{{
  "queries": [
    "query 1",
    "query 2",
    ...
    "query {num_queries}"
  ]
}}

IMPORTANT:
- Return ONLY valid JSON
- No explanations, no markdown code blocks
- Exactly {num_queries} queries
- All queries must be about SUPERCONDUCTIVITY specifically
"""

    return prompt


# ============================================================================
# QUERY GENERATION
# ============================================================================

def generate_queries_for_document(
    doc: Dict,
    client: Anthropic,
    num_queries: int
) -> List[str]:
    """
    Generate queries for a single document using Claude API.

    Args:
        doc: Document dictionary
        client: Anthropic client
        num_queries: Number of queries to generate

    Returns:
        List of generated queries
    """

    prompt = create_prompt(doc, num_queries)

    try:
        response = client.messages.create(
            model=config.MODEL,
            max_tokens=2000,
            temperature=0.8,  # Some creativity for variation
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract text from response
        response_text = response.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()

        # Parse JSON
        result = json.loads(response_text)
        queries = result.get('queries', [])

        if len(queries) != num_queries:
            print(f"  ⚠️  Expected {num_queries} queries, got {len(queries)}")

        return queries

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parse error: {e}")
        print(f"  Response was: {response_text[:200]}...")
        return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def generate_all_queries(
    documents: List[Dict],
    output_path: str,
    sample_size: int = None
) -> List[Dict]:
    """
    Generate queries for all documents (or sample).

    Args:
        documents: List of document dictionaries
        output_path: Where to save results
        sample_size: If set, only process this many documents (for testing)

    Returns:
        List of training pairs
    """

    # Check API key
    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not found in environment!")

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Sample if requested
    if sample_size:
        documents = documents[:sample_size]
        print(f"📊 SAMPLE MODE: Processing {sample_size} documents")

    print(f"\n🚀 Starting query generation for {len(documents)} documents")
    print(f"💰 Estimated cost: ${len(documents) * 0.003:.2f}")
    print(f"⏱️  Estimated time: {len(documents) * 1.5 / 60:.1f} minutes\n")

    training_pairs = []
    total_queries = 0
    errors = 0

    # Progress bar
    for i, doc in enumerate(tqdm(documents, desc="Generating queries")):

        # Determine number of queries based on difficulty/source
        source = doc.get('source', '')
        difficulty = doc.get('difficulty_level', 3)

        # More queries for expert/arXiv papers
        if source == 'arxiv' or difficulty >= 4:
            num_queries = config.QUERIES_PER_DOC_EXPERT
        else:
            num_queries = config.QUERIES_PER_DOC_BASIC

        # Generate queries
        queries = generate_queries_for_document(doc, client, num_queries)

        if not queries:
            errors += 1
            continue

        # Create training pairs (positive only for now)
        doc_id = doc.get('id', f'doc_{i}')
        doc_text = doc.get('text', doc.get('content', ''))
        doc_difficulty = doc.get('difficulty_level', 3)

        for query in queries:
            training_pairs.append({
                "query_text": query,
                "query_difficulty": doc_difficulty,  # Inherit from doc
                "doc_id": doc_id,
                "doc_text": doc_text,
                "doc_difficulty": doc_difficulty,
                "label": 1,
                "pair_type": "llm_generated_positive"
            })
            total_queries += 1

        # Rate limiting
        if i < len(documents) - 1:  # Don't wait after last request
            time.sleep(config.DELAY_BETWEEN_REQUESTS)

        # Save checkpoint every 50 documents
        if (i + 1) % 50 == 0:
            checkpoint_path = output_path.replace('.json', f'_checkpoint_{i+1}.json')
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(training_pairs, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Checkpoint saved: {checkpoint_path}")

    # Save final results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(training_pairs, f, indent=2, ensure_ascii=False)

    # Statistics
    sep = '='*70
    print(f"\n{sep}")
    print(f"✅ GENERATION COMPLETE!")
    print(sep)
    print(f"📊 Documents processed: {len(documents)}")
    print(f"📊 Total queries generated: {total_queries}")
    print(f"📊 Average queries per doc: {total_queries/len(documents):.1f}")
    print(f"❌ Errors: {errors}")
    print(f"💾 Saved to: {output_path}")
    print(f"{'='*70}\n")

    return training_pairs


# ============================================================================
# ANALYSIS & PREVIEW
# ============================================================================

def analyze_generated_queries(training_pairs: List[Dict]):
    """Analyze quality of generated queries"""

    print("\n📊 QUERY ANALYSIS\n")

    # Count unique queries
    unique_queries = set([p['query_text'] for p in training_pairs])
    print(f"Unique queries: {len(unique_queries)}")
    print(f"Total pairs: {len(training_pairs)}")

    # Check superconductor relevance
    super_keywords = ['superconductor', 'superconduct', 'meissner', 'cooper',
                      'bcs', 'critical temperature', 'cuprate', 'pnictide',
                      'josephson', 'flux', 'pairing', 'gap', 'tc']

    relevant = sum(1 for q in unique_queries
                   if any(kw in q.lower() for kw in super_keywords))

    print(f"Domain-specific queries: {relevant}/{len(unique_queries)} ({relevant/len(unique_queries)*100:.1f}%)")

    # Query length distribution
    short = sum(1 for q in unique_queries if len(q.split()) <= 3)
    medium = sum(1 for q in unique_queries if 4 <= len(q.split()) <= 8)
    long = sum(1 for q in unique_queries if len(q.split()) > 8)

    print(f"\nQuery length distribution:")
    print(f"  Short (1-3 words): {short} ({short/len(unique_queries)*100:.1f}%)")
    print(f"  Medium (4-8 words): {medium} ({medium/len(unique_queries)*100:.1f}%)")
    print(f"  Long (9+ words): {long} ({long/len(unique_queries)*100:.1f}%)")

    # Sample queries
    print(f"\n📝 Sample queries (random 20):")
    import random
    sample = random.sample(list(unique_queries), min(20, len(unique_queries)))
    for i, q in enumerate(sample, 1):
        print(f"  {i:2d}. {q}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate training queries using Claude API')
    parser.add_argument('--sample', type=int, help='Process only N documents (for testing)')
    parser.add_argument('--all', action='store_true', help='Process all documents')
    parser.add_argument('--analyze', type=str, help='Analyze existing query file')

    args = parser.parse_args()

    # Analyze mode
    if args.analyze:
        with open(args.analyze, 'r') as f:
            pairs = json.load(f)
        analyze_generated_queries(pairs)
        return

    # Check mode
    if not args.sample and not args.all:
        print("❌ Please specify --sample N or --all")
        print("\nExamples:")
        print("  python generate_queries_llm.py --sample 5")
        print("  python generate_queries_llm.py --all")
        return

    # Load documents
    print(f"📂 Loading documents from {config.DOCUMENTS_PATH}")
    with open(config.DOCUMENTS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        documents = data['documents'] if 'documents' in data else data

    print(f"✅ Loaded {len(documents)} documents\n")

    # Create output directory
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Generate queries
    sample_size = args.sample if args.sample else None
    output_path = config.OUTPUT_PATH

    if sample_size:
        output_path = output_path.replace('.json', f'_sample_{sample_size}.json')

    training_pairs = generate_all_queries(documents, output_path, sample_size)

    # Analyze results
    analyze_generated_queries(training_pairs)

    sep = '='*70
    print(f"\n{sep}")
    print("🎉 NEXT STEPS:")
    print(sep)
    print(f"1. Review generated queries in: {output_path}")
    print(f"2. Check quality with: python generate_queries_llm.py --analyze {output_path}")
    print(f"3. If satisfied, add hard negatives: python add_hard_negatives.py")
    print(f"4. Finally, retrain model: python train_model_v2.py")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
