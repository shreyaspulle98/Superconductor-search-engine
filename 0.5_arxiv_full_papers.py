#!/usr/bin/env python3
"""
arXiv Full Paper Downloader & Extractor
==========================================

Downloads full PDFs from existing arXiv papers and extracts text.
Chunks papers by sections for better semantic search.

Current: 230 abstracts (~200 words each) = ~46,000 words
Target:  230 full papers (~6,000 words each) = ~1,380,000 words

This will add ~1,150 new documents (230 papers × ~5 sections average)
"""

import os
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import requests
from pathlib import Path

# Try to import PDF libraries
try:
    import fitz  # pymupdf (import as fitz, not PyMuPDF)
    PDF_LIBRARY = 'pymupdf'
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = 'pdfplumber'
    except ImportError:
        print("❌ ERROR: No PDF library found!")
        print("   Install one of: pip3 install pymupdf  OR  pip3 install pdfplumber")
        exit(1)

print(f"✅ Using PDF library: {PDF_LIBRARY}")

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_FILE = "data/raw/superconductor_pure_300.json"
OUTPUT_DIR = "data/raw/arxiv_pdfs"
OUTPUT_FILE = "data/raw/arxiv_full_papers.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

RATE_LIMIT_DELAY = 3  # seconds between downloads (be respectful!)
MAX_PAPERS = None  # None = all papers, or set a number for testing

# ============================================================================
# PDF TEXT EXTRACTION
# ============================================================================

def extract_text_pymupdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"    ⚠️  PyMuPDF extraction error: {e}")
        return ""


def extract_text_pdfplumber(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"    ⚠️  pdfplumber extraction error: {e}")
        return ""


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text using available PDF library."""
    if PDF_LIBRARY == 'pymupdf':
        return extract_text_pymupdf(pdf_path)
    else:
        return extract_text_pdfplumber(pdf_path)


# ============================================================================
# SECTION DETECTION & CHUNKING
# ============================================================================

def detect_sections(text: str) -> Dict[str, str]:
    """
    Split paper into sections based on common section headers.

    Returns dict with keys: abstract, introduction, methods, results, discussion, conclusion
    """
    sections = {}

    # Common section patterns (case-insensitive)
    patterns = {
        'abstract': r'\n\s*abstract\s*\n',
        'introduction': r'\n\s*(introduction|1\s*\.?\s*introduction)\s*\n',
        'methods': r'\n\s*(\d+\s*\.?\s*)?(methods?|methodology|experimental|experimental methods)\s*\n',
        'results': r'\n\s*(\d+\s*\.?\s*)?(results?|findings)\s*\n',
        'discussion': r'\n\s*(\d+\s*\.?\s*)?discussion\s*\n',
        'conclusion': r'\n\s*(\d+\s*\.?\s*)?(conclusion|conclusions|summary)\s*\n',
        'references': r'\n\s*(\d+\s*\.?\s*)?(references|bibliography)\s*\n'
    }

    # Find all section positions
    section_positions = []
    for section_name, pattern in patterns.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for match in matches:
            section_positions.append((match.start(), section_name))

    # Sort by position
    section_positions.sort()

    # If no sections detected, treat whole paper as one section
    if len(section_positions) == 0:
        return {'full_paper': text}

    # Extract text between sections
    for i, (pos, name) in enumerate(section_positions):
        if i < len(section_positions) - 1:
            next_pos = section_positions[i + 1][0]
            section_text = text[pos:next_pos].strip()
        else:
            section_text = text[pos:].strip()

        # Only keep sections before references
        if name == 'references':
            break

        # Store section if it has substantial content (> 100 chars)
        if len(section_text) > 100:
            sections[name] = section_text

    return sections


def chunk_paper(text: str, paper_title: str, paper_id: str) -> List[Dict]:
    """
    Chunk paper into sections for separate indexing.

    Returns list of document dicts, one per section.
    """
    sections = detect_sections(text)

    # If no sections detected, create chunks by paragraph/length
    if len(sections) == 0 or (len(sections) == 1 and 'full_paper' in sections):
        # Fallback: split into ~2000 word chunks
        words = text.split()
        chunk_size = 2000
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk_text = ' '.join(words[i:i+chunk_size])
            if len(chunk_text) > 200:  # Minimum chunk size
                chunks.append({
                    'section_name': f'part_{i//chunk_size + 1}',
                    'section_text': chunk_text,
                    'word_count': len(chunk_text.split())
                })

        return chunks

    # Convert sections dict to list of dicts
    chunks = []
    for section_name, section_text in sections.items():
        chunks.append({
            'section_name': section_name,
            'section_text': section_text,
            'word_count': len(section_text.split())
        })

    return chunks


# ============================================================================
# PDF DOWNLOADING
# ============================================================================

def download_pdf(pdf_url: str, save_path: str) -> bool:
    """Download PDF from URL."""
    try:
        response = requests.get(pdf_url, timeout=30, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        print(f"    ❌ Download error: {e}")
        return False


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def process_arxiv_papers():
    """Main function to download and process arXiv papers."""

    print("\n" + "="*80)
    print("📄 arXiv FULL PAPER DOWNLOADER & EXTRACTOR")
    print("="*80)
    print(f"📂 Input: {INPUT_FILE}")
    print(f"💾 PDFs: {OUTPUT_DIR}/")
    print(f"📄 Output: {OUTPUT_FILE}")
    print(f"⏱️  Rate limit: {RATE_LIMIT_DELAY}s between downloads")
    print()

    # Load existing data
    print("📖 Loading existing arXiv abstracts...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: {INPUT_FILE} not found!")
        print("   Run 0.1_superconductor_scraper.py first to collect arXiv abstracts.")
        return

    # Filter arXiv papers
    arxiv_papers = [doc for doc in data if doc.get('source') == 'arxiv']
    print(f"✅ Found {len(arxiv_papers)} arXiv papers")

    if MAX_PAPERS:
        arxiv_papers = arxiv_papers[:MAX_PAPERS]
        print(f"   (Processing first {MAX_PAPERS} for testing)")

    # Process each paper
    all_sections = []
    success_count = 0
    fail_count = 0

    for idx, paper in enumerate(arxiv_papers, 1):
        paper_id = paper.get('id', f'arxiv_{idx}')
        title = paper.get('title', 'Untitled')
        pdf_url = paper.get('pdf_url', '')

        print(f"\n[{idx}/{len(arxiv_papers)}] {title[:60]}...")

        if not pdf_url:
            print("    ⏭️  No PDF URL, skipping")
            fail_count += 1
            continue

        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
        pdf_filename = f"{paper_id.replace('/', '_')}_{safe_title}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

        # Download PDF if not already downloaded
        if not os.path.exists(pdf_path):
            print(f"    📥 Downloading...")
            if download_pdf(pdf_url, pdf_path):
                print(f"    ✅ Downloaded ({os.path.getsize(pdf_path) / 1024:.1f} KB)")
                time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
            else:
                fail_count += 1
                continue
        else:
            print(f"    ✓  Already downloaded")

        # Extract text
        print(f"    📄 Extracting text...")
        full_text = extract_text_from_pdf(pdf_path)

        if not full_text or len(full_text) < 500:
            print(f"    ❌ Extraction failed or too short ({len(full_text)} chars)")
            fail_count += 1
            continue

        print(f"    ✅ Extracted {len(full_text):,} characters")

        # Chunk into sections
        print(f"    ✂️  Chunking into sections...")
        sections = chunk_paper(full_text, title, paper_id)
        print(f"    ✅ Created {len(sections)} sections")

        # Create document for each section
        for section_idx, section in enumerate(sections, 1):
            section_doc = {
                'id': f"{paper_id}_section_{section_idx}",
                'parent_paper_id': paper_id,
                'source': 'arxiv',
                'type': 'research_section',
                'focus_area': paper.get('focus_area', 'main'),
                'section_name': section['section_name'],
                'section_number': section_idx,
                'total_sections': len(sections),
                'paper_title': title,
                'content': section['section_text'],
                'word_count': section['word_count'],
                'url': paper.get('url', ''),
                'pdf_url': pdf_url,
                'authors': paper.get('authors', []),
                'published': paper.get('published', ''),
                'year': paper.get('year', ''),
                'categories': paper.get('categories', []),
                'difficulty_level': 4,  # arXiv papers are expert level
                'collected_at': datetime.now().isoformat()
            }

            all_sections.append(section_doc)

        success_count += 1

        # Progress update every 10 papers
        if idx % 10 == 0:
            print(f"\n📊 Progress: {success_count} successful, {fail_count} failed, {len(all_sections)} sections created")

    # Save results
    print("\n" + "="*80)
    print("💾 SAVING RESULTS")
    print("="*80)

    output_data = {
        'metadata': {
            'collection_date': datetime.now().isoformat(),
            'source': 'arxiv_full_papers',
            'total_papers_processed': success_count,
            'total_papers_failed': fail_count,
            'total_sections_created': len(all_sections),
            'pdf_extraction_library': PDF_LIBRARY,
            'average_sections_per_paper': len(all_sections) / success_count if success_count > 0 else 0
        },
        'documents': all_sections
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)

    print(f"\n✅ Saved to: {OUTPUT_FILE}")
    print(f"   File size: {file_size_mb:.1f} MB")
    print(f"   Total sections: {len(all_sections):,}")
    print(f"   Papers processed: {success_count}/{len(arxiv_papers)}")
    print(f"   Average sections per paper: {len(all_sections) / success_count:.1f}")

    # Statistics
    total_words = sum(doc['word_count'] for doc in all_sections)
    print(f"\n📊 STATISTICS")
    print(f"   Total words: {total_words:,}")
    print(f"   Average words per section: {total_words // len(all_sections):,}")
    print(f"   Compared to abstracts: {total_words // (success_count * 200):.1f}x more content")

    print("\n" + "="*80)
    print("✅ ARXIV FULL PAPER EXTRACTION COMPLETE!")
    print("="*80)
    print("\n📝 Next steps:")
    print("   1. Merge this with other datasets using 0.4_merge_datasets.py")
    print("   2. Re-train model: python3 02.train_model.py")
    print("   3. Rebuild index: python3 03_build_search_index.py")
    print()


if __name__ == "__main__":
    process_arxiv_papers()
