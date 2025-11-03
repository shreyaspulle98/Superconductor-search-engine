---
title: Superconductor Semantic Search
emoji: ⚡
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
tags:
  - sentence-transformers
  - semantic-search
  - physics
  - superconductivity
  - faiss
  - education
---

# ⚡ Superconductor Semantic Search

A semantic search engine for exploring superconductivity research, educational content, and documentation.

## Features

- **1,086 Documents** across multiple sources (Wikipedia, arXiv, MIT OCW, Simple Wikipedia, Scholarpedia, HyperPhysics)
- **Difficulty-Aware Ranking** - Matches query complexity to appropriate content level
- **Title Matching Boost** - Prioritizes documents with relevant titles
- **Semantic Understanding** - Goes beyond keyword matching to understand meaning

## How It Works

1. **Fine-tuned Model**: Based on `sentence-transformers/all-mpnet-base-v2`, fine-tuned on 12,795 superconductivity-specific query-document pairs
2. **FAISS Vector Search**: Fast similarity search using normalized embeddings
3. **Smart Ranking**: Combines semantic similarity with difficulty matching and title relevance

## Usage

1. Enter a question about superconductors
2. Optionally filter by difficulty level (1=Beginner to 5=Cutting-edge)
3. Choose how many results to display (5-20)
4. Get relevant papers, articles, and educational content

## Examples

- **Beginner**: "What is a superconductor?"
- **Intermediate**: "How does the Meissner effect work?"
- **Advanced**: "Explain BCS theory mechanism"
- **Expert**: "room temperature superconductor research"

## Dataset Sources

- **Wikipedia** (97 articles) - General encyclopedia
- **arXiv** (842 papers) - Research preprints
- **MIT OCW** (43 documents) - Lecture notes
- **Simple Wikipedia** (99 articles) - Beginner-friendly
- **Scholarpedia** (1 article) - Peer-reviewed
- **HyperPhysics** (4 pages) - Educational physics

## Technical Details

- **Model**: Fine-tuned all-mpnet-base-v2 (768-dim embeddings)
- **Index**: FAISS IndexFlatIP (cosine similarity)
- **Training**: 4 epochs, CosineSimilarityLoss, batch size 16
- **Hardware**: Trained on Apple M4 (MPS acceleration)

## Links

- [GitHub Repository](https://github.com/shreyaspulle98/superconductor-search)
- [Model on HuggingFace](https://huggingface.co/shreyaspulle98/superconductor-search-v1)

## Citation

If you use this search engine in your research or education, please cite:

```bibtex
@software{superconductor_search_2025,
  title={Superconductor Semantic Search Engine},
  author={Your Name},
  year={2025},
  url={https://huggingface.co/spaces/shreyaspulle98/superconductor-search}
}
```

## License

MIT License - See LICENSE file for details
