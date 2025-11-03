# ⚡ Superconductor Semantic Search

A semantic search engine for superconductivity research, powered by fine-tuned sentence transformers and FAISS vector search.

[![HuggingFace Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/shreyaspulle98/superconductor-search)
[![Model](https://img.shields.io/badge/🤗%20Hugging%20Face-Model-orange)](https://huggingface.co/shreyaspulle98/superconductor-search-v1)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Try It Now

**[Live Demo on HuggingFace Spaces →](https://huggingface.co/spaces/shreyaspulle98/superconductor-search)**

## System Overview

**Total indexed:** 1,086 documents from 6 sources
**Model:** Fine-tuned sentence-transformers/all-mpnet-base-v2
**Training pairs:** 12,795 (26.3% positive, 73.7% negative)
**Search index:** FAISS with 768-dimensional embeddings

## Quick Start

### 1. Start the Web Interface
```bash
source venv/bin/activate
python3 web_ui.py
```
Access at: http://localhost:8080

### 2. Interactive CLI Search
```bash
source venv/bin/activate
python3 interactive_search.py
```

### 3. Test the System
```bash
source venv/bin/activate
python3 04_test_search.py
```

## Project Structure

```
superconductor-search/
│
├── Core Production System
│   ├── web_ui.py                  # Flask web interface
│   ├── interactive_search.py      # CLI search tool
│   ├── 02.train_model.py          # Model training script
│   ├── 03_build_search_index.py   # Index building script
│   └── 04_test_search.py          # Testing script
│
├── Data Collection Scripts
│   ├── 0.1_superconductor_scraper.py      # Wikipedia scraper
│   ├── 0.1b_simple_wikipedia_scraper.py   # Simple Wikipedia scraper
│   ├── 0.2_mit_OCW_scraper.py             # MIT OCW scraper
│   ├── 0.3_youtube_maximiser_scraper.py   # YouTube transcript scraper
│   ├── 0.4_merge_datasets.py              # Dataset merger
│   ├── 0.5_arxiv_full_papers.py           # arXiv paper scraper
│   ├── 0.6_scholarpedia_scraper.py        # Scholarpedia scraper
│   └── 0.7_hyperphysics_scraper.py        # HyperPhysics scraper
│
├── Data & Models
│   ├── data/
│   │   ├── processed/
│   │   │   ├── merged_all_20251103_124240.json  # Current dataset (1,086 docs)
│   │   │   ├── training_pairs.json              # Training pairs (12,795)
│   │   │   └── queries_with_labels.json         # Labeled queries
│   │   └── search_index/
│   │       ├── faiss_index.bin                  # FAISS vector index
│   │       ├── documents.json                   # Document metadata
│   │       └── index_metadata.json              # Index metadata
│   │
│   └── models/
│       └── superconductor-search-v1/            # Fine-tuned model (418MB)
│
├── Web UI
│   └── templates/
│       └── index.html                           # Web interface template
│
├── Configuration
│   ├── requirements.txt                         # Python dependencies
│   └── .env                                     # Environment variables
│
└── Documentation
    ├── README.md                                # This file
    ├── WEB_UI_GUIDE.md                          # Web UI documentation
    └── EVALUATION_GUIDE.md                      # Evaluation documentation
```

## Data Sources

| Source | Documents | Difficulty Levels | Description |
|--------|-----------|-------------------|-------------|
| **arXiv** | 842 | Level 4 (Expert) | Research papers |
| **Simple Wikipedia** | 99 | Level 1 (Beginner) | Beginner-friendly articles |
| **Wikipedia** | 97 | Levels 1-3 | General articles |
| **MIT OCW** | 43 | Levels 2-3 | Course materials |
| **HyperPhysics** | 4 | Level 2 | Physics explanations |
| **Scholarpedia** | 1 | Level 3 | Academic articles |

## Model Training Details

**Training Date:** November 3, 2025
**Model Base:** sentence-transformers/all-mpnet-base-v2
**Training Pairs:** 12,795
- Positive pairs (similar): 3,364 (26.3%)
- Negative pairs (dissimilar): 9,431 (73.7%)

**Training Configuration:**
- Epochs: 4
- Batch size: 16
- Loss function: CosineSimilarityLoss
- Device: Apple M4 MPS (GPU acceleration)
- Training time: ~30 minutes

**Model Size:** 418MB
**Embedding Dimension:** 768

## Search Features

### Semantic Search
- Natural language queries
- Difficulty-aware ranking
- Multi-source retrieval
- Top-k results with relevance scores

### Difficulty Levels
1. **Beginner** - Simple Wikipedia content
2. **Intermediate** - Wikipedia, HyperPhysics
3. **Advanced** - Academic content
4. **Expert** - arXiv research papers

### Query Types Supported
- Beginner: "What is a superconductor?"
- Intermediate: "Explain Type I and Type II superconductors"
- Advanced: "BCS theory ground state wavefunction"
- Expert: "Topological superconductivity applications"

## Maintenance Tasks

### Retrain the Model
```bash
source venv/bin/activate
python3 02.train_model.py
```

### Rebuild the Search Index
```bash
source venv/bin/activate
python3 03_build_search_index.py
```

### Add New Data Sources
1. Create a new scraper script following the pattern in `0.X_*_scraper.py`
2. Run the scraper to collect data
3. Merge datasets using `0.4_merge_datasets.py`
4. Retrain the model with new data
5. Rebuild the search index

### Update Training Pairs
Edit `data/processed/training_pairs.json` and retrain the model.

## Performance

**Search Speed:**
- Query encoding: <100ms
- FAISS search: <10ms (for top-10 results)
- Total response time: <200ms

**Index Size:** 3.2MB (FAISS index)
**Memory Usage:** ~500MB (loaded model + index)

## System Requirements

- Python 3.9+
- 2GB RAM minimum (4GB recommended)
- Apple Silicon (M1/M2/M3/M4) for MPS acceleration (optional)
- 2GB disk space

## Dependencies

Key packages:
- `sentence-transformers` - Embedding model
- `faiss-cpu` - Vector search
- `flask` - Web interface
- `torch` - Deep learning framework
- `numpy`, `pandas` - Data processing

See `requirements.txt` for complete list.

## Web Interface Features

- **Search bar** with real-time results
- **Difficulty filter** for targeted results
- **Color-coded results** by difficulty level
- **Source attribution** for each result
- **Direct links** to original documents
- **Responsive design** for mobile/desktop

## API Endpoints

### Search
```
POST /api/search
Body: {"query": "your query", "difficulty_filter": optional_level}
```

### Statistics
```
GET /api/stats
Returns: Document counts, sources, difficulty breakdown
```

## Troubleshooting

### Web UI won't start
- Check if port 8080 is available
- Verify virtual environment is activated
- Ensure all dependencies are installed

### Search returns no results
- Verify search index exists in `data/search_index/`
- Rebuild index if necessary: `python3 03_build_search_index.py`

### Training fails
- Check available disk space (need ~1GB free)
- Verify training pairs file exists
- Ensure GPU/MPS is available for acceleration

## 📦 Deployment

### GitHub Repository
- Code: [github.com/shreyaspulle98/superconductor-search](https://github.com/shreyaspulle98/superconductor-search)

### HuggingFace
- Model: [huggingface.co/shreyaspulle98/superconductor-search-v1](https://huggingface.co/shreyaspulle98/superconductor-search-v1)
- Demo: [huggingface.co/spaces/shreyaspulle98/superconductor-search](https://huggingface.co/spaces/shreyaspulle98/superconductor-search)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## 📚 Additional Resources

- [DATA_SOURCE_RECOMMENDATIONS.md](DATA_SOURCE_RECOMMENDATIONS.md) - Guide for adding more data sources
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment instructions for GitHub and HuggingFace

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Base model: [sentence-transformers/all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
- Vector search: [FAISS by Facebook Research](https://github.com/facebookresearch/faiss)
- Data sources: Wikipedia, arXiv, MIT OCW, Simple Wikipedia, Scholarpedia, HyperPhysics

## 📧 Contact

For issues or questions, please open an issue on [GitHub](https://github.com/shreyaspulle98/superconductor-search/issues).

---

**Last Updated:** November 3, 2025
**Version:** 1.0
**Made with ❤️ for physics education and research**
