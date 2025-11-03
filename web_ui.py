"""
Superconductor Semantic Search - Web UI
========================================

Flask-based web interface for the semantic search engine.
Features:
- Clean, modern design
- Color-coded difficulty levels
- Top 5 most relevant results
- Links and descriptions for each result
"""

from flask import Flask, render_template, request, jsonify
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)

# ============================================================================
# LOAD SEARCH SYSTEM
# ============================================================================

print("Loading search system...")

# Load FAISS index
faiss_index = faiss.read_index("data/search_index/faiss_index.bin")

# Load documents
with open("data/search_index/documents.json", 'r', encoding='utf-8') as f:
    documents = json.load(f)

# Load metadata
with open("data/search_index/index_metadata.json", 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Load model
model = SentenceTransformer(metadata['model_path'])

print(f"✅ Search system loaded! {len(documents)} documents indexed")

# ============================================================================
# SEARCH FUNCTION
# ============================================================================

def detect_query_difficulty(query):
    """
    Detect the difficulty level of a query based on keywords.

    Returns:
        int: Estimated difficulty level (1-5)
    """
    query_lower = query.lower()

    # Beginner indicators
    beginner_keywords = ['what is', 'explain', 'introduction', 'basics', 'simple',
                         'beginner', 'how does', 'what are', 'eli5', 'for dummies']
    if any(kw in query_lower for kw in beginner_keywords):
        return 1

    # Expert indicators
    expert_keywords = ['derive', 'proof', 'hamiltonian', 'eigenvalue', 'tensor',
                       'renormalization', 'lagrangian', 'quantum field', 'topology']
    if any(kw in query_lower for kw in expert_keywords):
        return 4

    # Advanced indicators
    advanced_keywords = ['mechanism', 'theory of', 'calculate', 'mathematical',
                        'statistical mechanics', 'thermodynamics']
    if any(kw in query_lower for kw in advanced_keywords):
        return 3

    # Default to intermediate
    return 2

def perform_search(query, k=10, difficulty_filter=None):
    """
    Search for documents matching the query with difficulty-aware ranking.

    Args:
        query: Search query string
        k: Number of results to return (default 10)
        difficulty_filter: Optional difficulty level (1-5)

    Returns:
        List of result dictionaries
    """
    # Encode query
    query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(query_embedding)

    # Detect query difficulty if no filter specified
    query_difficulty = detect_query_difficulty(query) if not difficulty_filter else None

    # Search more results for better ranking
    search_k = k * 20  # Get more candidates for re-ranking
    scores, indices = faiss_index.search(query_embedding, min(search_k, len(documents)))

    # Collect and score results
    results = []
    for score, idx in zip(scores[0], indices[0]):
        doc = documents[idx]

        # Apply difficulty filter if specified
        if difficulty_filter and doc.get('difficulty_level') != difficulty_filter:
            continue

        # Boost score for difficulty match
        adjusted_score = float(score)
        if query_difficulty and not difficulty_filter:
            doc_difficulty = doc.get('difficulty_level', 3)

            # Boost if difficulties match
            if doc_difficulty == query_difficulty:
                adjusted_score *= 1.3  # 30% boost for exact match
            elif abs(doc_difficulty - query_difficulty) == 1:
                adjusted_score *= 1.1  # 10% boost for close match

            # Extra boost for beginner content on beginner queries
            if query_difficulty == 1 and doc_difficulty == 1:
                adjusted_score *= 1.2  # Additional 20% boost

        # Boost for title match (helps with specific queries like "room temperature superconductor")
        doc_title = doc.get('title', '').lower()
        query_terms = query.lower().split()

        # Filter out common stop words
        stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are'}
        meaningful_terms = [term for term in query_terms if term not in stop_words and len(term) > 2]

        if meaningful_terms:
            # Count how many query terms appear in title
            terms_in_title = sum(1 for term in meaningful_terms if term in doc_title)
            match_ratio = terms_in_title / len(meaningful_terms)

            # Apply boost based on match ratio
            if match_ratio >= 0.8:  # 80%+ of terms match
                adjusted_score *= 1.5  # Strong boost for near-complete title match
            elif match_ratio >= 0.5:  # 50%+ of terms match
                adjusted_score *= 1.3  # Moderate boost for partial title match
            elif match_ratio >= 0.3:  # 30%+ of terms match
                adjusted_score *= 1.15  # Small boost for weak title match

        # Get difficulty name
        difficulty_level = doc.get('difficulty_level', 3)
        difficulty_names = {
            1: "Beginner",
            2: "Intermediate",
            3: "Advanced",
            4: "Expert",
            5: "Cutting-edge"
        }
        difficulty_name = difficulty_names.get(difficulty_level, "Advanced")

        # Generate description from available metadata
        source = doc.get('source', 'unknown')
        doc_type = doc.get('type', 'document')
        word_count = doc.get('word_count') or 0

        # Create informative description from metadata
        source_names = {
            'wikipedia': 'Wikipedia article',
            'simple_wikipedia': 'Simple Wikipedia article (beginner-friendly)',
            'arxiv': 'Research paper from arXiv',
            'mit_ocw': 'MIT OpenCourseWare material',
            'youtube': 'Video transcript'
        }

        source_desc = source_names.get(source, f'{source} {doc_type}')
        title_text = doc.get('title') or 'superconductors'
        if word_count > 0:
            description = f"{source_desc} about {title_text}. Contains approximately {word_count:,} words."
        else:
            description = f"{source_desc} about {title_text}."

        # Add focus area if available
        focus_area = doc.get('focus_area')
        if focus_area and focus_area != 'main':
            focus_names = {
                'hot_topic': 'Covers cutting-edge developments and recent breakthroughs.',
                'sub_focus': 'Includes computational and AI/ML perspectives.'
            }
            if focus_area in focus_names:
                description += ' ' + focus_names[focus_area]

        result = {
            'rank': len(results) + 1,
            'score': adjusted_score,
            'original_score': float(score),
            'title': doc.get('title', 'Untitled'),
            'url': doc.get('url', '#'),
            'source': doc.get('source', 'unknown'),
            'difficulty_level': difficulty_level,
            'difficulty_name': difficulty_name,
            'description': description,
            'type': doc.get('type', 'document'),
            'word_count': doc.get('word_count', 0)
        }

        results.append(result)

    # Sort by adjusted score (higher is better)
    results.sort(key=lambda x: x['score'], reverse=True)

    # Re-rank and limit to k results
    for i, result in enumerate(results[:k], 1):
        result['rank'] = i

    return results[:k]

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render the main search page."""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for search queries."""
    try:
        data = request.json
        query = data.get('query', '').strip()
        difficulty_filter = data.get('difficulty_filter')

        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400

        # Perform search
        results = perform_search(query, k=10, difficulty_filter=difficulty_filter)

        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API endpoint for system statistics."""
    return jsonify({
        'total_documents': len(documents),
        'sources': metadata.get('source_breakdown', {}),
        'difficulty_levels': metadata.get('difficulty_breakdown', {})
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    print("\n" + "="*80)
    print("🚀 Starting Superconductor Search Web UI")
    print("="*80)
    print("\n📊 System Info:")
    print(f"   Documents: {len(documents)}")
    print(f"   Sources: {', '.join(metadata.get('source_breakdown', {}).keys())}")
    print(f"\n🌐 Open your browser to: http://localhost:8080")
    print("   Press Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=8080)
