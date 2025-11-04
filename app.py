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
    difficulty_styles = {
        1: {
            "name": "Beginner",
            "chip_bg": "#16a34a",
            "chip_text": "#f0fdf4",
            "accent": "linear-gradient(135deg, rgba(22, 163, 74, 0.08) 0%, rgba(22, 163, 74, 0.35) 55%, rgba(15, 23, 42, 0.0) 100%)",
            "border": "#16a34a"
        },
        2: {
            "name": "Intermediate",
            "chip_bg": "#0ea5e9",
            "chip_text": "#f0f9ff",
            "accent": "linear-gradient(135deg, rgba(14, 165, 233, 0.08) 0%, rgba(14, 165, 233, 0.35) 55%, rgba(15, 23, 42, 0.0) 100%)",
            "border": "#0ea5e9"
        },
        3: {
            "name": "Advanced",
            "chip_bg": "#f59e0b",
            "chip_text": "#fff7ed",
            "accent": "linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.3) 55%, rgba(15, 23, 42, 0.0) 100%)",
            "border": "#f59e0b"
        },
        4: {
            "name": "Expert",
            "chip_bg": "#ef4444",
            "chip_text": "#fef2f2",
            "accent": "linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.35) 55%, rgba(15, 23, 42, 0.0) 100%)",
            "border": "#ef4444"
        },
        5: {
            "name": "Cutting-edge",
            "chip_bg": "#6366f1",
            "chip_text": "#eef2ff",
            "accent": "linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(99, 102, 241, 0.3) 55%, rgba(15, 23, 42, 0.0) 100%)",
            "border": "#6366f1"
        }
    }

    default_style = {
        "name": "Advanced",
        "chip_bg": "#475569",
        "chip_text": "#f8fafc",
        "accent": "linear-gradient(135deg, rgba(71, 85, 105, 0.1) 0%, rgba(71, 85, 105, 0.25) 55%, rgba(15, 23, 42, 0.0) 100%)",
        "border": "#475569"
    }

    html = f"<h3 style='color:#f8fafc;'>Top {len(results)} Results for: '{query}'</h3><br>"

    for i, result in enumerate(results, 1):
        level = result['difficulty_level']
        style = difficulty_styles.get(level, default_style)
        source_label = (result['source'] or 'unknown').replace('_', ' ').title()

        html += f"""
        <div class='result-card' style='border-left: 6px solid {style['border']}'>
            <div style='position:absolute; inset:0; background: {style['accent']}; opacity:0.6; pointer-events:none;'></div>
            <div style='position:relative; z-index:1;'>
                <div style='display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px;'>
                    <div style='display: flex; align-items: center; gap: 12px;'>
                        <span class='result-rank' style='background: {style['chip_bg']}; color: {style['chip_text']};'>
                            {i}
                        </span>
                        <a href='{result['url']}' target='_blank' class='result-title'>
                            {result['title']}
                        </a>
                    </div>
                </div>
                <div style='display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;'>
                    <span class='result-chip' style='background: {style['chip_bg']}; color: {style['chip_text']};'>
                        {style['name']}
                    </span>
                    <span class='result-chip source-chip'>
                        {source_label}
                    </span>
                    <span class='result-chip meta-chip'>
                        {result['word_count']:,} words
                    </span>
                </div>
                <div style='font-size: 0.9em; color: #94a3b8;'>
                    Score: {result['score']:.4f}
                </div>
            </div>
        </div>
        """

    return html

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

with gr.Blocks(title="Superconductor Semantic Search", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <style>
      body, .gradio-container {
          background: linear-gradient(180deg, #020617 0%, #0b1120 100%) !important;
          color: #e2e8f0;
      }

      .gradio-container .gr-block, .gradio-container .gr-panel, .gradio-container .gr-root {
          background: transparent !important;
      }

      .result-card {
          background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.92));
          border-radius: 18px;
          padding: 20px 22px;
          margin-bottom: 18px;
          border: 1px solid rgba(148, 163, 184, 0.25);
          box-shadow: 0 18px 40px rgba(15, 23, 42, 0.45);
          position: relative;
          overflow: hidden;
          color: #e2e8f0;
      }

      .result-rank {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          border-radius: 999px;
          width: 34px;
          height: 34px;
          font-size: 1rem;
          box-shadow: 0 10px 20px rgba(15, 23, 42, 0.35);
      }

      .result-title {
          font-size: 1.2em;
          font-weight: 700;
          color: #f8fafc;
          text-decoration: none;
      }

      .result-title:hover {
          text-decoration: underline;
      }

      .result-chip {
          display: inline-flex;
          align-items: center;
          font-size: 0.85em;
          font-weight: 600;
          padding: 6px 14px;
          border-radius: 999px;
          letter-spacing: 0.01em;
      }

      .source-chip {
          background: rgba(148, 163, 184, 0.18);
          color: #cbd5f5;
          border: 1px solid rgba(148, 163, 184, 0.28);
      }

      .meta-chip {
          color: #cbd5f5;
          background: rgba(148, 163, 184, 0.08);
          border: 1px solid rgba(148, 163, 184, 0.18);
      }

      .gr-markdown, .gr-markdown p, .gr-markdown h3, .gr-markdown li {
          color: #e2e8f0 !important;
      }
    </style>
    """)
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

    query_input.submit(
        fn=perform_search,
        inputs=[query_input, difficulty_dropdown, num_results_slider],
        outputs=results_output
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
