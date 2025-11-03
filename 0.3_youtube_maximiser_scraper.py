"""
YouTube Data Maximizer for Superconductor Search Engine - ROBUST VERSION
=====================================================================

This version includes:
✅ Secure API key handling (environment variables)
✅ Comprehensive error handling
✅ Conservative rate limiting to avoid blocks
✅ Checkpoint system (resume if interrupted)
✅ Better logging and progress tracking
✅ Graceful degradation when errors occur

"""

import os
import json
import time
import sys
import logging
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Set up logging with unbuffered output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_scraper.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None


class YouTubeMaximizerRobust:
    def __init__(self, api_key=None):
        """
        Initialize with YouTube API key.
        
        Args:
            api_key: YouTube Data API v3 key. If None, reads from environment variable.
        """
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get('YOUTUBE_API_KEY')
        
        # Validate API key exists
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError(
                "❌ ERROR: No valid YouTube API key provided!\n"
                "   Set environment variable: export YOUTUBE_API_KEY='your-key-here'\n"
                "   Or pass it directly: YouTubeMaximizerRobust(api_key='your-key')"
            )
        
        # Initialize YouTube API client (skip validation to save quota)
        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            print("✅ API client initialized (validation skipped to save quota)")
        except Exception as e:
            raise ValueError(f"❌ ERROR: Could not initialize YouTube API: {e}")
        
        self.quota_used = 0
        self.quota_limit = 9900  # Leave 100 units buffer
        self.checkpoint_file = 'youtube_scrape_checkpoint.json'
        
        # Statistics tracking
        self.stats = {
            'searches_completed': 0,
            'videos_found': 0,
            'transcripts_checked': 0,
            'transcripts_available': 0,
            'details_fetched': 0,
            'final_videos': 0,
            'errors': {
                'search_errors': 0,
                'transcript_errors': 0,
                'detail_errors': 0
            }
        }
        
    def get_comprehensive_search_queries(self):
        """Generate comprehensive search queries for superconductors."""
        queries = {
            # === FUNDAMENTALS (25 queries - ENHANCED with educational content) ===
            'fundamentals': [
                'superconductivity explained',
                'what is a superconductor',
                'how do superconductors work',
                'superconductor physics',
                'quantum mechanics superconductivity',
                'zero electrical resistance',
                'superconductor applications',
                'superconductor properties',
                'introduction to superconductivity',
                'superconductor materials science',
                'superconductivity lecture',
                'superconductor tutorial',
                'superconductor basics',
                'superconducting materials',
                'superconductor discovery',
                'history of superconductivity',
                'superconductor temperature',
                'critical temperature superconductor',
                'superconductor magnetic field',
                'superconductor quantum',
                # NEW: Educational/beginner queries
                'superconductor for beginners',
                'superconductor explained simply',
                'superconductor course',
                'superconductor lesson',
                'understanding superconductivity',
            ],
            
            # === BCS THEORY & MECHANISMS (15 queries) ===
            'theory': [
                'BCS theory superconductivity',
                'Cooper pairs explained',
                'electron phonon coupling',
                'superconducting gap',
                'BCS theory lecture',
                'quantum theory superconductivity',
                'phonon mediated pairing',
                'Cooper pair formation',
                'BCS ground state',
                'superconducting transition',
                'BCS Hamiltonian',
                'Bardeen Cooper Schrieffer',
                'superconductivity theory',
                'microscopic theory superconductivity',
                'quantum condensation superconductor',
            ],
            
            # === MEISSNER EFFECT (10 queries) ===
            'meissner': [
                'Meissner effect explained',
                'Meissner effect demonstration',
                'superconductor levitation',
                'magnetic levitation superconductor',
                'quantum levitation',
                'flux expulsion superconductor',
                'perfect diamagnetism',
                'Meissner Ochsenfeld effect',
                'superconductor magnet levitation',
                'floating superconductor',
            ],
            
            # === TYPES OF SUPERCONDUCTORS (12 queries) ===
            'types': [
                'Type I superconductor',
                'Type II superconductor',
                'Type I vs Type II',
                'vortex state superconductor',
                'flux pinning',
                'Abrikosov vortex',
                'mixed state superconductivity',
                'hard superconductors',
                'soft superconductors',
                'conventional superconductor',
                'unconventional superconductor',
                's-wave d-wave superconductor',
            ],
            
            # === HIGH-Tc SUPERCONDUCTORS (15 queries) ===
            'high_tc': [
                'high temperature superconductor',
                'cuprate superconductor',
                'YBCO superconductor',
                'BSCCO superconductor',
                'ceramic superconductor',
                'iron based superconductor',
                'pnictide superconductor',
                'FeSe superconductor',
                'nickelate superconductor',
                'high Tc mechanism',
                'cuprate physics',
                'YBCO synthesis',
                'liquid nitrogen superconductor',
                '77K superconductor',
                'perovskite superconductor',
            ],
            
            # === ROOM TEMPERATURE (HOT TOPIC) (20 queries) ===
            'room_temp': [
                'room temperature superconductor',
                'ambient superconductor',
                'LK-99 superconductor',
                'LK99 explained',
                'room temperature superconductivity',
                'hydrogen rich superconductor',
                'high pressure superconductor',
                'carbonaceous sulfur hydride',
                'CSH superconductor',
                'H3S superconductor',
                'lanthanum hydride superconductor',
                'diamond anvil superconductor',
                'superhydride superconductor',
                'metallic hydrogen superconductor',
                'Ranga Dias superconductor',
                'room temp superconductor 2024',
                'room temp superconductor 2023',
                'room temp superconductor breakthrough',
                'ambient pressure superconductor',
                'practical superconductor',
            ],
            
            # === APPLICATIONS (12 queries) ===
            'applications': [
                'superconductor applications',
                'superconducting magnet',
                'MRI superconductor',
                'particle accelerator superconductor',
                'superconducting quantum computer',
                'superconductor power grid',
                'maglev train superconductor',
                'superconducting cable',
                'SQUID superconductor',
                'Josephson junction',
                'superconducting electronics',
                'superconductor fusion reactor',
            ],
            
            # === AI & MATERIALS SCIENCE (15 queries) ===
            'ai_ml': [
                'AI materials discovery',
                'machine learning superconductor',
                'AI predict superconductor',
                'materials informatics',
                'computational materials science',
                'DFT superconductor',
                'density functional theory materials',
                'machine learning materials',
                'AI discover new materials',
                'neural network materials',
                'deep learning chemistry',
                'materials genome initiative',
                'high throughput materials',
                'AI chemistry discovery',
                'ML predict Tc superconductor',
            ],
            
            # === EXPERIMENTS & DEMOS (10 queries) ===
            'experiments': [
                'superconductor experiment',
                'making superconductor',
                'DIY superconductor',
                'superconductor demonstration',
                'liquid nitrogen superconductor demo',
                'YBCO synthesis lab',
                'superconductor liquid nitrogen',
                'superconductor cooling',
                'cryogenic superconductor',
                'superconductor lab demo',
            ],

            # === EDUCATIONAL INSTITUTIONS (15 queries - NEW) ===
            'educational': [
                'MIT superconductor lecture',
                'Stanford superconductivity',
                'Berkeley physics superconductor',
                'Caltech superconductor',
                'Princeton superconductivity course',
                'Yale superconductor physics',
                'Cambridge superconductivity',
                'Oxford superconductor',
                'superconductor university lecture',
                'superconductor physics course',
                'quantum mechanics superconductor lecture',
                'condensed matter superconductor',
                'solid state physics superconductor',
                'graduate superconductivity',
                'undergraduate superconductor',
            ],
        }

        return queries
    
    def save_checkpoint(self, data):
        """Save checkpoint to resume later if interrupted."""
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save checkpoint: {e}")
    
    def load_checkpoint(self):
        """Load checkpoint if exists."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def search_videos(self, query, max_results=50):
        """
        Search YouTube for videos with error handling.
        
        Returns:
            list: Video IDs found, or empty list if error
        """
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id',
                type='video',
                maxResults=max_results,
                relevanceLanguage='en',
                videoCaption='closedCaption',  # Prefer videos with captions
                order='relevance'
            ).execute()
            
            self.quota_used += 100  # Search costs 100 units
            
            video_ids = [
                item['id']['videoId'] 
                for item in search_response.get('items', [])
            ]
            
            self.stats['searches_completed'] += 1
            self.stats['videos_found'] += len(video_ids)
            
            return video_ids
            
        except HttpError as e:
            self.stats['errors']['search_errors'] += 1
            if e.resp.status == 403:
                print(f"    ❌ Quota exceeded! Used {self.quota_used}/{self.quota_limit}")
                return None  # Signal to stop
            else:
                print(f"    ❌ Search error (HTTP {e.resp.status}): {str(e)[:60]}")
                return []
        except Exception as e:
            self.stats['errors']['search_errors'] += 1
            print(f"    ❌ Unexpected search error: {str(e)[:60]}")
            return []
    
    def check_transcript_availability(self, video_id):
        """
        Check if transcript is available (doesn't use API quota).

        IMPORTANT: Includes rate limiting to avoid being blocked!
        """
        try:
            # Add delay BEFORE each request to be respectful
            time.sleep(0.3)  # 300ms delay = max ~3 requests/second

            # Check if transcript exists
            YouTubeTranscriptApi.get_transcript(video_id)
            self.stats['transcripts_available'] += 1
            return True

        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
            return False
        except Exception as e:
            # Log unexpected errors occasionally
            if self.stats['errors']['transcript_errors'] < 5:
                print(f"  ⚠️  Transcript check error: {type(e).__name__}")
                self.stats['errors']['transcript_errors'] += 1
            return False
        finally:
            self.stats['transcripts_checked'] += 1
    
    def get_video_details_batch(self, video_ids):
        """
        Get video details in batches of 50 with error handling.
        
        Returns:
            list: Video details, or empty list if error
        """
        all_details = []
        
        # Process in batches of 50
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            
            try:
                video_response = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch)
                ).execute()
                
                self.quota_used += 1  # 1 unit per request (regardless of batch size)
                
                details = video_response.get('items', [])
                all_details.extend(details)
                self.stats['details_fetched'] += len(details)
                
                # Rate limiting between batches
                if i + 50 < len(video_ids):
                    time.sleep(0.5)
                
            except HttpError as e:
                self.stats['errors']['detail_errors'] += 1
                if e.resp.status == 403:
                    print(f"    ❌ Quota exceeded during details fetch!")
                    break
                else:
                    print(f"    ❌ Batch details error: {str(e)[:60]}")
            except Exception as e:
                self.stats['errors']['detail_errors'] += 1
                print(f"    ❌ Unexpected batch error: {str(e)[:60]}")
        
        return all_details
    
    def get_transcript(self, video_id):
        """
        Get transcript for a video (free - no API quota).

        Returns:
            str: Full transcript text, or None if unavailable
        """
        try:
            # Rate limiting
            time.sleep(0.3)

            # Get transcript and extract text
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript_list])
            return full_text
        except:
            return None

    def _infer_difficulty_level(self, title, description, transcript, channel, duration):
        """
        Infer difficulty level (1-5) based on video characteristics.

        1-2: Beginner (introductory, simple explanations)
        3: Intermediate (educational, some technical depth)
        4-5: Expert (research talks, advanced theory)
        """
        text = f"{title} {description} {transcript[:1000]}".lower()

        # Educational channel indicators
        edu_channels = ['mit', 'stanford', 'khan', 'crashcourse', 'veritasium',
                       'minutephysics', '3blue1brown', 'physics girl']
        is_edu_channel = any(name in channel.lower() for name in edu_channels)

        # Beginner indicators
        beginner_keywords = ['basics', 'introduction', 'explained', 'simple',
                            'for beginners', 'what is', 'eli5', 'understand',
                            'tutorial', 'guide', 'how to', 'beginner']
        beginner_score = sum(1 for kw in beginner_keywords if kw in text)

        # Expert indicators
        expert_keywords = ['quantum field theory', 'hamiltonian', 'eigenvalue',
                          'renormalization', 'feynman diagram', 'perturbation theory',
                          'density functional', 'many-body', 'topological invariant',
                          'seminar', 'colloquium', 'research talk', 'arxiv']
        expert_score = sum(1 for kw in expert_keywords if kw in text)

        # Intermediate indicators
        intermediate_keywords = ['bcs theory', 'cooper pairs', 'meissner effect',
                                'lecture', 'course', 'phonon', 'lattice']
        intermediate_score = sum(1 for kw in intermediate_keywords if kw in text)

        # Parse duration (ISO 8601 format like PT15M33S)
        duration_minutes = 0
        if 'H' in duration:
            duration_minutes = 60  # Long video
        elif 'M' in duration:
            import re
            match = re.search(r'(\d+)M', duration)
            if match:
                duration_minutes = int(match.group(1))

        # Decision logic
        if expert_score >= 2:
            return 4 if is_edu_channel else 5
        elif beginner_score >= 3:
            return 1 if duration_minutes < 15 else 2
        elif intermediate_score >= 2 or is_edu_channel:
            return 3
        elif 'lecture' in text or 'course' in text:
            return 3
        elif beginner_score >= 1:
            return 2
        else:
            return 3  # Default to intermediate
    
    def scrape_maximum_videos(self):
        """
        Scrape maximum videos using all available API quota.
        
        This is the main function that orchestrates the entire scraping process.
        """
        print("\n" + "="*80)
        print("🚀 YOUTUBE MAXIMIZER - ROBUST VERSION")
        print("="*80)
        print(f"💰 API Quota: {self.quota_limit:,} units available")
        print(f"🎯 Target: 100-300 videos with transcripts")
        print(f"🔒 Security: API key loaded from environment")
        print(f"💾 Checkpoints: Enabled (can resume if interrupted)\n")
        
        # Check for existing checkpoint
        checkpoint = self.load_checkpoint()
        if checkpoint:
            print("📂 Found checkpoint from previous run!")
            print("   ✅ Automatically resuming from checkpoint...")
            all_video_ids = set(checkpoint.get('video_ids', []))
            self.quota_used = checkpoint.get('quota_used', 0)
            processed_queries = checkpoint.get('processed_queries', [])
            print(f"   Videos found so far: {len(all_video_ids)}")
            print(f"   Quota used so far: {self.quota_used}\n")
        else:
            all_video_ids = set()
            processed_queries = []
        
        # Get all search queries
        all_queries = self.get_comprehensive_search_queries()
        
        # Track data
        videos_data = []
        
        # === PHASE 1: COLLECT VIDEO IDs ===
        print("="*80)
        print("📊 PHASE 1: Searching for videos")
        print("="*80)
        
        query_count = 0
        quota_exceeded = False

        for category, queries in all_queries.items():
            if self.quota_used >= self.quota_limit:
                print("\n⚠️  Quota limit reached in Phase 1")
                break

            print(f"\n📁 Category: {category.upper()}")

            for query in queries:
                # Skip if already processed
                if query in processed_queries:
                    continue

                if self.quota_used >= self.quota_limit:
                    break

                query_count += 1
                video_ids = self.search_videos(query, max_results=50)

                # Check for quota exceeded signal
                if video_ids is None:
                    print("⚠️  Stopping searches due to quota")
                    quota_exceeded = True
                    break

                new_ids = len(video_ids)
                all_video_ids.update(video_ids)
                processed_queries.append(query)

                print(f"  [{query_count:3d}] {query[:45]:<45} → {new_ids:2d} vids | "
                      f"Total: {len(all_video_ids):4d} | "
                      f"Quota: {self.quota_used:5d}/{self.quota_limit}")

                # Save checkpoint every 10 queries
                if query_count % 10 == 0:
                    self.save_checkpoint({
                        'video_ids': list(all_video_ids),
                        'quota_used': self.quota_used,
                        'processed_queries': processed_queries,
                        'phase': 1
                    })

                # Rate limiting between searches
                time.sleep(1.0)  # Be extra careful with API

            # Break outer loop if quota exceeded
            if quota_exceeded or self.quota_used >= self.quota_limit:
                break
        
        print(f"\n✅ Phase 1 Complete:")
        print(f"   Queries executed: {self.stats['searches_completed']}")
        print(f"   Unique videos found: {len(all_video_ids):,}")
        print(f"   Quota used: {self.quota_used:,}/{self.quota_limit:,}")
        
        if len(all_video_ids) == 0:
            print("\n❌ ERROR: No videos found! Check your search queries.")
            return []
        
        # === PHASE 2: CHECK TRANSCRIPTS ===
        print("\n" + "="*80)
        print("📝 PHASE 2: Checking transcript availability (FREE - but rate limited)")
        print("="*80)
        print("⏱️  This will take a while to avoid rate limiting...")
        print(f"   Estimated time: ~{len(all_video_ids) * 0.3 / 60:.1f} minutes\n")
        
        videos_with_transcripts = []
        start_time = time.time()

        for idx, video_id in enumerate(all_video_ids, 1):
            if idx % 50 == 0:
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                remaining = (len(all_video_ids) - idx) / rate if rate > 0 else 0
                print(f"  Progress: {idx}/{len(all_video_ids)} checked "
                      f"({idx/len(all_video_ids)*100:.1f}%) | "
                      f"Found: {len(videos_with_transcripts)} | "
                      f"ETA: {remaining/60:.1f}min")

            if self.check_transcript_availability(video_id):
                videos_with_transcripts.append(video_id)
            
            # Extra pause every 20 videos to be really safe
            if idx % 20 == 0:
                time.sleep(1.0)
        
        transcript_rate = len(videos_with_transcripts)/len(all_video_ids)*100 if len(all_video_ids) > 0 else 0
        
        print(f"\n✅ Phase 2 Complete:")
        print(f"   Transcripts checked: {self.stats['transcripts_checked']:,}")
        print(f"   Transcripts available: {len(videos_with_transcripts):,}")
        print(f"   Success rate: {transcript_rate:.1f}%")
        
        if len(videos_with_transcripts) == 0:
            print("\n❌ ERROR: No videos with transcripts found!")
            return []
        
        # === PHASE 3: GET VIDEO DETAILS ===
        print("\n" + "="*80)
        print("📊 PHASE 3: Fetching video details")
        print("="*80)
        
        # Calculate how many video details we can fetch
        remaining_quota = self.quota_limit - self.quota_used
        # Each batch of 50 videos = 1 unit, so we can fetch roughly:
        max_batches = remaining_quota
        max_videos = max_batches * 50
        max_details = min(len(videos_with_transcripts), max_videos)
        
        print(f"   Remaining quota: {remaining_quota} units")
        print(f"   Can fetch details for: {max_details} videos")
        print(f"   (Fetching in batches of 50)")
        
        videos_to_fetch = videos_with_transcripts[:max_details]
        video_details = self.get_video_details_batch(videos_to_fetch)
        
        print(f"\n✅ Phase 3 Complete:")
        print(f"   Details fetched: {len(video_details)}")
        print(f"   Final quota used: {self.quota_used:,}/{self.quota_limit:,}")
        
        if len(video_details) == 0:
            print("\n❌ ERROR: Could not fetch any video details!")
            return []
        
        # === PHASE 4: GET TRANSCRIPTS & BUILD DATASET ===
        print("\n" + "="*80)
        print("📥 PHASE 4: Downloading transcripts & building dataset (FREE)")
        print("="*80)
        print(f"⏱️  Estimated time: ~{len(video_details) * 0.3 / 60:.1f} minutes\n")
        
        for idx, video_info in enumerate(video_details, 1):
            video_id = video_info['id']
            
            # Get transcript
            transcript = self.get_transcript(video_id)
            
            if not transcript:
                continue
            
            # Determine focus type based on title/description
            title = video_info['snippet']['title'].lower()
            description = video_info['snippet'].get('description', '').lower()
            combined_text = title + ' ' + description
            
            if any(term in combined_text for term in ['room temp', 'lk-99', 'lk99', 'ambient', 'breakthrough']):
                focus_type = 'hot_topic'
            elif any(term in combined_text for term in ['ai', 'machine learning', 'ml', 'computational', 'predict']):
                focus_type = 'sub_focus'
            else:
                focus_type = 'main'
            
            # Auto-categorize difficulty level
            difficulty_level = self._infer_difficulty_level(
                title, description, transcript,
                video_info['snippet']['channelTitle'],
                video_info['contentDetails']['duration']
            )

            video_data = {
                'id': f'youtube_{video_id}',
                'source': 'youtube',
                'type': 'video',
                'content': {
                    'title': video_info['snippet']['title'],
                    'transcript': transcript,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'video_id': video_id,
                    'description': video_info['snippet'].get('description', '')[:500]  # Truncate
                },
                'metadata': {
                    'channel': video_info['snippet']['channelTitle'],
                    'published_date': video_info['snippet']['publishedAt'],
                    'view_count': int(video_info['statistics'].get('viewCount', 0)),
                    'like_count': int(video_info['statistics'].get('likeCount', 0)),
                    'duration': video_info['contentDetails']['duration']
                },
                'categorization': {
                    'material': 'superconductors',
                    'focus_type': focus_type,
                    'keywords': []  # Can be populated from title analysis
                },
                'quality_metrics': {
                    'word_count': len(transcript.split()),
                    'reading_time_minutes': len(transcript.split()) // 200,
                    'technicality_score': None,  # Will be rated later by Claude
                    'difficulty_level': difficulty_level
                }
            }
            
            videos_data.append(video_data)
            self.stats['final_videos'] += 1
            
            if idx % 25 == 0:
                print(f"  Downloaded: {idx}/{len(video_details)} transcripts... "
                      f"({len(videos_data)} successful)")
        
        print(f"\n✅ Phase 4 Complete:")
        print(f"   Final dataset: {len(videos_data)} videos")
        
        # Calculate statistics
        total_words = sum(v['quality_metrics']['word_count'] for v in videos_data)
        focus_breakdown = {
            'main': len([v for v in videos_data if v['categorization']['focus_type'] == 'main']),
            'hot_topic': len([v for v in videos_data if v['categorization']['focus_type'] == 'hot_topic']),
            'sub_focus': len([v for v in videos_data if v['categorization']['focus_type'] == 'sub_focus'])
        }
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'youtube_robust_{timestamp}.json'
        
        output_data = {
            'metadata': {
                'scrape_date': datetime.now().isoformat(),
                'api_quota_used': self.quota_used,
                'api_quota_limit': self.quota_limit,
                'total_videos': len(videos_data),
                'total_words': total_words,
                'focus_breakdown': focus_breakdown,
                'statistics': self.stats,
                'queries_executed': self.stats['searches_completed'],
                'unique_videos_found': len(all_video_ids),
                'transcript_availability_rate': f"{transcript_rate:.1f}%"
            },
            'videos': videos_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Clean up checkpoint file
        if os.path.exists(self.checkpoint_file):
            try:
                os.remove(self.checkpoint_file)
                print("   Checkpoint file cleaned up")
            except:
                pass
        
        # Print final summary
        print("\n" + "="*80)
        print("✅ SCRAPING COMPLETE!")
        print("="*80)
        print(f"📊 Final Statistics:")
        print(f"   Videos collected: {len(videos_data):,}")
        print(f"   Total words: {total_words:,}")
        if len(videos_data) > 0:
            print(f"   Average words/video: {total_words//len(videos_data):,}")
        print(f"   ")
        print(f"   Focus breakdown:")
        print(f"     Main (Superconductors): {focus_breakdown['main']}")
        print(f"     Hot Topic (Room-Temp):  {focus_breakdown['hot_topic']}")
        print(f"     Sub-focus (AI/ML):      {focus_breakdown['sub_focus']}")
        print(f"   ")
        print(f"   API Usage:")
        print(f"     Quota used: {self.quota_used:,}/{self.quota_limit:,}")
        print(f"     Efficiency: {self.quota_used/self.quota_limit*100:.1f}%")
        print(f"   ")
        print(f"   Error Summary:")
        print(f"     Search errors: {self.stats['errors']['search_errors']}")
        print(f"     Transcript errors: {self.stats['errors']['transcript_errors']}")
        print(f"     Detail fetch errors: {self.stats['errors']['detail_errors']}")
        print(f"   ")
        print(f"💾 Saved to: {output_file}")
        
        return videos_data


# ========================================
# MAIN EXECUTION
# ========================================

def main():
    """Main entry point with comprehensive error handling."""
    
    print("="*80)
    print("🚀 YouTube Maximizer - Robust Version")
    print("="*80)
    print()
    
    # Check for API key in environment
    api_key = os.environ.get('YOUTUBE_API_KEY')
    
    if not api_key:
        print("❌ ERROR: YouTube API key not found!")
        print()
        print("To fix this:")
        print("  1. Get a YouTube Data API v3 key from:")
        print("     https://console.cloud.google.com/apis/credentials")
        print()
        print("  2. Set it as an environment variable:")
        print("     ")
        print("     On Mac/Linux:")
        print("       export YOUTUBE_API_KEY='your-key-here'")
        print()
        print("     On Windows:")
        print("       set YOUTUBE_API_KEY=your-key-here")
        print()
        print("  3. Run this script again")
        print()
        sys.exit(1)
    
    try:
        # Initialize maximizer
        print("🔧 Initializing YouTube Maximizer...")
        maximizer = YouTubeMaximizerRobust()
        
        # Run scraper
        videos = maximizer.scrape_maximum_videos()
        
        if len(videos) > 0:
            print("\n" + "="*80)
            print("🎉 SUCCESS!")
            print("="*80)
            print(f"✅ Collected {len(videos)} superconductor videos")
            print(f"✅ Ready for embedding and search engine integration")
        else:
            print("\n" + "="*80)
            print("⚠️  WARNING: No videos collected")
            print("="*80)
            print("This could mean:")
            print("  - Quota was exceeded early")
            print("  - Network issues")
            print("  - No videos had transcripts")
        
    except ValueError as e:
        print(f"\n{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("💾 Progress saved to checkpoint - run again to resume")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("💾 Check if checkpoint was saved to resume")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()