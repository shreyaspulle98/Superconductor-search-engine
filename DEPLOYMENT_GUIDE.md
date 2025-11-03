# Deployment Guide

Complete guide for deploying the Superconductor Semantic Search to GitHub and HuggingFace.

---

## Table of Contents

1. [GitHub Deployment](#github-deployment)
2. [HuggingFace Model Upload](#huggingface-model-upload)
3. [HuggingFace Spaces Deployment](#huggingface-spaces-deployment)
4. [Local Development](#local-development)
5. [Troubleshooting](#troubleshooting)

---

## GitHub Deployment

### Step 1: Initialize Git Repository

```bash
cd "/Users/shrey/Semantic Search Project/superconductor-search"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Superconductor semantic search engine"
```

### Step 2: Create GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the **"+"** icon → **"New repository"**
3. Repository name: `superconductor-search`
4. Description: `Semantic search engine for superconductivity research and educational content`
5. Choose **Public** (for HuggingFace integration) or **Private**
6. **DO NOT** initialize with README (we already have one)
7. Click **"Create repository"**

### Step 3: Push to GitHub

```bash
# Add remote (replace shreyaspulle98 with your GitHub username)
git remote add origin https://github.com/shreyaspulle98/superconductor-search.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Verify

Go to `https://github.com/shreyaspulle98/superconductor-search` and verify all files are there.

### What Gets Uploaded:

✅ **Included**:
- All Python scripts (scrapers, training, search)
- `web_ui.py` (Flask application)
- `app.py` (Gradio application for HuggingFace)
- `requirements.txt`
- `README.md`, `DATA_SOURCE_RECOMMENDATIONS.md`, `DEPLOYMENT_GUIDE.md`
- `.gitignore`

❌ **Excluded** (via .gitignore):
- `venv/` (virtual environment)
- `checkpoints/` (training checkpoints)
- `__pycache__/` (Python cache)
- `*.log` (log files)

⚠️ **Large Files** (consider Git LFS or separate hosting):
- `data/raw/` (372 MB) - Raw scraped data
- `data/processed/` (56 MB) - Processed datasets
- `data/search_index/` (4.5 MB) - FAISS index
- `models/superconductor-search-v1/` (419 MB) - Trained model

### Optional: Use Git LFS for Large Files

If you want to include large files in GitHub:

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "models/**/*.safetensors"
git lfs track "models/**/*.bin"
git lfs track "data/search_index/*.bin"

# Add .gitattributes
git add .gitattributes

# Push LFS files
git add models/ data/search_index/
git commit -m "Add model and search index with Git LFS"
git push
```

**Note**: GitHub LFS has storage limits on free accounts (1 GB storage, 1 GB bandwidth/month).

---

## HuggingFace Model Upload

### Step 1: Create HuggingFace Account

1. Go to [huggingface.co](https://huggingface.co/join)
2. Create an account if you don't have one
3. Go to Settings → Access Tokens → Create new token
4. Copy the token (you'll need it below)

### Step 2: Install HuggingFace CLI

```bash
# Activate your virtual environment
source venv/bin/activate

# Install Hugging Face Hub
pip install huggingface_hub

# Login
huggingface-cli login
# Paste your token when prompted
```

### Step 3: Upload Model

```bash
cd "/Users/shrey/Semantic Search Project/superconductor-search"

# Create repository on HuggingFace (replace shreyaspulle98)
huggingface-cli repo create superconductor-search-v1 --type model

# Upload model files
huggingface-cli upload shreyaspulle98/superconductor-search-v1 \
  models/superconductor-search-v1 \
  --repo-type model
```

### Step 4: Create Model Card

Create a README on HuggingFace model page with this content:

````markdown
---
language: en
license: mit
tags:
  - sentence-transformers
  - semantic-search
  - physics
  - superconductivity
  - feature-extraction
library_name: sentence-transformers
base_model: sentence-transformers/all-mpnet-base-v2
datasets:
  - custom
pipeline_tag: sentence-similarity
---

# Superconductor Search v1

Fine-tuned sentence-transformers model for semantic search over superconductivity research and educational content.

## Model Details

- **Base Model**: sentence-transformers/all-mpnet-base-v2
- **Fine-tuning Data**: 12,795 query-document pairs from superconductivity domain
- **Training**: 4 epochs with CosineSimilarityLoss
- **Embedding Dimension**: 768
- **Use Case**: Semantic search for scientific literature

## Training Data

- **Positive pairs**: 3,382 (26.4%)
- **Negative pairs**: 9,413 (73.6%)
- **Sources**: Wikipedia, arXiv, MIT OCW, Simple Wikipedia

## Usage

```python
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('shreyaspulle98/superconductor-search-v1')

# Encode queries and documents
query_embedding = model.encode("What is a superconductor?")
doc_embedding = model.encode("Superconductors are materials that conduct...")

# Compute similarity
from sentence_transformers.util import cos_sim
similarity = cos_sim(query_embedding, doc_embedding)
```

## Performance

Optimized for:
- Query-to-document retrieval
- Cross-encoder style semantic similarity
- Domain-specific (superconductivity) content

## Citation

```bibtex
@software{superconductor_search_v1_2025,
  title={Superconductor Search Model v1},
  author={Your Name},
  year={2025},
  url={https://huggingface.co/shreyaspulle98/superconductor-search-v1}
}
```
````

---

## HuggingFace Spaces Deployment

### Step 1: Create Space

1. Go to [huggingface.co](https://huggingface.co)
2. Click your profile → **"New Space"**
3. Space name: `superconductor-search`
4. License: MIT
5. SDK: **Gradio**
6. Hardware: **CPU basic** (free tier)
7. Click **"Create Space"**

### Step 2: Upload Files to Space

You have two options:

#### Option A: Using Git (Recommended)

```bash
# Clone the Space
git clone https://huggingface.co/spaces/shreyaspulle98/superconductor-search
cd superconductor-search

# Copy files from your project
cp "/Users/shrey/Semantic Search Project/superconductor-search/app.py" .
cp "/Users/shrey/Semantic Search Project/superconductor-search/requirements.txt" .
cp "/Users/shrey/Semantic Search Project/superconductor-search/HUGGINGFACE_README.md" README.md

# Copy search index and documents (IMPORTANT!)
mkdir -p data/search_index
cp "/Users/shrey/Semantic Search Project/superconductor-search/data/search_index/"* data/search_index/

# Add and commit
git add .
git commit -m "Add Gradio app and search index"
git push
```

#### Option B: Using HuggingFace Web Interface

1. Go to your Space: `https://huggingface.co/spaces/shreyaspulle98/superconductor-search`
2. Click **"Files"** tab → **"Add file"** → **"Upload files"**
3. Upload:
   - `app.py`
   - `requirements.txt`
   - Rename `HUGGINGFACE_README.md` → `README.md`
4. Create folder `data/search_index/` and upload:
   - `faiss_index.bin`
   - `documents.json`
   - `index_metadata.json`

### Step 3: Update Requirements for Gradio

Make sure your `requirements.txt` includes Gradio:

```txt
# Add to requirements.txt
gradio>=4.0.0
```

### Step 4: Update Model Path in app.py

In `app.py`, update the model loading to use your HuggingFace model:

```python
# Replace this line in app.py:
model_path = "sentence-transformers/all-mpnet-base-v2"  # Replace with your HF model

# With:
model_path = "shreyaspulle98/superconductor-search-v1"
```

### Step 5: Wait for Build

HuggingFace will automatically build your Space. Check the **"Logs"** tab to see progress.

Build time: ~2-5 minutes

### Step 6: Test Your Space

Go to: `https://huggingface.co/spaces/shreyaspulle98/superconductor-search`

Test queries:
- "What is a superconductor?"
- "room temperature superconductor"
- "BCS theory"

---

## File Size Considerations

### Current File Sizes:
- Model: **419 MB** (models/superconductor-search-v1/)
- FAISS Index: **3.2 MB** (data/search_index/faiss_index.bin)
- Documents: **278 KB** (data/search_index/documents.json)
- Total needed for Spaces: **~423 MB**

### HuggingFace Spaces Limits:
- **Free tier**: 5 GB storage
- **Pro tier**: 50 GB storage

✅ Your app fits comfortably in the free tier!

### Optimization Tips:

If you need to reduce size:

1. **Model**: Already efficiently stored in `safetensors` format
2. **FAISS Index**: Can use Product Quantization (PQ) to reduce:
   ```python
   # In 03_build_search_index.py, replace IndexFlatIP with:
   quantizer = faiss.IndexFlatIP(dim)
   index = faiss.IndexIVFPQ(quantizer, dim, nlist=100, m=8, nbits=8)
   # Reduces size by ~75% with minimal quality loss
   ```
3. **Documents**: Already minimal (JSON format)

---

## Local Development

### Running Flask UI Locally

```bash
cd "/Users/shrey/Semantic Search Project/superconductor-search"
source venv/bin/activate
python web_ui.py
```

Visit: http://localhost:8080

### Running Gradio UI Locally

```bash
cd "/Users/shrey/Semantic Search Project/superconductor-search"
source venv/bin/activate
pip install gradio
python app.py
```

Visit: http://localhost:7860

### Testing Search Index

```bash
python 04_test_search.py
```

---

## Troubleshooting

### GitHub Issues

**Problem**: "remote: error: File is too large"
**Solution**: Use Git LFS (see GitHub deployment section)

**Problem**: Push fails with authentication error
**Solution**: Use a Personal Access Token instead of password:
1. Go to GitHub Settings → Developer Settings → Personal Access Tokens
2. Generate new token with `repo` scope
3. Use token as password when pushing

### HuggingFace Model Upload Issues

**Problem**: "Repository not found"
**Solution**: Make sure you created the model repository first:
```bash
huggingface-cli repo create superconductor-search-v1 --type model
```

**Problem**: "Authentication error"
**Solution**: Login again:
```bash
huggingface-cli login
```

### HuggingFace Spaces Issues

**Problem**: Space build fails with "Module not found"
**Solution**: Make sure all dependencies are in `requirements.txt`

**Problem**: "File not found: data/search_index/faiss_index.bin"
**Solution**: Ensure you uploaded the entire `data/search_index/` folder to your Space

**Problem**: Space runs out of memory
**Solution**:
1. Use smaller batch sizes in search
2. Upgrade to CPU Upgrade hardware (small fee)
3. Consider model quantization

**Problem**: Model loading is slow
**Solution**: Model is cached after first load. First request takes ~30 seconds, subsequent requests are fast.

---

## Post-Deployment Checklist

### GitHub:
- [ ] Repository created and public
- [ ] All code files pushed
- [ ] README displays correctly
- [ ] .gitignore working (no venv, cache files)
- [ ] Repository description and topics added

### HuggingFace Model:
- [ ] Model uploaded successfully
- [ ] Model card (README) filled out
- [ ] Model tags added
- [ ] License specified
- [ ] Example usage code tested

### HuggingFace Spaces:
- [ ] Space created and running
- [ ] Gradio interface loads
- [ ] Search returns results
- [ ] Example queries work
- [ ] README displays correctly
- [ ] Space is public/discoverable

### Links to Update:
- [ ] Update GitHub URL in README
- [ ] Update HuggingFace model URL in app.py
- [ ] Update HuggingFace Space URL in README
- [ ] Update model path in app.py to use HF model
- [ ] Add badges to README (optional)

---

## Optional Enhancements

### Add Badges to README

```markdown
[![HuggingFace Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/shreyaspulle98/superconductor-search)
[![Model](https://img.shields.io/badge/🤗%20Hugging%20Face-Model-orange)](https://huggingface.co/shreyaspulle98/superconductor-search-v1)
[![GitHub](https://img.shields.io/github/stars/shreyaspulle98/superconductor-search?style=social)](https://github.com/shreyaspulle98/superconductor-search)
```

### Enable Gradio Analytics

In `app.py`, add analytics:

```python
demo.launch(analytics_enabled=True)
```

### Add Custom Domain (Pro only)

If you have HuggingFace Pro, you can add a custom domain:
1. Go to Space Settings
2. Add custom domain
3. Update DNS records

---

## Costs

### Free Tier:
- **GitHub**: Free for public repositories (with 1 GB Git LFS)
- **HuggingFace Models**: Free unlimited storage
- **HuggingFace Spaces**: Free CPU basic (permanent uptime)

### Paid Options:
- **GitHub Pro**: $4/month (includes 50 GB Git LFS)
- **HuggingFace Pro**: $9/month (includes GPU spaces, custom domains)
- **HuggingFace Spaces Upgrade**: $0.60/hour for GPU

**Recommendation**: Start with free tier. It's more than sufficient for this project!

---

## Support

If you encounter issues:

1. **GitHub**: Check [GitHub Docs](https://docs.github.com/)
2. **HuggingFace**: Check [HF Docs](https://huggingface.co/docs) or [Forum](https://discuss.huggingface.co/)
3. **Gradio**: Check [Gradio Docs](https://www.gradio.app/docs/)

---

## Next Steps

After successful deployment:

1. **Share your Space** on social media, Reddit, physics forums
2. **Add to HuggingFace** collections (search for "physics" or "education")
3. **Gather feedback** and iterate
4. **Add more data sources** (see DATA_SOURCE_RECOMMENDATIONS.md)
5. **Retrain model** with new data and update deployment

Good luck! 🚀
