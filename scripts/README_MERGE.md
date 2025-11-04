# Data Merge Script Documentation

## Overview

The `merge_data.py` script consolidates multiple JSON data sources into a unified document format suitable for semantic search. It currently supports:

- **Wikipedia articles** - Encyclopedia entries about superconductivity
- **arXiv papers** - Research papers and reviews
- **MIT OCW materials** - Lecture notes and readings
- **YouTube videos** - Video transcripts (ready to use when data is available)

## Quick Start

### Basic Usage

Run the script from the project root directory:

```bash
python3 scripts/merge_data.py
```

This will:
1. Scan the `data/raw/` directory for JSON files
2. Merge all compatible files into a unified format
3. Save the output to `data/raw/merged_documents_TIMESTAMP.json`
4. Print a summary of merged documents

### Output

The merged file contains:
- **Metadata** - Statistics about the merged dataset
- **Documents** - Array of unified document objects

Sample output structure:
```json
{
  "metadata": {
    "merge_date": "2025-10-30T21:33:01",
    "total_documents": 483,
    "total_words": 218470,
    "sources": {
      "arxiv": 376,
      "wikipedia": 64,
      "mit_ocw": 43
    }
  },
  "documents": [
    {
      "id": "wikipedia_1",
      "source": "wikipedia",
      "title": "Superconductivity",
      "content": "...",
      "url": "https://...",
      "word_count": 5068,
      "type": "encyclopedia",
      "category": "fundamentals",
      "focus_area": "main",
      ...
    }
  ]
}
```

## Adding YouTube Data Tomorrow

When you have YouTube data ready, the script is **already configured** to handle it! Just make sure your YouTube JSON file follows this structure:

```json
{
  "metadata": {
    "scrape_date": "2025-10-30T16:19:06",
    "total_videos": 50
  },
  "videos": [
    {
      "id": "youtube_video_1",
      "video_id": "abc123",
      "title": "Introduction to Superconductivity",
      "url": "https://youtube.com/watch?v=abc123",
      "channel_name": "Physics Lectures",
      "transcript": {
        "text": "Full transcript text here..."
      },
      "categorization": {
        "focus_type": "main"
      },
      "tags": ["superconductivity", "physics"]
    }
  ]
}
```

### Steps to Add YouTube Data:

1. **Place your YouTube JSON file** in `data/raw/` directory with a name containing "youtube" (e.g., `youtube_data_20251031.json`)

2. **Run the merge script** - It will automatically detect and process the YouTube data:
   ```bash
   python3 scripts/merge_data.py
   ```

3. **Done!** The YouTube videos will be merged with all other data sources.

The script already has a dedicated `merge_youtube()` function that:
- Extracts video transcripts
- Preserves video metadata (views, likes, channel info)
- Handles missing transcripts gracefully
- Calculates word counts automatically

## Advanced Usage

### Specify Custom Output Path

```bash
python3 scripts/merge_data.py --output data/processed/my_merged_data.json
```

### Merge Only Specific Files

```bash
python3 scripts/merge_data.py --patterns "youtube*.json" "wikipedia*.json"
```

### Compact JSON Output

```bash
python3 scripts/merge_data.py --compact
```

### Custom Data Directory

```bash
python3 scripts/merge_data.py --data-dir /path/to/data
```

## Unified Document Schema

All documents are converted to this standard format:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier |
| `source` | string | Yes | Data source (wikipedia, arxiv, youtube, etc.) |
| `title` | string | Yes | Document title |
| `content` | string | Yes | Full text content |
| `url` | string | Yes | Source URL |
| `word_count` | int | Yes | Number of words |
| `collected_at` | string | Yes | ISO timestamp |
| `type` | string | No | Document type (encyclopedia, video, etc.) |
| `category` | string | No | Subject category |
| `focus_area` | string | No | Focus classification (main, hot_topic, etc.) |
| `difficulty_level` | int | No | Content difficulty (1-5) |
| `summary` | string | No | Brief summary or abstract |
| `tags` | array | No | Keywords/tags |
| `source_metadata` | object | No | Source-specific metadata |

## Extending the Script

### Adding a New Data Source

To add support for a new data source (e.g., research databases, podcasts):

1. **Create a merge method** in the `DataMerger` class:
   ```python
   def merge_my_source(self, file_path: Path) -> int:
       """Merge documents from my new source."""
       # Read your JSON file
       # Convert to UnifiedDocument objects
       # Add to self.documents
       return count
   ```

2. **Update `merge_all()`** to detect your file pattern:
   ```python
   elif 'my_source' in file_path.name:
       total_count += self.merge_my_source(file_path)
   ```

3. **Add pattern** to default patterns if needed:
   ```python
   patterns = [
       'superconductor*.json',
       'mit_ocw*.json',
       'youtube*.json',
       'my_source*.json'  # Add this
   ]
   ```

### Customizing the Output

You can modify the `save_merged()` method to:
- Change the output format (CSV, Parquet, etc.)
- Add additional metadata fields
- Split output into multiple files
- Implement compression

## Troubleshooting

### File Not Found

Make sure you're running from the project root:
```bash
cd /Users/shrey/Semantic\ Search\ Project/superconductor-search
python3 scripts/merge_data.py
```

### Missing Fields

The script handles missing fields gracefully using defaults. Check the console output for warnings.

### Large Files

For very large JSON files (>100MB), consider:
- Using `--compact` flag to reduce output size
- Processing files in batches
- Using streaming JSON parsers

## Example Workflow

### Daily Update Workflow

```bash
# 1. Run your data collection scripts
python3 scripts/scrape_youtube.py
python3 scripts/scrape_mit_ocw.py

# 2. Merge all data
python3 scripts/merge_data.py --output data/processed/merged_latest.json

# 3. Use merged data for indexing
python3 scripts/build_index.py --input data/processed/merged_latest.json
```

## Notes

- The script preserves all original metadata in `source_metadata` field
- Duplicate detection is not implemented - ensure input files don't have duplicates
- Files with "merged" in the name are automatically skipped
- Word counts are calculated automatically if not provided
- All timestamps are in ISO 8601 format

## Support

For issues or questions, check:
1. Console output for error messages
2. Ensure JSON files are valid (use `python3 -m json.tool yourfile.json`)
3. Verify file permissions in `data/raw/` directory
