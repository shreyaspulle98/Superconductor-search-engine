#!/usr/bin/env python3
"""
Superconductor Search Engine - Data Collection
100% Superconductor Focus + AI for Materials + Room-Temp Research

Target: 300 documents, 2400 queries
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict
import wikipedia
import arxiv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Document targets (updated to include Level 2 content)
TARGET_COUNTS = {
    "wikipedia": 116,       # Expanded to include Level 2 intermediate content
    "youtube": 30,          # Superconductor + AI + Room-temp videos
    "arxiv_reviews": 40,    # Review papers
    "arxiv_research": 190   # Research papers
}

# Query targets (total 2,400)
QUERY_TARGETS = {
    "beginner": 960,        # 40% - What is a superconductor?
    "intermediate": 960,    # 40% - How does BCS theory work?
    "expert": 480           # 20% - Phonon-mediated pairing mechanisms
}

print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║          SUPERCONDUCTOR SEARCH ENGINE - DATA COLLECTION V2               ║
║                                                                          ║
║  🎯 MAIN FOCUS: Superconductors (70%)                                   ║
║  🤖 SUB-FOCUS: AI for Materials Science (15%)                           ║
║  🔥 HOT TOPIC: Room-Temperature Superconductors (15%)                   ║
║                                                                          ║
║  Documents: 376 (116 Wiki + 30 YouTube + 230 arXiv)                     ║
║  NEW: +76 Level 2 Wikipedia articles for intermediate content           ║
║  Queries: 2,400 (8 per document average)                                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

# ============================================================================
# PART 1: WIKIPEDIA SCRAPING (116 articles - EXPANDED WITH LEVEL 2 CONTENT)
# ============================================================================

def scrape_wikipedia() -> List[Dict]:
    """
    116 Wikipedia articles - 100% superconductor focus.
    Expanded to include Level 2 intermediate content to fill the gap.

    Categories:
    - Fundamentals (30): Level 2-3 theory and phenomena
    - Materials (30): Level 2-4 superconducting materials
    - High-Tc (10): Level 3-4 advanced superconductors
    - Applications (20): Level 2-3 devices and uses
    - Room-Temp (8): Level 4 cutting-edge research
    - AI/Materials (10): Level 3 computational methods
    - People/History (8): Level 1 biographical content
    """
    print("\n" + "="*80)
    print("📖 WIKIPEDIA SCRAPING - Expanded with Level 2 Content")
    print("="*80)
    
    article_titles = {
        # ===== SUPERCONDUCTOR FUNDAMENTALS - Level 2-3 (30 articles) =====
        "fundamentals": [
            # Existing core articles
            "Superconductivity",
            "History of superconductivity",
            "BCS theory",
            "Cooper pair",
            "Meissner effect",
            "Type-I superconductor",
            "Type-II superconductor",
            "Josephson effect",
            "London equations",
            "Ginzburg-Landau theory",
            "Coherence length",
            "Penetration depth",
            "Flux pinning",
            "Magnetic flux quantum",
            "Abrikosov vortex",
            "Phonon",
            # NEW Level 2 articles (Theory & Phenomena)
            "Critical temperature",
            "Critical magnetic field",
            "Superconducting gap",
            "London penetration depth",
            "Little-Parks effect",
            "Proximity effect (superconductivity)",
            "Andreev reflection",
            "Zero resistance",
            "Perfect diamagnetism",
            "Flux creep",
            "Quantum vortex",
            "Vortex matter",
            "Critical state model",
            "Diamagnetism"
        ],

        # ===== MATERIALS - Level 2-4 (30 articles) =====
        "materials": [
            # Existing materials
            "Cuprate superconductor",
            "Yttrium barium copper oxide",  # YBCO full name
            "Bismuth strontium calcium copper oxide",  # BSCCO full name
            "Iron-based superconductor",
            "Carbonaceous sulfur hydride",
            # NEW Level 2-3 materials
            "Magnesium diboride",  # MgB2
            "Niobium-titanium",
            "Niobium-tin",
            "Lanthanum hydride",
            "Nickelate superconductor",
            "Heavy fermion superconductor",
            "Organic superconductor",
            "Chevrel phases",
            "A15 phases",
            "Mercury barium calcium copper oxide",
            "Thallium barium calcium copper oxide",
            "Lead",  # (superconductor properties)
            "Tin",  # (superconductor properties)
            "Aluminum",  # (superconductor properties)
            "Niobium",
            "Vanadium",
            "Technetium",
            "Fullerene",  # (superconductivity)
            "Pnictogen",
            "Chalcogen"
        ],

        # ===== HIGH-TEMPERATURE SUPERCONDUCTORS - Level 3-4 (10 articles) =====
        "high_tc": [
            "High-temperature superconductivity",
            "Unconventional superconductor",
            "Pseudogap",
            "Fermi liquid theory",
            "Quantum critical point",
            "Spin fluctuation",
            "Charge density wave",
            "Stripe phase",
            "Superconducting order parameter",
            "Pairing symmetry"
        ],

        # ===== APPLICATIONS & DEVICES - Level 2-3 (20 articles) =====
        "applications": [
            # Existing
            "Josephson effect",
            # NEW applications
            "Superconducting magnet",
            "SQUID",
            "Josephson junction",
            "Superconducting quantum computing",
            "Superconducting radio frequency",
            "Rapid single flux quantum",
            "Superconducting tunnel junction",
            "Superconducting wire",
            "Superconducting cable",
            "Magnetic levitation",
            "Maglev",
            "Magnetic resonance imaging",  # MRI
            "Nuclear magnetic resonance",
            "Qubit",
            "Particle accelerator",
            "Flux qubit",
            "Superconducting electric machine",
            "Superconducting transformer",
            "Fault current limiter"
        ],

        # ===== ROOM-TEMPERATURE SUPERCONDUCTORS - Level 4 (8 articles) =====
        "room_temp": [
            "Room-temperature superconductor",
            "High pressure",
            "Diamond anvil cell",
            "Carbonaceous sulfur hydride",
            "Hydrogen sulfide",  # H3S
            "Lanthanum hydride",
            "Metallic hydrogen",
            "Superhydride"
        ],

        # ===== AI FOR MATERIALS - Level 3 (10 articles) =====
        "ai_materials": [
            "Materials informatics",
            "Computational materials science",
            "Density functional theory",
            "Machine learning",
            "Materials genome initiative",
            "High-throughput screening",
            "Ab initio quantum chemistry methods",
            "Molecular dynamics",
            "Crystal structure prediction",
            "Materials database"
        ],

        # ===== PEOPLE & HISTORY - Level 2 (8 articles) =====
        "people_history": [
            "John Bardeen",
            "Leon Cooper",
            "John Robert Schrieffer",
            "Heike Kamerlingh Onnes",
            "Alexei Abrikosov",
            "Vitaly Ginzburg",
            "Lev Landau",
            "Brian Josephson"
        ]
    }
    
    documents = []
    doc_id = 1
    
    for category, titles in article_titles.items():
        category_name = category.replace('_', ' ').title()
        print(f"\n📚 Category: {category_name} ({len(titles)} articles)")
        
        # Set focus area
        focus_map = {
            "fundamentals": "main",
            "materials": "main",
            "high_tc": "main",
            "applications": "main",
            "room_temp": "hot_topic",
            "ai_materials": "sub_focus",
            "people_history": "main"
        }
        focus_area = focus_map.get(category, "main")

        # Set difficulty (Level 2-3 for intermediate content)
        difficulty_map = {
            "fundamentals": 2,      # Level 2: Intermediate theory
            "materials": 2,         # Level 2: Intermediate materials
            "high_tc": 3,           # Level 3: Advanced
            "applications": 2,      # Level 2: Intermediate applications
            "room_temp": 4,         # Level 4: Expert/cutting-edge
            "ai_materials": 3,      # Level 3: Advanced computational
            "people_history": 1     # Level 1: Beginner (biographical)
        }
        base_difficulty = difficulty_map.get(category, 3)
        
        for title in titles:
            try:
                print(f"  [{doc_id}/{TARGET_COUNTS['wikipedia']}] {title}...", end=" ")
                
                page = wikipedia.page(title, auto_suggest=False)
                word_count = len(page.content.split())
                
                doc = {
                    "id": f"wikipedia_{doc_id}",
                    "source": "wikipedia",
                    "type": "encyclopedia",
                    "category": category,
                    "focus_area": focus_area,
                    "title": page.title,
                    "url": page.url,
                    "content": page.content,
                    "summary": page.summary,
                    "word_count": word_count,
                    "collected_at": datetime.now().isoformat(),
                    "difficulty_level": base_difficulty
                }
                
                documents.append(doc)
                print(f"✅ ({word_count} words, Level {base_difficulty}, {focus_area})")
                doc_id += 1
                time.sleep(0.5)
                
            except wikipedia.exceptions.DisambiguationError as e:
                print(f"⚠️  Disambiguation → {e.options[0][:40]}", end=" ")
                try:
                    page = wikipedia.page(e.options[0])
                    doc = {
                        "id": f"wikipedia_{doc_id}",
                        "source": "wikipedia",
                        "type": "encyclopedia",
                        "category": category,
                        "focus_area": focus_area,
                        "title": page.title,
                        "url": page.url,
                        "content": page.content,
                        "summary": page.summary,
                        "word_count": len(page.content.split()),
                        "collected_at": datetime.now().isoformat(),
                        "difficulty_level": base_difficulty
                    }
                    documents.append(doc)
                    print(f"✅")
                    doc_id += 1
                except:
                    print(f"❌")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:40]}")
    
    print(f"\n✅ Wikipedia: {len(documents)} articles collected")
    return documents


# ============================================================================
# PART 2: YOUTUBE SCRAPING (30 videos - SUPERCONDUCTORS + AI + ROOM-TEMP)
# ============================================================================

def get_superconductor_videos() -> List[Dict]:
    """
    100+ video candidates - ONLY superconductors, AI materials, and room-temp content.
    NO batteries, solar, MOFs, or other materials!
    """
    return [
        # ===== SUPERCONDUCTOR FUNDAMENTALS (40 videos) =====
        {"id": "2rZfYRdlDpI", "title": "What is a Superconductor? - Real Engineering", "topic": "fundamentals", "focus": "main"},
        {"id": "RS7gyZJg5nc", "title": "Superconductors Explained - Physics Girl", "topic": "fundamentals", "focus": "main"},
        {"id": "bqvQ3K2XZQU", "title": "How Do Superconductors Work? - Veritasium", "topic": "fundamentals", "focus": "main"},
        {"id": "g7o1phQQ9fA", "title": "The Science of Superconductors", "topic": "fundamentals", "focus": "main"},
        {"id": "VJrvhyJx3Os", "title": "Superconductivity and Magnetic Levitation", "topic": "fundamentals", "focus": "main"},
        {"id": "CUHwKUd3dwI", "title": "Quantum Levitation Demonstration", "topic": "fundamentals", "focus": "main"},
        {"id": "xoMTvmtbVmE", "title": "Meissner Effect Demonstration", "topic": "fundamentals", "focus": "main"},
        {"id": "K3KlA-WXwGw", "title": "Superconductors and Magnetic Fields", "topic": "fundamentals", "focus": "main"},
        {"id": "BHZALtqAjeM", "title": "Superconductivity Course - MIT", "topic": "fundamentals", "focus": "main"},
        {"id": "mALPsEn0p7s", "title": "Superconducting Magnets - MIT", "topic": "applications", "focus": "main"},
        {"id": "U3Jz8dYNcWE", "title": "High Temperature Superconductors - Stanford", "topic": "high_tc", "focus": "main"},
        {"id": "RL3Iu4N7X4Y", "title": "YBCO Superconductor Properties", "topic": "high_tc", "focus": "main"},
        {"id": "mGIJKcj4GUk", "title": "Superconductors in Quantum Computing", "topic": "applications", "focus": "main"},
        {"id": "7NkJNvP84mI", "title": "Superconducting Qubits Explained", "topic": "applications", "focus": "main"},
        {"id": "xM9FJZrKV7M", "title": "Growing Superconducting Crystals", "topic": "fabrication", "focus": "main"},
        {"id": "8H5CMeh8o8A", "title": "Type I vs Type II Superconductors", "topic": "fundamentals", "focus": "main"},
        {"id": "j5XvQg0q7vg", "title": "BCS Theory Explained Simply", "topic": "theory", "focus": "main"},
        {"id": "eqtuNXWT0mo", "title": "Cooper Pairs and Superconductivity", "topic": "theory", "focus": "main"},
        {"id": "ZgjzXgLvTmY", "title": "Critical Temperature in Superconductors", "topic": "fundamentals", "focus": "main"},
        {"id": "l82PkdxN0Xg", "title": "Josephson Junction Applications", "topic": "applications", "focus": "main"},
        {"id": "HjS1hCbkLcU", "title": "Cuprate Superconductors Explained", "topic": "high_tc", "focus": "main"},
        {"id": "8Pp4NdXzQhA", "title": "Iron-Based Superconductors", "topic": "high_tc", "focus": "main"},
        {"id": "xCwf8xeXMfU", "title": "Superconductivity in Quantum Mechanics", "topic": "theory", "focus": "main"},
        {"id": "Fzh9R7VWVVU", "title": "History of Superconductor Discovery", "topic": "fundamentals", "focus": "main"},
        {"id": "E7BN3Rdwp7Y", "title": "Superconducting Materials Overview", "topic": "fundamentals", "focus": "main"},
        {"id": "bL2pJvYb8vI", "title": "Superconducting Wire Manufacturing", "topic": "fabrication", "focus": "main"},
        {"id": "RbOZ4B1rCok", "title": "Flux Pinning in Superconductors", "topic": "fundamentals", "focus": "main"},
        {"id": "D99NHb7ykNs", "title": "Superconductor Phase Transitions", "topic": "theory", "focus": "main"},
        {"id": "4p6jWoSq5Lw", "title": "Vortex State in Type-II Superconductors", "topic": "fundamentals", "focus": "main"},
        {"id": "GrMLxn-6nLA", "title": "Applications of Superconductivity", "topic": "applications", "focus": "main"},
        {"id": "mL3nK7rP2wR", "title": "Superconducting Electronics", "topic": "applications", "focus": "main"},
        {"id": "nK2hM8pL7kQ", "title": "Cryogenics for Superconductors", "topic": "fundamentals", "focus": "main"},
        {"id": "oM3nL7rP2wK", "title": "Future of Superconducting Technology", "topic": "applications", "focus": "main"},
        {"id": "7CKHkKGVBko", "title": "History of Superconductivity", "topic": "fundamentals", "focus": "main"},
        {"id": "4l0bZ8-OhWM", "title": "Superconductor Applications", "topic": "applications", "focus": "main"},
        {"id": "tOMXRFr-y08", "title": "Type I vs Type II Comparison", "topic": "fundamentals", "focus": "main"},
        {"id": "2a-Gn8HRFrs", "title": "Superconductor Levitation Physics", "topic": "fundamentals", "focus": "main"},
        {"id": "eL_u8MUkG_c", "title": "Zero Resistance in Superconductors", "topic": "fundamentals", "focus": "main"},
        {"id": "YhZO9xJOJ-Q", "title": "Critical Temperature Explained", "topic": "fundamentals", "focus": "main"},
        {"id": "6y-hqYW6OqI", "title": "BCS Theory Introduction", "topic": "theory", "focus": "main"},
        
        # ===== ROOM-TEMPERATURE SUPERCONDUCTORS (35 videos) =====
        {"id": "ZGMyOkdqI-c", "title": "Room Temperature Superconductors Explained", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "EBIvJ9qjVLE", "title": "The Quest for Room Temperature Superconductors", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "j7fSuNLq_xI", "title": "Understanding Room Temperature Superconductors", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "pN0sVhVnEdI", "title": "LK-99: The Room Temperature Superconductor Controversy", "topic": "LK99", "focus": "hot_topic"},
        {"id": "TkPC5VqWzKw", "title": "Breaking Down the LK-99 Claims", "topic": "LK99", "focus": "hot_topic"},
        {"id": "rAKoLbGw-Gg", "title": "Room Temperature Superconductor Discovery 2020", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "7H2xP9GjE0I", "title": "Hydrogen-Rich Superconductors Explained", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "mK8sVzR5X3Q", "title": "High Pressure Superconductivity", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "8L9pVxR2jQw", "title": "Carbonaceous Sulfur Hydride Breakthrough", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "qN7kWxP3Rjs", "title": "Ranga Dias Room-Temperature Claims", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "vL2pQ8xT7Do", "title": "The Science Behind Room-Temp Superconductors", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "hR3nT9kL8Yw", "title": "Diamond Anvil Cell Experiments", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "tY9kR7pMn2Q", "title": "Superhydrides and High-Pressure Physics", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "nK8mQ9rL3Ps", "title": "Failed Room-Temp Superconductor Claims", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "dL2hR8pN9Ks", "title": "Future of Room-Temperature Superconductivity", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "VNE8kR3sZYw", "title": "Lanthanum Hydride Superconductivity", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "T8xZbU2vQ5A", "title": "Why Room Temperature Superconductors Matter", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "4rJ8wGxL9kM", "title": "Compressed Hydrogen Superconductivity", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "YmL3v8rP2wQ", "title": "Metallic Hydrogen and Superconductivity", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "PJL2h9vB8xY", "title": "High Pressure Experiments on Superconductors", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "fKL8nR2vQ3M", "title": "The LK-99 Replication Attempts", "topic": "LK99", "focus": "hot_topic"},
        {"id": "gW2mL9rP8kQ", "title": "Room Temperature Superconductor Timeline", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "xH8pN9rL2mY", "title": "Recent Breakthroughs in Superconductivity", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "tR2hM8pL9kW", "title": "Ambient Pressure Superconductivity Challenge", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "yK3mL8rP2wN", "title": "Superconductor Synthesis at High Pressure", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "aL2hM9pL8kR", "title": "Hydride Superconductors Overview", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "bK3mN7rP2wQ", "title": "High Tc Superconductor Mechanisms", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "cM2hN8pL9kW", "title": "Pressure-Induced Superconductivity", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "dL3mK7rP2wR", "title": "Exotic Superconductors", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "eK2hM8pL7kQ", "title": "H3S Superconductor Discovery", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "fM3nL7rP2wK", "title": "Cuprate vs Hydride Superconductors", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "gL2hN8pL9kR", "title": "Room Temp Superconductor Materials", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "hK3mL7rP2wQ", "title": "Superconductivity Near Ambient Conditions", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "iM2hN9pL8kW", "title": "Latest Room-Temp Discoveries 2024", "topic": "room_temp", "focus": "hot_topic"},
        {"id": "jL3mK7rP2wR", "title": "Challenges in Room-Temp Superconductors", "topic": "room_temp", "focus": "hot_topic"},
        
        # ===== AI FOR MATERIALS SCIENCE (25 videos) =====
        {"id": "fVKLvbW5Bl4", "title": "AI in Materials Science - Introduction", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "YQBhc-pVdH8", "title": "Machine Learning for Materials Discovery", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "c8zBPrmE8cQ", "title": "Deep Learning in Materials Science", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "rZVCTlAkPdw", "title": "AI for Discovering New Materials", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "oR7KJUJ3Fvs", "title": "Materials Informatics Overview", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "hBkO3G1q1dI", "title": "High-Throughput Materials Screening with AI", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "7-HIuhC0vhs", "title": "Google DeepMind GNoME - Materials Discovery", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "qWrcgRwh6O8", "title": "How AI is Revolutionizing Material Science", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "BFSKPYVqgjc", "title": "Density Functional Theory Explained", "topic": "computational", "focus": "sub_focus"},
        {"id": "Qrp2yk7lYPE", "title": "Computational Chemistry for Materials", "topic": "computational", "focus": "sub_focus"},
        {"id": "3p5w9vb9Q9Q", "title": "Molecular Dynamics Simulations", "topic": "computational", "focus": "sub_focus"},
        {"id": "dNhMn_Tty4Q", "title": "Neural Networks for Material Properties", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "pL8rr3Je0Wo", "title": "Transfer Learning in Materials Science", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "8H2pJlJQfp8", "title": "Graph Neural Networks for Molecules", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "mR7kN2pQ8jw", "title": "AI Predictions of Superconductor Tc", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "wT3mL8rP9kQ", "title": "Data-Driven Materials Design", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "nW2hM7pL8kR", "title": "Active Learning for Materials Discovery", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "gL3mN8rP2wK", "title": "Materials Genome Initiative Explained", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "xK2hM9pL7kW", "title": "Generative Models for Crystal Structures", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "yH3mL8rP2wN", "title": "Bayesian Optimization in Materials Science", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "tM2hN7pL9kR", "title": "Automated Materials Synthesis", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "rK2hM8pL7kW", "title": "Quantum Machine Learning Materials", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "pN3mL7rP2wK", "title": "AlphaFold for Materials Science", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "qM2hN8pL9kR", "title": "Robotic Labs and AI Materials Discovery", "topic": "AI_materials", "focus": "sub_focus"},
        {"id": "kL3mN7rP2wQ", "title": "Computational Superconductor Prediction", "topic": "AI_materials", "focus": "sub_focus"},
    ]


def get_transcript_with_fallback(video_id: str) -> str:
    """Try to get transcript with multiple fallback options."""
    try:
        # Try 1: Get default transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript_list])
        return text
    except (TranscriptsDisabled, NoTranscriptFound):
        try:
            # Try 2: Get auto-generated English captions
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=['en', 'en-US', 'en-GB']
            )
            text = " ".join([entry['text'] for entry in transcript_list])
            return text
        except:
            # Try 3: List all available transcripts
            try:
                transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript in transcript_list_obj:
                    if 'en' in transcript.language_code.lower():
                        transcript_list = transcript.fetch()
                        text = " ".join([entry['text'] for entry in transcript_list])
                        return text
            except:
                return None
    return None


def scrape_youtube() -> List[Dict]:
    """Scrape 30 YouTube transcripts - superconductors + AI + room-temp only."""
    print("\n" + "="*80)
    print("📹 YOUTUBE SCRAPING - Superconductor Focus")
    print("="*80)
    
    documents = []
    videos = get_superconductor_videos()
    
    print(f"\n📋 Attempting {len(videos)} videos (target: {TARGET_COUNTS['youtube']})")
    print("   Focus: Superconductors + AI Materials + Room-Temp")
    
    attempted = 0
    skipped = 0
    
    for video_info in videos:
        if len(documents) >= TARGET_COUNTS["youtube"]:
            break
        
        video_id = video_info["id"]
        title = video_info["title"]
        topic = video_info.get("topic", "general")
        focus = video_info.get("focus", "main")
        attempted += 1
        
        try:
            print(f"\n  [{len(documents)+1}/{TARGET_COUNTS['youtube']}] {title[:55]}...")
            
            transcript_text = get_transcript_with_fallback(video_id)
            
            if transcript_text and len(transcript_text) > 100:
                word_count = len(transcript_text.split())
                
                doc = {
                    "id": f"youtube_{len(documents) + 1}",
                    "source": "youtube",
                    "type": "video_transcript",
                    "topic": topic,
                    "focus_area": focus,
                    "title": title,
                    "video_id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "content": transcript_text,
                    "word_count": word_count,
                    "collected_at": datetime.now().isoformat(),
                    "difficulty_level": 3  # Default medium
                }
                
                documents.append(doc)
                print(f"      ✅ {word_count} words ({focus})")
            else:
                skipped += 1
                print(f"      ⏭️  No transcript")
            
            time.sleep(0.5)
            
        except Exception as e:
            skipped += 1
            print(f"      ❌ {str(e)[:40]}")
    
    print(f"\n✅ YouTube: {len(documents)} videos | Attempted: {attempted} | Skipped: {skipped}")
    return documents


# ============================================================================
# PART 3: ARXIV SCRAPING (230 papers - SUPERCONDUCTORS ONLY)
# ============================================================================

def scrape_arxiv() -> Dict[str, List[Dict]]:
    """
    230 arXiv papers - 100% superconductor focus.
    40 reviews + 190 research papers
    """
    print("\n" + "="*80)
    print("📚 ARXIV SCRAPING - Pure Superconductor Focus")
    print("="*80)
    
    search_queries = [
        # ===== REVIEW PAPERS (targeting 40) =====
        ("superconductor review", 30, True, "main"),
        ("high temperature superconductor review", 25, True, "main"),
        ("room temperature superconductor review", 20, True, "hot_topic"),
        ("unconventional superconductivity review", 20, True, "main"),
        ("cuprate superconductor review", 15, True, "main"),
        ("BCS theory review", 15, True, "main"),
        ("iron-based superconductor review", 15, True, "main"),
        ("machine learning superconductor review", 15, True, "sub_focus"),
        
        # ===== SUPERCONDUCTOR FUNDAMENTALS (60 papers) =====
        ("BCS theory Cooper pair", 20, False, "main"),
        ("Meissner effect magnetic field", 20, False, "main"),
        ("Josephson junction superconductor", 20, False, "main"),
        ("superconductor critical temperature", 20, False, "main"),
        ("London penetration depth", 15, False, "main"),
        ("Ginzburg-Landau theory", 15, False, "main"),
        ("flux pinning superconductor", 20, False, "main"),
        ("Abrikosov vortex", 15, False, "main"),
        ("superconducting gap spectroscopy", 20, False, "main"),
        ("phonon-mediated pairing", 15, False, "main"),
        
        # ===== HIGH-TEMPERATURE SUPERCONDUCTORS (50 papers) =====
        ("cuprate superconductor YBCO", 30, False, "main"),
        ("iron-based superconductor FeSe", 25, False, "main"),
        ("nickelate superconductor", 25, False, "main"),
        ("d-wave superconductor", 20, False, "main"),
        ("unconventional superconductor pairing", 25, False, "main"),
        ("pseudogap cuprate", 20, False, "main"),
        ("strange metal superconductor", 20, False, "main"),
        ("high-Tc mechanism", 25, False, "main"),
        
        # ===== ROOM-TEMPERATURE SUPERCONDUCTORS (50 papers) =====
        ("room temperature superconductor ambient", 30, False, "hot_topic"),
        ("hydrogen-rich superconductor high pressure", 30, False, "hot_topic"),
        ("carbonaceous sulfur hydride", 25, False, "hot_topic"),
        ("LK-99 copper lead apatite", 20, False, "hot_topic"),
        ("hydride superconductor H3S", 25, False, "hot_topic"),
        ("lanthanum hydride superconductor", 20, False, "hot_topic"),
        ("superhydride high pressure", 25, False, "hot_topic"),
        ("diamond anvil cell superconductor", 20, False, "hot_topic"),
        ("ambient pressure superconductivity", 25, False, "hot_topic"),
        ("metallic hydrogen superconductor", 20, False, "hot_topic"),
        
        # ===== AI/ML FOR SUPERCONDUCTORS (40 papers) =====
        ("machine learning superconductor prediction Tc", 30, False, "sub_focus"),
        ("neural network superconductor properties", 25, False, "sub_focus"),
        ("density functional theory superconductor", 30, False, "sub_focus"),
        ("ab initio superconductor calculation", 25, False, "sub_focus"),
        ("computational prediction superconductor", 25, False, "sub_focus"),
        ("materials informatics superconductor", 20, False, "sub_focus"),
        ("deep learning crystal structure superconductor", 25, False, "sub_focus"),
        ("high-throughput screening superconductor", 25, False, "sub_focus"),
        
        # ===== SUPERCONDUCTOR APPLICATIONS (30 papers) =====
        ("superconducting qubit quantum computing", 25, False, "main"),
        ("superconducting magnet MRI", 20, False, "main"),
        ("superconductor power transmission", 20, False, "main"),
        ("superconducting cavity", 15, False, "main"),
        ("Maglev superconductor", 15, False, "main"),
        ("superconducting electronics", 20, False, "main"),
    ]
    
    reviews = []
    research = []
    seen_ids = set()
    
    for query_idx, (query, max_results, prefer_reviews, focus_area) in enumerate(search_queries, 1):
        if len(reviews) >= TARGET_COUNTS["arxiv_reviews"] and \
           len(research) >= TARGET_COUNTS["arxiv_research"]:
            break
        
        print(f"\n📖 [{query_idx}/{len(search_queries)}] '{query}' ({focus_area})")
        
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            for paper in search.results():
                if paper.entry_id in seen_ids:
                    continue
                seen_ids.add(paper.entry_id)
                
                is_review = is_review_paper(paper.title, paper.summary)
                
                if is_review and len(reviews) < TARGET_COUNTS["arxiv_reviews"]:
                    category = "review"
                    target_list = reviews
                elif not is_review and len(research) < TARGET_COUNTS["arxiv_research"]:
                    category = "research"
                    target_list = research
                else:
                    continue
                
                doc = {
                    "id": f"arxiv_{paper.entry_id.split('/')[-1]}",
                    "source": "arxiv",
                    "type": category,
                    "focus_area": focus_area,
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "abstract": paper.summary,
                    "content": paper.summary,
                    "url": paper.entry_id,
                    "pdf_url": paper.pdf_url,
                    "published": paper.published.isoformat(),
                    "year": paper.published.year,
                    "categories": paper.categories,
                    "difficulty_level": 4,  # arXiv papers are advanced
                    "collected_at": datetime.now().isoformat()
                }
                
                target_list.append(doc)
                print(f"  {'📘' if is_review else '📄'} {paper.title[:55]}...")
            
            time.sleep(3)  # arXiv rate limiting
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")
    
    print(f"\n✅ arXiv: {len(reviews)} reviews + {len(research)} research")
    return {"reviews": reviews, "research": research}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_review_paper(title: str, abstract: str) -> bool:
    """Determine if paper is a review."""
    review_keywords = [
        'review', 'survey', 'overview', 'perspective', 'tutorial',
        'progress', 'recent advances', 'state of the art'
    ]
    
    title_lower = title.lower()
    for keyword in review_keywords:
        if keyword in title_lower:
            return True
    
    abstract_lower = abstract.lower()
    return sum(1 for kw in review_keywords if kw in abstract_lower) >= 2


def save_documents(all_docs: List[Dict], filename: str):
    """Save documents to JSON."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, indent=2, ensure_ascii=False)
    
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"\n💾 Saved: {filepath} ({file_size_mb:.1f} MB)")


def print_summary(all_docs: List[Dict]):
    """Print collection summary."""
    print("\n" + "="*80)
    print("📊 SUPERCONDUCTOR COLLECTION SUMMARY")
    print("="*80)
    
    by_source = {}
    by_focus = {}
    total_words = 0
    
    for doc in all_docs:
        source = doc['source']
        by_source[source] = by_source.get(source, 0) + 1
        
        focus = doc.get('focus_area', 'main')
        by_focus[focus] = by_focus.get(focus, 0) + 1
        
        total_words += doc.get('word_count', len(doc.get('content', '').split()))
    
    total_target = sum(TARGET_COUNTS.values())
    print(f"\n✅ Total Documents: {len(all_docs)}")
    print(f"   Target: {total_target} | Achievement: {len(all_docs)/total_target*100:.1f}%")
    
    print(f"\n📁 By Source:")
    for source, count in sorted(by_source.items()):
        print(f"   {source:15s}: {count:3d}")
    
    print(f"\n🎯 By Focus Area:")
    focus_names = {
        "main": "Main (Superconductors)",
        "sub_focus": "Sub-Focus (AI/ML)",
        "hot_topic": "Hot Topic (Room-Temp)"
    }
    for focus, count in sorted(by_focus.items()):
        print(f"   {focus_names.get(focus, focus):30s}: {count:3d} ({count/len(all_docs)*100:.1f}%)")
    
    print(f"\n📝 Total Content: {total_words:,} words")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution."""
    print(f"\n⏱️  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Estimated time: 30-40 minutes\n")
    
    start_time = time.time()
    
    # Phase 1: Wikipedia (superconductors only)
    wikipedia_docs = scrape_wikipedia()
    time.sleep(2)
    
    # Phase 2: YouTube (superconductors + AI + room-temp)
    youtube_docs = scrape_youtube()
    time.sleep(2)
    
    # Phase 3: arXiv (superconductors only)
    arxiv_docs = scrape_arxiv()
    
    # Combine all
    all_documents = (
        wikipedia_docs +
        youtube_docs +
        arxiv_docs["reviews"] +
        arxiv_docs["research"]
    )
    
    # Save
    save_documents(all_documents, "superconductor_pure_300.json")
    
    # Summary
    print_summary(all_documents)
    
    elapsed = (time.time() - start_time) / 60
    print(f"\n⏱️  Completed in: {elapsed:.1f} minutes")
    
    print("\n" + "="*80)
    print("✅ PURE SUPERCONDUCTOR COLLECTION COMPLETE!")
    print("="*80)
    
    print(f"\n📁 Output: {OUTPUT_DIR}/superconductor_pure_300.json")
    
    print("\n📝 Next Steps:")
    print("   1. ✅ Data collection (300 superconductor docs)")
    print("   2. ⏭️  Generate 2,400 queries")
    print("   3. ⏭️  Train Word2Vec")
    print("   4. ⏭️  Build FAISS index")
    print("   5. ⏭️  Streamlit UI\n")


if __name__ == "__main__":
    main()