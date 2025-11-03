"""
Superconductor Semantic Search - HuggingFace Spaces App
========================================================

Gradio interface for the semantic search engine.
This is the entry point for HuggingFace Spaces deployment.
"""

import gradio as gr
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

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

# Load model (will download from HuggingFace if not present locally)
model_path = metadata.get('model_path', 'models/superconductor-search-v1')
if not os.path.exists(model_path):
    # Fall back to HuggingFace Hub
    model_path = "shreyaspulle98/superconductor-search-v1"  # Will be uploaded to HF

model = SentenceTransformer(model_path)

print(f"✅ Search system loaded! {len(documents)} documents indexed")

# ============================================================================
# SEARCH FUNCTION
# ============================================================================

def detect_query_difficulty(query):
    """Detect the difficulty level of a query based on keywords."""
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

    return 2

def perform_search(query, difficulty_filter=None, num_results=10):
    """
    Search for documents matching the query with difficulty-aware ranking.

    Args:
        query: Search query string
        difficulty_filter: Optional difficulty level filter ("All" or 1-5)
        num_results: Number of results to return

    Returns:
        Formatted HTML string with results
    """
    if not query or not query.strip():
        return "<p style='color: red;'>Please enter a search query.</p>"

    # Encode query
    query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(query_embedding)

    # Detect query difficulty if no filter specified
    query_difficulty = detect_query_difficulty(query) if difficulty_filter == "All" else None

    # Search more results for better ranking
    search_k = num_results * 10
    scores, indices = faiss_index.search(query_embedding, min(search_k, len(documents)))

    # Collect and score results
    results = []
    for score, idx in zip(scores[0], indices[0]):
        doc = documents[idx]

        # Apply difficulty filter if specified
        if difficulty_filter != "All":
            filter_level = int(difficulty_filter)
            if doc.get('difficulty_level') != filter_level:
                continue

        # Boost score for difficulty match
        adjusted_score = float(score)
        if query_difficulty:
            doc_difficulty = doc.get('difficulty_level', 3)

            if doc_difficulty == query_difficulty:
                adjusted_score *= 1.3
            elif abs(doc_difficulty - query_difficulty) == 1:
                adjusted_score *= 1.1

            if query_difficulty == 1 and doc_difficulty == 1:
                adjusted_score *= 1.2

        # Boost for title match
        doc_title = doc.get('title', '').lower()
        query_terms = query.lower().split()
        stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are'}
        meaningful_terms = [term for term in query_terms if term not in stop_words and len(term) > 2]

        if meaningful_terms:
            terms_in_title = sum(1 for term in meaningful_terms if term in doc_title)
            match_ratio = terms_in_title / len(meaningful_terms)

            if match_ratio >= 0.8:
                adjusted_score *= 1.5
            elif match_ratio >= 0.5:
                adjusted_score *= 1.3
            elif match_ratio >= 0.3:
                adjusted_score *= 1.15

        results.append({
            'score': adjusted_score,
            'title': doc.get('title', 'Untitled'),
            'url': doc.get('url', '#'),
            'source': doc.get('source', 'unknown'),
            'difficulty_level': doc.get('difficulty_level', 3),
            'word_count': doc.get('word_count', 0)
        })

    # Sort by adjusted score
    results.sort(key=lambda x: x['score'], reverse=True)
    results = results[:num_results]

    if not results:
        return "<p style='color: orange;'>No results found. Try a different query or remove the difficulty filter.</p>"

    # Format results as HTML
    difficulty_colors = {
        1: "#d4edda",
        2: "#d1ecf1",
        3: "#fff3cd",
        4: "#f8d7da",
        5: "#d6d8db"
    }

    difficulty_names = {
        1: "Beginner",
        2: "Intermediate",
        3: "Advanced",
        4: "Expert",
        5: "Cutting-edge"
    }

    html = f"<h3>Top {len(results)} Results for: '{query}'</h3><br>"

    for i, result in enumerate(results, 1):
        level = result['difficulty_level']
        bg_color = difficulty_colors.get(level, "#e9ecef")
        diff_name = difficulty_names.get(level, "Advanced")

        html += f"""
        <div style='background: white; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 12px;'>
            <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                <span style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                             border-radius: 50%; width: 28px; height: 28px; display: inline-flex;
                             align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;'>
                    {i}
                </span>
                <a href='{result['url']}' target='_blank' style='font-size: 1.2em; font-weight: bold;
                   color: #333; text-decoration: none;'>
                    {result['title']}
                </a>
            </div>
            <div style='display: flex; gap: 8px; margin-bottom: 8px;'>
                <span style='background: {bg_color}; padding: 4px 12px; border-radius: 12px;
                             font-size: 0.85em; font-weight: 600;'>
                    {diff_name}
                </span>
                <span style='background: #e9ecef; padding: 4px 12px; border-radius: 12px;
                             font-size: 0.85em; font-weight: 600;'>
                    {result['source']}
                </span>
                <span style='color: #999; font-size: 0.85em; padding: 4px 12px;'>
                    {result['word_count']:,} words
                </span>
            </div>
            <div style='font-size: 0.9em; color: #666;'>
                Score: {result['score']:.4f}
            </div>
        </div>
        """

    return html

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

with gr.Blocks(title="Superconductor Semantic Search", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # ⚡ Superconductor Semantic Search

    Semantic search engine across research papers, lectures, and educational content about superconductivity.
    Powered by fine-tuned sentence transformers and FAISS vector search.

    **Dataset**: 1,086 documents from Wikipedia, arXiv, MIT OCW, Simple Wikipedia, Scholarpedia, and HyperPhysics.
    """)

    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label="Search Query",
                placeholder="Ask a question about superconductors...",
                lines=2
            )
        with gr.Column(scale=1):
            difficulty_dropdown = gr.Dropdown(
                label="Difficulty Filter",
                choices=["All", "1", "2", "3", "4", "5"],
                value="All",
                info="Filter by difficulty level"
            )

    with gr.Row():
        num_results_slider = gr.Slider(
            minimum=5,
            maximum=20,
            value=10,
            step=1,
            label="Number of Results"
        )

    search_button = gr.Button("🔍 Search", variant="primary", size="lg")

    results_output = gr.HTML(label="Results")

    # Examples
    gr.Examples(
        examples=[
            ["What is a superconductor?", "All", 10],
            ["room temperature superconductor", "All", 10],
            ["BCS theory mechanism", "4", 10],
            ["How does the Meissner effect work?", "2", 10],
            ["high-Tc cuprate superconductors", "3", 10],
        ],
        inputs=[query_input, difficulty_dropdown, num_results_slider],
    )

    search_button.click(
        fn=perform_search,
        inputs=[query_input, difficulty_dropdown, num_results_slider],
        outputs=results_output
    )

    gr.Markdown("""
    ---
    ### About

    **Difficulty Levels:**
    - 🟢 **Level 1 (Beginner)**: Introductory content from Simple Wikipedia and basic resources
    - 🔵 **Level 2 (Intermediate)**: Wikipedia articles and educational content
    - 🟡 **Level 3 (Advanced)**: Specialized encyclopedia entries and advanced lectures
    - 🔴 **Level 4 (Expert)**: Research papers and technical documentation
    - ⚫ **Level 5 (Cutting-edge)**: Latest research and preprints

    **Features:**
    - Difficulty-aware ranking (matches query complexity to content level)
    - Title matching boost (prioritizes documents with relevant titles)
    - Semantic search (understands meaning, not just keywords)

    Built with [Sentence Transformers](https://www.sbert.net/) and [FAISS](https://github.com/facebookresearch/faiss)
    """)

# Launch
if __name__ == "__main__":
    demo.launch()
