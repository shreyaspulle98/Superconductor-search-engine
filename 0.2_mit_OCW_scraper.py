"""
MIT OpenCourseWare Scraper for Superconductor Search Engine
Scrapes lecture notes, readings, and course materials from MIT OCW
"""

import os
import json
import time
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class MITOCWScraper:
    def __init__(self):
        """Initialize MIT OCW scraper."""
        self.base_url = "https://ocw.mit.edu"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def get_relevant_courses(self):
        """Define MIT OCW courses relevant to superconductors and materials science."""
        courses = {
            # === CORE MATERIALS SCIENCE ===
            'materials_science': [
                {
                    'url': 'https://ocw.mit.edu/courses/3-091sc-introduction-to-solid-state-chemistry-fall-2010/',
                    'code': '3.091SC',
                    'name': 'Introduction to Solid State Chemistry',
                    'focus': 'main',
                    'priority': 'high'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/3-012-fundamentals-of-materials-science-fall-2005/',
                    'code': '3.012',
                    'name': 'Fundamentals of Materials Science',
                    'focus': 'main',
                    'priority': 'high'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/3-22-mechanical-behavior-of-materials-spring-2008/',
                    'code': '3.22',
                    'name': 'Mechanical Behavior of Materials',
                    'focus': 'main',
                    'priority': 'medium'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/3-014-materials-laboratory-fall-2006/',
                    'code': '3.014',
                    'name': 'Materials Laboratory',
                    'focus': 'main',
                    'priority': 'medium'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/3-021j-introduction-to-modeling-and-simulation-spring-2012/',
                    'code': '3.021J',
                    'name': 'Introduction to Modeling and Simulation',
                    'focus': 'sub_focus',
                    'priority': 'high'
                },
            ],
            
            # === SOLID STATE PHYSICS & CONDENSED MATTER ===
            'solid_state': [
                {
                    'url': 'https://ocw.mit.edu/courses/8-231-physics-of-solids-i-fall-2006/',
                    'code': '8.231',
                    'name': 'Physics of Solids I',
                    'focus': 'main',
                    'priority': 'high'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/8-232-physics-of-solids-ii-spring-2007/',
                    'code': '8.232',
                    'name': 'Physics of Solids II',
                    'focus': 'main',
                    'priority': 'high'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/8-512-theory-of-solids-ii-spring-2009/',
                    'code': '8.512',
                    'name': 'Theory of Solids II',
                    'focus': 'main',
                    'priority': 'high'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/8-514-many-body-theory-for-condensed-matter-systems-fall-2004/',
                    'code': '8.514',
                    'name': 'Many-Body Theory for Condensed Matter Systems',
                    'focus': 'main',
                    'priority': 'medium'
                },
            ],
            
            # === QUANTUM MECHANICS (MATERIALS FOCUS) ===
            'quantum': [
                {
                    'url': 'https://ocw.mit.edu/courses/8-04-quantum-physics-i-spring-2016/',
                    'code': '8.04',
                    'name': 'Quantum Physics I',
                    'focus': 'main',
                    'priority': 'medium'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/8-05-quantum-physics-ii-fall-2013/',
                    'code': '8.05',
                    'name': 'Quantum Physics II',
                    'focus': 'main',
                    'priority': 'medium'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/8-06-quantum-physics-iii-spring-2018/',
                    'code': '8.06',
                    'name': 'Quantum Physics III',
                    'focus': 'main',
                    'priority': 'low'
                },
            ],
            
            # === COMPUTATIONAL & AI FOR MATERIALS ===
            'computational': [
                {
                    'url': 'https://ocw.mit.edu/courses/3-320-atomistic-computer-modeling-of-materials-sma-5107-spring-2005/',
                    'code': '3.320',
                    'name': 'Atomistic Computer Modeling of Materials',
                    'focus': 'sub_focus',
                    'priority': 'high'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/3-021j-introduction-to-modeling-and-simulation-spring-2012/',
                    'code': '3.021J',
                    'name': 'Introduction to Modeling and Simulation',
                    'focus': 'sub_focus',
                    'priority': 'high'
                },
            ],
            
            # === STATISTICAL MECHANICS & THERMODYNAMICS ===
            'stat_mech': [
                {
                    'url': 'https://ocw.mit.edu/courses/8-333-statistical-mechanics-i-statistical-mechanics-of-particles-fall-2013/',
                    'code': '8.333',
                    'name': 'Statistical Mechanics I',
                    'focus': 'main',
                    'priority': 'medium'
                },
                {
                    'url': 'https://ocw.mit.edu/courses/8-334-statistical-mechanics-ii-statistical-physics-of-fields-spring-2014/',
                    'code': '8.334',
                    'name': 'Statistical Mechanics II',
                    'focus': 'main',
                    'priority': 'low'
                },
            ],
            
            # === APPLIED SUPERCONDUCTIVITY (IF AVAILABLE) ===
            'superconductivity': [
                {
                    'url': 'https://ocw.mit.edu/courses/6-763-applied-superconductivity-fall-2005/',
                    'code': '6.763',
                    'name': 'Applied Superconductivity',
                    'focus': 'main',
                    'priority': 'critical'  # Most relevant!
                },
            ],
        }
        
        return courses
    
    def get_course_structure(self, course_url):
        """Get the structure of a course (syllabus, lecture notes, readings)."""
        try:
            response = self.session.get(course_url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            structure = {
                'lecture_notes': [],
                'readings': [],
                'assignments': [],
                'exams': []
            }
            
            # Find all navigation links
            nav_links = soup.find_all('a', href=True)
            
            for link in nav_links:
                href = link['href']
                text = link.get_text().lower()
                
                # Make URL absolute
                if not href.startswith('http'):
                    href = urljoin(course_url, href)
                
                # Categorize links
                if 'lecture' in text or 'notes' in text:
                    structure['lecture_notes'].append({
                        'title': link.get_text().strip(),
                        'url': href
                    })
                elif 'reading' in text:
                    structure['readings'].append({
                        'title': link.get_text().strip(),
                        'url': href
                    })
                elif 'assignment' in text or 'problem' in text or 'pset' in text:
                    structure['assignments'].append({
                        'title': link.get_text().strip(),
                        'url': href
                    })
                elif 'exam' in text or 'quiz' in text:
                    structure['exams'].append({
                        'title': link.get_text().strip(),
                        'url': href
                    })
            
            return structure
            
        except Exception as e:
            print(f"    ❌ Error getting course structure: {str(e)[:60]}")
            return None
    
    def scrape_page_content(self, url, title=""):
        """Scrape text content from a page."""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Try to find main content area
            main_content = None
            
            # Common content containers in MIT OCW
            content_selectors = [
                'div.main-content',
                'article',
                'div.course-content',
                'div#course-content',
                'div.body',
                'main',
                'div#main'
            ]
            
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            # Fallback to body
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                return None
            
            # Extract text
            text = main_content.get_text(separator=' ', strip=True)
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean line breaks
            
            return text
            
        except Exception as e:
            print(f"      ❌ Error scraping page: {str(e)[:50]}")
            return None
    
    def scrape_course_materials(self, course_info):
        """Scrape all materials from a single course."""
        print(f"\n📚 Course: {course_info['code']} - {course_info['name']}")
        print(f"   Priority: {course_info['priority'].upper()}")
        
        documents = []
        
        # Get course structure
        print("   📋 Getting course structure...")
        structure = self.get_course_structure(course_info['url'])
        
        if not structure:
            print("   ❌ Could not get course structure")
            return documents
        
        # Count available materials
        total_materials = (
            len(structure['lecture_notes']) + 
            len(structure['readings']) + 
            len(structure['assignments'])
        )
        
        print(f"   Found: {len(structure['lecture_notes'])} lectures, "
              f"{len(structure['readings'])} readings, "
              f"{len(structure['assignments'])} assignments")
        
        if total_materials == 0:
            print("   ⚠️  No materials found")
            return documents
        
        # Scrape lecture notes
        print(f"   📝 Scraping lecture notes...")
        for idx, lecture in enumerate(structure['lecture_notes'][:20], 1):  # Limit to 20 per type
            try:
                content = self.scrape_page_content(lecture['url'], lecture['title'])
                
                if not content or len(content.split()) < 50:
                    continue
                
                doc_data = {
                    'id': f"mit_ocw_{course_info['code']}_{idx}",
                    'source': 'mit_ocw',
                    'type': 'lecture_notes',
                    'content': {
                        'title': lecture['title'],
                        'full_text': content,
                        'url': lecture['url']
                    },
                    'metadata': {
                        'course_code': course_info['code'],
                        'course_name': course_info['name'],
                        'institution': 'MIT',
                        'material_type': 'lecture_notes'
                    },
                    'categorization': {
                        'material': 'superconductors',
                        'focus_type': course_info['focus']
                    },
                    'quality_metrics': {
                        'word_count': len(content.split()),
                        'reading_time_minutes': len(content.split()) // 200
                    }
                }
                
                documents.append(doc_data)
                print(f"      [{len(documents):3d}] {lecture['title'][:50]:<50} | {len(content.split()):5d} words ✅")
                
                time.sleep(1)  # Be polite to MIT servers
                
            except Exception as e:
                print(f"      ❌ Failed: {lecture['title'][:50]} - {str(e)[:30]}")
        
        # Scrape readings
        print(f"   📖 Scraping readings...")
        for idx, reading in enumerate(structure['readings'][:10], 1):  # Limit to 10
            try:
                content = self.scrape_page_content(reading['url'], reading['title'])
                
                if not content or len(content.split()) < 50:
                    continue
                
                doc_data = {
                    'id': f"mit_ocw_{course_info['code']}_reading_{idx}",
                    'source': 'mit_ocw',
                    'type': 'reading',
                    'content': {
                        'title': reading['title'],
                        'full_text': content,
                        'url': reading['url']
                    },
                    'metadata': {
                        'course_code': course_info['code'],
                        'course_name': course_info['name'],
                        'institution': 'MIT',
                        'material_type': 'reading'
                    },
                    'categorization': {
                        'material': 'superconductors',
                        'focus_type': course_info['focus']
                    },
                    'quality_metrics': {
                        'word_count': len(content.split()),
                        'reading_time_minutes': len(content.split()) // 200
                    }
                }
                
                documents.append(doc_data)
                print(f"      [{len(documents):3d}] {reading['title'][:50]:<50} | {len(content.split()):5d} words ✅")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"      ❌ Failed: {reading['title'][:50]} - {str(e)[:30]}")
        
        print(f"   ✅ Collected {len(documents)} documents from this course")
        return documents
    
    def scrape_all_courses(self):
        """Scrape all relevant MIT OCW courses."""
        print("\n" + "="*80)
        print("🎓 MIT OCW SCRAPER - Materials Science & Superconductivity")
        print("="*80)
        print("🎯 Target: 100+ lecture notes and readings\n")
        
        all_courses = self.get_relevant_courses()
        all_documents = []
        
        # Count total courses
        total_courses = sum(len(courses) for courses in all_courses.values())
        course_count = 0
        
        print(f"📊 Found {total_courses} relevant courses\n")
        
        # Scrape by priority
        priority_order = ['critical', 'high', 'medium', 'low']
        
        for priority in priority_order:
            print(f"\n{'='*80}")
            print(f"🎯 Priority: {priority.upper()}")
            print(f"{'='*80}")
            
            for category, courses in all_courses.items():
                for course in courses:
                    if course['priority'] != priority:
                        continue
                    
                    course_count += 1
                    print(f"\n[{course_count}/{total_courses}] Processing...")
                    
                    docs = self.scrape_course_materials(course)
                    all_documents.extend(docs)
                    
                    print(f"   Running total: {len(all_documents)} documents")
                    
                    # Be extra polite between courses
                    time.sleep(2)
        
        # Calculate statistics
        print("\n" + "="*80)
        print("📊 CALCULATING STATISTICS")
        print("="*80)
        
        total_words = sum(d['quality_metrics']['word_count'] for d in all_documents)
        
        focus_breakdown = {
            'main': len([d for d in all_documents if d['categorization']['focus_type'] == 'main']),
            'sub_focus': len([d for d in all_documents if d['categorization']['focus_type'] == 'sub_focus']),
        }
        
        type_breakdown = {
            'lecture_notes': len([d for d in all_documents if d['type'] == 'lecture_notes']),
            'reading': len([d for d in all_documents if d['type'] == 'reading']),
        }
        
        course_breakdown = {}
        for doc in all_documents:
            course = doc['metadata']['course_code']
            course_breakdown[course] = course_breakdown.get(course, 0) + 1
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'mit_ocw_{timestamp}.json'
        
        output_data = {
            'metadata': {
                'scrape_date': datetime.now().isoformat(),
                'total_documents': len(all_documents),
                'total_words': total_words,
                'average_words_per_doc': total_words // len(all_documents) if all_documents else 0,
                'courses_scraped': course_count,
                'focus_breakdown': focus_breakdown,
                'type_breakdown': type_breakdown,
                'course_breakdown': course_breakdown
            },
            'documents': all_documents
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Print final summary
        print("\n" + "="*80)
        print("✅ SCRAPING COMPLETE!")
        print("="*80)
        print(f"📊 Final Statistics:")
        print(f"   Documents collected: {len(all_documents):,}")
        print(f"   Total words: {total_words:,}")
        print(f"   Average words/doc: {total_words//len(all_documents) if all_documents else 0:,}")
        print(f"   ")
        print(f"   By Type:")
        print(f"     Lecture Notes: {type_breakdown['lecture_notes']}")
        print(f"     Readings:      {type_breakdown['reading']}")
        print(f"   ")
        print(f"   By Focus:")
        print(f"     Main (Physics/Materials): {focus_breakdown['main']}")
        print(f"     Sub-focus (Computational): {focus_breakdown['sub_focus']}")
        print(f"   ")
        print(f"   By Course:")
        for course, count in sorted(course_breakdown.items(), key=lambda x: x[1], reverse=True):
            print(f"     {course}: {count}")
        print(f"   ")
        print(f"💾 Saved to: {output_file}")
        
        return all_documents


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    print("🎓 Initializing MIT OCW Scraper...")
    print("⚠️  Note: This will take 30-60 minutes due to polite rate limiting\n")
    
    # Initialize scraper
    scraper = MITOCWScraper()
    
    # Run scraper
    documents = scraper.scrape_all_courses()
    
    print("\n" + "="*80)
    print("🎉 ALL DONE!")
    print("="*80)
    print(f"You now have {len(documents)} MIT OCW documents ready for embedding!")
    print("\nNext steps:")
    print("  1. Check the output JSON file")
    print("  2. Merge with your existing data")
    print("  3. Proceed to embedding phase")