"""
Superconductor Semantic Search V7 - Semantic Relevance Search
==============================================================

Gradio interface for the semantic search engine using Model V7.
Returns the most semantically relevant results with difficulty labels.
"""

import gradio as gr
import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import os
from pathlib import Path

# ============================================================================
# LOAD MODEL AND DOCUMENTS
# ============================================================================

print("=" * 70)
print("🚀 Loading Superconductor Search V7...")
print("=" * 70)

# Load Model V7
print("📥 Loading Model V7...")
model_path = "models/superconductor-search-v7"
model = SentenceTransformer(model_path)
print(f"✅ Model V7 loaded from: {model_path}")

# Load documents
print("📥 Loading documents...")
docs_path = "training/documents.json"
with open(docs_path, 'r', encoding='utf-8') as f:
    documents = json.load(f)
print(f"✅ Documents loaded: {len(documents)} documents")

# Encode all documents
print("🔄 Encoding documents...")
doc_texts = [str(doc.get('content', ''))[:500] for doc in documents]  # Use first 500 chars
doc_embeddings = model.encode(doc_texts, convert_to_numpy=True, show_progress_bar=True)
print(f"✅ Document embeddings created: {doc_embeddings.shape}")

print("=" * 70)
print(f"✅ Search system ready! {len(documents)} documents indexed")
print("=" * 70)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_document_difficulty_label(doc: dict) -> str:
    """
    Get difficulty label for a document based on its source and difficulty_level field.

    Returns:
        'Beginner', 'Intermediate', or 'Advanced'
    """
    # First check if document has explicit difficulty level
    doc_difficulty = doc.get('difficulty_level', None)
    if doc_difficulty:
        if doc_difficulty <= 2:
            return 'Beginner'
        elif doc_difficulty <= 3:
            return 'Intermediate'
        else:
            return 'Advanced'

    # Fallback: infer from source
    source = doc.get('source', 'unknown')
    if source == 'simple_wikipedia':
        return 'Beginner'
    elif source in ['wikipedia', 'youtube', 'hyperphysics']:
        return 'Intermediate'
    elif source in ['arxiv', 'mit_ocw']:
        return 'Advanced'
    else:
        return 'Intermediate'

def get_best_results(similarities: np.ndarray, top_k: int = 10, sort_by_difficulty: bool = False) -> list:
    """
    Get top-k results sorted by similarity score.

    Args:
        similarities: Similarity scores for all documents
        top_k: Number of results to return
        sort_by_difficulty: If True, sort results by difficulty (Beginner → Advanced)
                          while preserving semantic relevance within each tier

    Returns:
        List of (idx, score, doc, difficulty) tuples
    """
    # Get top indices sorted by similarity
    top_indices = np.argsort(-similarities)[:top_k]

    results = []
    for idx in top_indices:
        doc = documents[idx]
        score = float(similarities[idx])
        difficulty = get_document_difficulty_label(doc)

        results.append((idx, score, doc, difficulty))

    # Sort by difficulty if requested
    if sort_by_difficulty:
        # Define difficulty ordering
        difficulty_order = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}

        # Sort by difficulty first (ascending), then by similarity (descending) within each tier
        results.sort(key=lambda x: (difficulty_order.get(x[3], 2), -x[1]))

    return results

# ============================================================================
# SEARCH FUNCTION
# ============================================================================

def perform_search(query, sort_by_difficulty=False, num_results=10):
    """
    Search for documents matching the query.
    Returns the most relevant documents and labels them by their difficulty level.

    Args:
        query: Search query string
        sort_by_difficulty: If True, sort results by difficulty (Beginner → Advanced)
        num_results: Number of results to return
    """
    if not query or not query.strip():
        return "<p style='color: red;'>Please enter a search query.</p>"

    # Encode query
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Calculate similarities
    similarities = util.cos_sim(query_embedding, doc_embeddings)[0].cpu().numpy()

    # Get best results (sorted by similarity or difficulty)
    results = get_best_results(similarities, top_k=num_results, sort_by_difficulty=sort_by_difficulty)

    if not results:
        return "<p style='color: orange;'>No results found. Try a different query.</p>"

    # Colors for different difficulty levels
    difficulty_colors = {
        'Beginner': '#16a34a',       # Green
        'Intermediate': '#0ea5e9',   # Blue
        'Advanced': '#f59e0b'        # Orange
    }

    source_emojis = {
        'arxiv': '📄',
        'youtube': '📺',
        'wikipedia': '📖',
        'simple_wikipedia': '📘',
        'mit_ocw': '🎓',
        'scholarpedia': '📚',
        'hyperphysics': '🔬'
    }

    # Header
    sort_info = "📚 Sorted: Beginner → Advanced (preserving relevance within each level)" if sort_by_difficulty else "🎯 Sorted: Most semantically relevant first"
    html = f"""
    <div style='margin-bottom: 20px; padding: 15px; background: #1e293b;
                border-left: 4px solid #8b5cf6; border-radius: 10px; border: 1px solid #334155;'>
        <h3 style='color:#f1f5f9; margin: 0 0 8px 0;'>🔍 Search Results for: "{query}"</h3>
        <p style='margin: 0 0 5px 0; color: #94a3b8; font-size: 0.95em;'>
            Found <strong>{len(results)}</strong> relevant results
        </p>
        <p style='margin: 0; color: #a78bfa; font-size: 0.85em; font-style: italic;'>
            {sort_info}
        </p>
    </div>
    """

    # Results
    for i, (idx, score, doc, difficulty) in enumerate(results, 1):
        source = doc.get('source', 'unknown')
        source_emoji = source_emojis.get(source, '📋')
        source_label = source.replace('_', ' ').title()
        title = doc.get('title', 'Untitled')
        url = doc.get('url', '#')
        difficulty_color = difficulty_colors.get(difficulty, '#0ea5e9')

        html += f"""
        <div style='background: #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 14px;
                    border: 1px solid #334155; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    border-left: 4px solid {difficulty_color};'>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 8px;'>
                <span style='background: {difficulty_color}; color: white; font-weight: 700;
                             border-radius: 50%; width: 28px; height: 28px; display: flex;
                             align-items: center; justify-content: center; font-size: 0.9em;'>
                    {i}
                </span>
                <a href='{url}' target='_blank' style='font-size: 1.1em; font-weight: 600;
                   color: #f1f5f9; text-decoration: none; flex: 1;'>
                    {source_emoji} {title}
                </a>
            </div>
            <div style='display: flex; gap: 8px; flex-wrap: wrap;'>
                <span style='background: {difficulty_color}; color: white; padding: 4px 12px;
                             border-radius: 999px; font-size: 0.85em; font-weight: 600;'>
                    {difficulty}
                </span>
                <span style='background: #312e81; color: #a5b4fc; padding: 4px 12px;
                             border-radius: 999px; font-size: 0.85em; font-weight: 600;'>
                    {source_label}
                </span>
                <span style='background: #0f172a; color: #94a3b8; padding: 4px 12px;
                             border-radius: 999px; font-size: 0.85em;'>
                    Similarity: {score:.4f}
                </span>
            </div>
        </div>
        """

    return html

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

with gr.Blocks(title="Superconductor Semantic Search V7", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <style>
        body, .gradio-container {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        }
        .gr-button-primary {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }
        .gr-button-primary:hover {
            box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
            transform: translateY(-1px);
        }
    </style>
    """)

    gr.HTML("""
    <div style='padding: 20px; background: #1e293b; border-radius: 10px; margin-bottom: 20px; border: 1px solid #334155;'>
        <h1 style='color: #f1f5f9; margin-bottom: 10px;'>⚡ Superconductor Semantic Search</h1>
    </div>
    """)

    gr.HTML("""
    <div style='padding: 15px; background: #1e293b; border-radius: 8px; margin-bottom: 15px; border: 1px solid #334155;'>
        <p style='color: #cbd5e1; margin: 0; line-height: 1.6; font-size: 0.95em;'>
            Search across 1,848 documents about superconductivity from Wikipedia, arXiv, YouTube, and more!
            Results are ranked by semantic relevance and labeled by difficulty level:
            <span style='color: #16a34a; font-weight: 600;'>Beginner</span>,
            <span style='color: #0ea5e9; font-weight: 600;'>Intermediate</span>, or
            <span style='color: #f59e0b; font-weight: 600;'>Advanced</span>.
        </p>
    </div>
    """)

    query_input = gr.Textbox(
        label="",
        placeholder="Search for superconductivity topics...",
        lines=2,
        show_label=False
    )

    difficulty_sort_checkbox = gr.Checkbox(
        label="📚 Sort by difficulty (Beginner → Advanced) - Creates a learning progression",
        value=False,
        info="When checked, results are reordered from easiest to most complex, providing an intro/recap at the top"
    )

    search_button = gr.Button("🔍 Search", variant="primary", size="lg")

    results_output = gr.HTML(label="Results")

    query_input.submit(
        fn=lambda q, sort_diff: perform_search(q, sort_diff, 10),
        inputs=[query_input, difficulty_sort_checkbox],
        outputs=results_output
    )

    search_button.click(
        fn=lambda q, sort_diff: perform_search(q, sort_diff, 10),
        inputs=[query_input, difficulty_sort_checkbox],
        outputs=results_output
    )

# Launch
if __name__ == "__main__":
    demo.launch()
