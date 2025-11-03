# 🚀 Upload Instructions - Quick Start Guide

This guide provides step-by-step instructions to upload your Superconductor Search project to GitHub and HuggingFace.

---

## 📋 Pre-Upload Checklist

✅ **Cleanup completed:**
- Test files removed
- Log files removed
- `.gitignore` created
- `LICENSE` added

✅ **Files ready:**
- `app.py` (Gradio interface for HuggingFace)
- `web_ui.py` (Flask interface for local use)
- `requirements.txt` (all dependencies)
- `requirements-gradio.txt` (HuggingFace Spaces)
- `README.md` (updated with badges and links)
- `DEPLOYMENT_GUIDE.md` (detailed instructions)

✅ **Project structure:**
```
superconductor-search/
├── Data collection (8 scraper scripts)
├── Training & indexing (3 scripts)
├── Web interfaces (2 files: Flask + Gradio)
├── Search index (data/search_index/)
├── Trained model (models/superconductor-search-v1/)
└── Documentation (5 markdown files)
```

✅ **Sizes:**
- Total project: 1.8 GB
- Model: 419 MB
- Data: 433 MB
- Search index: 4.5 MB

---

## Part 1: Upload to GitHub (15 minutes)

### Step 1: Personalize Your README

Before uploading, replace placeholder text in files:

1. Open `README.md`
2. Replace all instances of `shreyaspulle98` with your GitHub/HuggingFace username
3. Do the same in:
   - `DEPLOYMENT_GUIDE.md`
   - `HUGGINGFACE_README.md`
   - `app.py` (line ~35)

### Step 2: Initialize Git Repository

```bash
cd "/Users/shrey/Semantic Search Project/superconductor-search"

# Initialize git
git init

# Add all files
git add .

# Check what will be committed (should NOT include venv, logs, cache)
git status

# Create first commit
git commit -m "Initial commit: Superconductor semantic search engine

- 1,086 documents from 6 sources
- Fine-tuned sentence-transformers model
- Flask web UI and Gradio app
- Complete documentation"
```

### Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: **`superconductor-search`**
3. Description: **`Semantic search engine for superconductivity research and educational content`**
4. Visibility: **Public** (recommended for HuggingFace integration)
5. **DO NOT** check "Initialize with README" (we have one)
6. Click **"Create repository"**

### Step 4: Push to GitHub

```bash
# Add GitHub as remote (replace shreyaspulle98)
git remote add origin https://github.com/shreyaspulle98/superconductor-search.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**⚠️ Expected Warning**: Large files may trigger warnings. This is normal.

### Step 5: Handle Large Files (Optional)

GitHub has a 100 MB file limit. Your model files are >100MB each.

**Option A: Use Git LFS** (Recommended if you want model in GitHub)

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "models/**/*.safetensors"
git lfs track "models/**/*.bin"
git lfs track "data/**/*.bin"

# Add .gitattributes
git add .gitattributes

# Commit and push
git commit -m "Add Git LFS tracking for large files"
git push
```

**Option B: Exclude large files from GitHub** (Recommended - host model on HuggingFace only)

Add to `.gitignore`:
```
models/
data/raw/
data/processed/
```

Then:
```bash
git rm --cached -r models/ data/raw/ data/processed/
git commit -m "Remove large files - will host on HuggingFace"
git push
```

**Recommendation**: Use Option B. Host the model on HuggingFace Hub (free unlimited storage) and download it from there.

### Step 6: Verify GitHub Upload

Visit: `https://github.com/shreyaspulle98/superconductor-search`

Check:
- ✅ README displays correctly
- ✅ All code files present
- ✅ License visible
- ✅ No venv or cache files

---

## Part 2: Upload Model to HuggingFace (10 minutes)

### Step 1: Install HuggingFace CLI

```bash
# Activate virtual environment
source venv/bin/activate

# Install HuggingFace Hub
pip install huggingface_hub

# Login (you'll need a HuggingFace account)
huggingface-cli login
# Paste your access token when prompted
# Get token from: https://huggingface.co/settings/tokens
```

### Step 2: Create Model Repository

```bash
# Create model repository (replace shreyaspulle98)
huggingface-cli repo create superconductor-search-v1 --type model --org shreyaspulle98

# Should show: "Your repo has been created!"
```

### Step 3: Upload Model Files

```bash
cd "/Users/shrey/Semantic Search Project/superconductor-search"

# Upload entire model directory
huggingface-cli upload shreyaspulle98/superconductor-search-v1 \
  models/superconductor-search-v1 \
  --repo-type model

# This will take 5-10 minutes (419 MB upload)
```

### Step 4: Create Model Card

1. Go to: `https://huggingface.co/shreyaspulle98/superconductor-search-v1`
2. Click **"Edit model card"**
3. Copy content from `HUGGINGFACE_README.md` (the model card section)
4. Add tags: `sentence-transformers`, `semantic-search`, `physics`, `superconductivity`
5. Set license: **MIT**
6. Click **"Commit changes to main"**

### Step 5: Test Model Download

```python
from sentence_transformers import SentenceTransformer

# Should download from HuggingFace and work
model = SentenceTransformer('shreyaspulle98/superconductor-search-v1')
embedding = model.encode("test query")
print(embedding.shape)  # Should output: (768,)
```

---

## Part 3: Deploy to HuggingFace Spaces (15 minutes)

### Step 1: Create Space

1. Go to https://huggingface.co/new-space
2. Space name: **`superconductor-search`**
3. License: **MIT**
4. SDK: **Gradio**
5. Hardware: **CPU basic - Free**
6. Visibility: **Public**
7. Click **"Create Space"**

### Step 2: Clone Space Repository

```bash
# Clone your new space
cd ~/Desktop  # or wherever you want to work
git clone https://huggingface.co/spaces/shreyaspulle98/superconductor-search
cd superconductor-search
```

### Step 3: Copy Files to Space

```bash
# Copy main files
cp "/Users/shrey/Semantic Search Project/superconductor-search/app.py" .
cp "/Users/shrey/Semantic Search Project/superconductor-search/requirements-gradio.txt" requirements.txt
cp "/Users/shrey/Semantic Search Project/superconductor-search/HUGGINGFACE_README.md" README.md

# Copy search index (CRITICAL!)
mkdir -p data/search_index
cp "/Users/shrey/Semantic Search Project/superconductor-search/data/search_index/"* data/search_index/

# Verify files
ls -lh
ls -lh data/search_index/
```

### Step 4: Update Model Path in app.py

Open `app.py` and find line ~35:

```python
# Change this:
model_path = "sentence-transformers/all-mpnet-base-v2"  # Replace with your HF model

# To this (use YOUR username):
model_path = "shreyaspulle98/superconductor-search-v1"
```

Save the file.

### Step 5: Push to HuggingFace Spaces

```bash
# Add all files
git add .

# Commit
git commit -m "Initial deployment of Superconductor Search

- Gradio interface
- FAISS search index
- 1,086 documents indexed
- Fine-tuned sentence-transformers model"

# Push to HuggingFace
git push
```

### Step 6: Wait for Build

1. Go to: `https://huggingface.co/spaces/shreyaspulle98/superconductor-search`
2. Click **"Logs"** tab to watch build progress
3. Build takes ~2-5 minutes
4. When you see "Running on public URL", it's live!

### Step 7: Test Your Space

1. Go to: `https://huggingface.co/spaces/shreyaspulle98/superconductor-search`
2. Try example queries:
   - "What is a superconductor?"
   - "room temperature superconductor"
   - "BCS theory"
3. Verify results appear correctly
4. Check that links work

---

## Part 4: Final Touches (5 minutes)

### Update Links

Now that everything is live, update the placeholder links:

1. **In GitHub repository**:
   ```bash
   cd "/Users/shrey/Semantic Search Project/superconductor-search"

   # Edit README.md - replace shreyaspulle98 with actual username
   # Edit other markdown files with placeholders

   git add .
   git commit -m "Update links to live deployments"
   git push
   ```

2. **In HuggingFace Space**:
   - Edit README.md to include GitHub link
   - Commit changes

### Add Repository Topics (GitHub)

1. Go to your GitHub repo
2. Click ⚙️ (Settings) or edit About section
3. Add topics:
   - `semantic-search`
   - `machine-learning`
   - `physics`
   - `superconductivity`
   - `sentence-transformers`
   - `faiss`
   - `python`
   - `flask`
   - `gradio`

### Add to Collections (HuggingFace)

1. Browse HuggingFace collections
2. Add your Space to relevant collections:
   - Search collections
   - Physics/Science collections
   - Educational tools

---

## 🎉 You're Done!

Your project is now live at:

- **GitHub**: `https://github.com/shreyaspulle98/superconductor-search`
- **Model**: `https://huggingface.co/shreyaspulle98/superconductor-search-v1`
- **Demo**: `https://huggingface.co/spaces/shreyaspulle98/superconductor-search`

---

## 📊 Quick Verification Checklist

Before sharing publicly, verify:

- [ ] GitHub repository is public and README displays
- [ ] HuggingFace model page has proper model card
- [ ] HuggingFace Space is running (not in "Building" state)
- [ ] Example queries work in Space demo
- [ ] All links in README point to correct URLs
- [ ] License file is present
- [ ] No sensitive information in code (API keys, passwords)
- [ ] Requirements.txt is complete

---

## 🐛 Common Issues & Solutions

### GitHub Push Fails

**Error**: "Large files detected"
**Solution**: Use Git LFS or exclude large files (see Step 5 above)

**Error**: "Authentication failed"
**Solution**: Use Personal Access Token instead of password:
1. GitHub Settings → Developer Settings → Personal Access Tokens
2. Generate new token (classic) with `repo` scope
3. Use token as password

### HuggingFace Model Upload Fails

**Error**: "Repository not found"
**Solution**: Create repository first with `huggingface-cli repo create`

**Error**: "Unauthorized"
**Solution**: Run `huggingface-cli login` and enter valid token

### HuggingFace Space Build Fails

**Error**: "FileNotFoundError: data/search_index/faiss_index.bin"
**Solution**: Make sure you copied the entire `data/search_index/` folder

**Error**: "ModuleNotFoundError"
**Solution**: Check that `requirements.txt` includes all dependencies

**Error**: Space runs but no results
**Solution**: Check that model path in `app.py` points to your HuggingFace model

---

## 📞 Getting Help

If you encounter issues:

1. **GitHub**: Check [GitHub Docs](https://docs.github.com/)
2. **HuggingFace**: Check [HF Documentation](https://huggingface.co/docs)
3. **Community**: Post on [HF Forums](https://discuss.huggingface.co/)

For project-specific issues, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

---

## 🎯 Next Steps After Deployment

1. **Share your work**:
   - Post on Twitter/X with #MachineLearning #Physics
   - Share on r/MachineLearning, r/Physics
   - Add to your portfolio/resume

2. **Gather feedback**:
   - Share with physics students/professors
   - Post in physics education forums
   - Monitor Space analytics

3. **Iterate and improve**:
   - Add more data sources (see DATA_SOURCE_RECOMMENDATIONS.md)
   - Retrain with user feedback
   - Add new features based on user requests

4. **Maintain**:
   - Update dependencies periodically
   - Monitor for bugs/issues
   - Keep model up to date with new research

---

**Good luck! 🚀**

If you successfully deploy this project, consider:
- ⭐ Starring the base model on HuggingFace
- 📝 Writing a blog post about your process
- 🎓 Sharing with educational communities
- 💬 Contributing back to open source
