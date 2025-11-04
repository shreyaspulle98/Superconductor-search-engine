#!/bin/bash

# Project Cleanup Script
# ======================
# Moves old/unnecessary files to archive while keeping essential code

echo "======================================================================"
echo "🧹 PROJECT CLEANUP"
echo "======================================================================"

# Create archive structure
mkdir -p archive/old_scripts
mkdir -p archive/old_docs
mkdir -p archive/logs

echo ""
echo "📁 Moving old/redundant files to archive..."

# Move old training/testing scripts (replaced by v2 versions)
mv 02.train_model.py archive/old_scripts/ 2>/dev/null
mv 03_build_search_index.py archive/old_scripts/ 2>/dev/null
mv 04_test_search.py archive/old_scripts/ 2>/dev/null

# Move old documentation (superseded)
mv DATA_SOURCE_RECOMMENDATIONS.md archive/old_docs/ 2>/dev/null
mv HOW_TO_USE_QUERY_GENERATOR.md archive/old_docs/ 2>/dev/null
mv MODEL_ANALYSIS_AND_IMPROVEMENT_PLAN.md archive/old_docs/ 2>/dev/null
mv SAMPLE_QUERIES_MANUAL.md archive/old_docs/ 2>/dev/null
mv UPLOAD_INSTRUCTIONS.md archive/old_docs/ 2>/dev/null

# Move temporary/helper scripts to archive
mv fetch_all_transcripts.py archive/old_scripts/ 2>/dev/null
mv fetch_youtube_titles.py archive/old_scripts/ 2>/dev/null
mv fetch_youtube_transcripts.py archive/old_scripts/ 2>/dev/null
mv format_youtube_documents.py archive/old_scripts/ 2>/dev/null
mv scripts/merge_data.py archive/old_scripts/ 2>/dev/null 2>/dev/null

# Move logs
mv youtube_scraper.log archive/logs/ 2>/dev/null
mv youtube_video_ids.txt archive/logs/ 2>/dev/null

# Remove old web UI (will create new one for HuggingFace)
mv web_ui.py archive/old_scripts/ 2>/dev/null

echo "   ✅ Moved old files to archive"

echo ""
echo "📊 Final Project Structure:"
echo ""
echo "Essential Scripts:"
echo "├── Data Collection (0.x_*.py)"
echo "│   ├── 0.1_superconductor_scraper.py      (Wikipedia scraper)"
echo "│   ├── 0.1b_simple_wikipedia_scraper.py   (Simple Wikipedia)"
echo "│   ├── 0.2_mit_OCW_scraper.py             (MIT OCW)"
echo "│   ├── 0.3_youtube_maximiser_scraper.py   (YouTube scraper)"
echo "│   ├── 0.4_merge_datasets.py              (Dataset merger)"
echo "│   ├── 0.5_arxiv_full_papers.py           (arXiv papers)"
echo "│   ├── 0.6_scholarpedia_scraper.py        (Scholarpedia)"
echo "│   └── 0.7_hyperphysics_scraper.py        (HyperPhysics)"
echo "│"
echo "├── Data Quality Pipeline"
echo "│   ├── generate_queries_llm.py            (Query generation)"
echo "│   ├── create_hard_negatives.py           (Hard negatives)"
echo "│   ├── fix_weak_positive_pairings.py      (Weak pairing removal)"
echo "│   ├── deep_quality_check.py              (Deep quality analysis)"
echo "│   ├── final_cleanup.py                   (Final cleanup)"
echo "│   └── prepare_for_training.py            (Training preparation)"
echo "│"
echo "├── Model Training & Testing"
echo "│   ├── train_model_v2.py                  (Training script)"
echo "│   ├── build_search_index.py              (Index builder)"
echo "│   ├── test_search_model.py               (Comprehensive tests)"
echo "│   └── interactive_search.py              (Interactive search CLI)"
echo "│"
echo "└── Deployment"
echo "    └── app.py                             (Gradio web interface)"
echo ""
echo "Data:"
echo "├── training/                              (Production training data)"
echo "│   ├── training_dataset.json             (4,546 examples)"
echo "│   ├── documents.json                     (1,762 documents)"
echo "│   └── training_metadata.json             (Metadata)"
echo "│"
echo "├── search_index/                          (Production search index)"
echo "│   ├── faiss_index.bin                    (FAISS index)"
echo "│   ├── document_metadata.json             (Metadata)"
echo "│   └── index_info.json                    (Index info)"
echo "│"
echo "├── models/                                (Trained models)"
echo "│   └── superconductor-search-v2/          (Latest model)"
echo "│"
echo "├── data/                                  (Processed/raw data)"
echo "│   ├── processed/                         (Final datasets)"
echo "│   └── raw/                               (Source data)"
echo "│"
echo "└── archive/                               (Old/intermediate files)"
echo ""

echo "======================================================================"
echo "✅ CLEANUP COMPLETE!"
echo "======================================================================"
echo ""
echo "Essential files kept:"
echo "   🔧 All data collection scripts (0.x)"
echo "   📊 Data quality pipeline scripts"
echo "   🤖 Training and testing scripts (v2)"
echo "   🚀 Deployment files (app.py)"
echo "   📚 Production data (training/, search_index/, models/)"
echo "   📝 Documentation (README.md, summaries)"
echo ""
echo "Archived:"
echo "   📦 Old scripts (archive/old_scripts/)"
echo "   📄 Old documentation (archive/old_docs/)"
echo "   📋 Logs (archive/logs/)"
echo ""
echo "======================================================================"
