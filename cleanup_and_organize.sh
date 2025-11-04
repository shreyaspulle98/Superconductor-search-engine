#!/bin/bash

# Cleanup and Organize Project
# =============================
# Moves intermediate files to archive and keeps only essential files

echo "======================================================================"
echo "🧹 Cleanup and Organization Script"
echo "======================================================================"

# Create archive directory
mkdir -p archive/intermediate_data
mkdir -p archive/old_queries
mkdir -p archive/old_documents

echo ""
echo "📁 Moving intermediate files to archive..."

# Move old query files
mv data/processed/queries_with_hard_negatives_20251104_224640.json archive/intermediate_data/ 2>/dev/null
mv data/processed/queries_strong_positives_20251104_225742.json archive/intermediate_data/ 2>/dev/null
mv data/processed/queries_highest_quality_20251104_230133.json archive/intermediate_data/ 2>/dev/null
mv data/processed/FINAL_ALL_IMPROVED_queries_20251104_223630.json archive/old_queries/ 2>/dev/null
mv data/processed/arxiv_queries_IMPROVED.json archive/old_queries/ 2>/dev/null
mv data/processed/youtube_queries_IMPROVED.json archive/old_queries/ 2>/dev/null
mv data/processed/youtube_queries_complete.json archive/old_queries/ 2>/dev/null
mv data/processed/youtube_queries_manual.json archive/old_queries/ 2>/dev/null
mv data/processed/manual_queries_comprehensive.json archive/old_queries/ 2>/dev/null
mv data/processed/all_queries_with_youtube_20251104_221809.json archive/old_queries/ 2>/dev/null
mv data/processed/FINAL_queries_with_youtube_20251104_222303.json archive/old_queries/ 2>/dev/null
mv data/processed/FINAL_IMPROVED_queries_20251104_222914.json archive/old_queries/ 2>/dev/null
mv data/processed/queries_with_labels.json archive/old_queries/ 2>/dev/null

# Move old document files
mv data/processed/merged_with_youtube_20251104_221755.json archive/old_documents/ 2>/dev/null
mv data/processed/FINAL_documents_with_youtube_20251104_222303.json archive/old_documents/ 2>/dev/null
mv data/processed/FINAL_IMPROVED_documents_20251104_222914.json archive/old_documents/ 2>/dev/null
mv data/processed/merged_all_20251103_124240.json archive/old_documents/ 2>/dev/null
mv data/processed/merged_all_20251103_124240_OLD.json archive/old_documents/ 2>/dev/null
mv data/processed/youtube_documents.json archive/old_documents/ 2>/dev/null
mv data/processed/youtube_documents_sc_only.json archive/old_documents/ 2>/dev/null
mv data/processed/youtube_documents_with_difficulty.json archive/old_documents/ 2>/dev/null
mv data/processed/youtube_videos_need_queries.json archive/old_documents/ 2>/dev/null

# Move checkpoint files
mv youtube_scrape_checkpoint.json archive/ 2>/dev/null
mv youtube_transcripts_checkpoint.json archive/ 2>/dev/null
mv data/processed/youtube_video_titles_checkpoint.json archive/ 2>/dev/null
mv data/processed/youtube_video_titles.json archive/ 2>/dev/null
mv data/processed/youtube_transcripts.json archive/ 2>/dev/null

# Move old training files
mv data/processed/training_pairs.json archive/ 2>/dev/null
mv dataset_upload/training_pairs.json archive/ 2>/dev/null
mv sample_docs_for_queries.json archive/ 2>/dev/null

echo "   ✅ Moved intermediate files"

echo ""
echo "📊 Current Project Structure:"
echo ""
echo "training/                              ← TRAINING DATA (USE THIS)"
echo "├── training_dataset.json             (4,546 examples)"
echo "├── documents.json                     (1,762 documents)"
echo "└── training_metadata.json             (metadata)"
echo ""
echo "data/processed/                        ← ESSENTIAL DATA"
echo "├── queries_final_clean_*.json         (Final cleaned query pairs)"
echo "├── FINAL_ALL_IMPROVED_documents_*.json (Final document collection)"
echo "└── FINAL_ALL_IMPROVED_queries_with_general_*.json (Original full queries)"
echo ""
echo "data/raw/                              ← RAW SOURCE DATA"
echo "├── arxiv_full_papers.json"
echo "├── superconductor_pure_300.json"
echo "└── [other source files]"
echo ""
echo "archive/                               ← OLD/INTERMEDIATE FILES"
echo "├── intermediate_data/"
echo "├── old_queries/"
echo "└── old_documents/"
echo ""

echo "======================================================================"
echo "✅ Cleanup Complete!"
echo "======================================================================"
echo ""
echo "Essential Files:"
echo "   🎯 training/training_dataset.json - Ready for training"
echo "   📚 training/documents.json - All documents"
echo "   📝 training/training_metadata.json - Metadata"
echo ""
echo "Archive:"
echo "   📦 archive/ - Old intermediate files (can be deleted if needed)"
echo ""
echo "======================================================================"
