import os
import hashlib
import requests
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import feedparser
from bs4 import BeautifulSoup
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class AIResearcher:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'demodb'),
            'user': os.getenv('DB_USER', 'admin'),
            'password': os.getenv('DB_PASSWORD', 'password123')
        }
        
        self.ai_news_sources = [
            'https://feeds.feedburner.com/oreilly/radar',
            'https://blog.openai.com/rss/',
            'https://ai.googleblog.com/feeds/posts/default',
            'https://blog.anthropic.com/rss',
            'https://www.deepmind.com/blog/rss.xml',
            'https://openai.com/blog/rss/',
        ]
        
        self.search_terms = [
            "latest AI developments 2024",
            "OpenAI GPT updates",
            "Google Gemini AI",
            "Anthropic Claude updates", 
            "Microsoft AI news",
            "AI model releases",
            "machine learning breakthroughs"
        ]

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None

    def extract_vendor_from_url(self, url: str) -> str:
        """Extract vendor name from URL"""
        domain = urlparse(url).netloc.lower()
        if 'openai' in domain:
            return 'OpenAI'
        elif 'google' in domain or 'googleblog' in domain:
            return 'Google'
        elif 'anthropic' in domain:
            return 'Anthropic'
        elif 'microsoft' in domain:
            return 'Microsoft'
        elif 'deepmind' in domain:
            return 'DeepMind'
        elif 'nvidia' in domain:
            return 'NVIDIA'
        elif 'meta' in domain or 'facebook' in domain:
            return 'Meta'
        else:
            return 'Other'

    def generate_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()

    def analyze_content_with_ai(self, title: str, content: str, url: str) -> Dict:
        """Use OpenAI to analyze and categorize AI content"""
        prompt = f"""
        Analyze this AI-related article and provide:
        1. A concise summary (2-3 sentences)
        2. Category (one of: LLM, computer-vision, robotics, research, product-release, general)
        3. Relevant tags (max 5, comma-separated)
        4. Importance score (1-10)

        Title: {title}
        Content: {content[:2000]}...
        URL: {url}

        Respond in this exact format:
        SUMMARY: [your summary]
        CATEGORY: [category]
        TAGS: [tag1, tag2, tag3]
        IMPORTANCE: [score]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Parse the response
            lines = content.strip().split('\n')
            result = {}
            
            for line in lines:
                if line.startswith('SUMMARY:'):
                    result['summary'] = line.replace('SUMMARY:', '').strip()
                elif line.startswith('CATEGORY:'):
                    result['category'] = line.replace('CATEGORY:', '').strip()
                elif line.startswith('TAGS:'):
                    tags_str = line.replace('TAGS:', '').strip()
                    result['tags'] = [tag.strip() for tag in tags_str.split(',')]
                elif line.startswith('IMPORTANCE:'):
                    try:
                        result['importance'] = int(line.replace('IMPORTANCE:', '').strip())
                    except:
                        result['importance'] = 5
            
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                'summary': f"AI-related content from {self.extract_vendor_from_url(url)}",
                'category': 'general',
                'tags': ['ai', 'news'],
                'importance': 5
            }

    def scrape_web_content(self, url: str) -> Optional[str]:
        """Scrape content from web page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:3000]  # Limit content size
            
        except Exception as e:
            print(f"Web scraping error for {url}: {e}")
            return None

    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch articles from RSS feeds"""
        articles = []
        
        for feed_url in self.ai_news_sources:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Latest 5 articles per feed
                    content = ""
                    if hasattr(entry, 'content'):
                        content = entry.content[0].value if entry.content else ""
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    articles.append({
                        'title': entry.title,
                        'url': entry.link,
                        'content': content,
                        'published': getattr(entry, 'published', str(datetime.now()))
                    })
                    
            except Exception as e:
                print(f"RSS feed error for {feed_url}: {e}")
                continue
        
        return articles

    def store_research_result(self, article_data: Dict):
        """Store research result in database"""
        conn = self.connect_db()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cur:
                # Check if URL already exists
                cur.execute("SELECT id FROM ai_research WHERE url = %s", (article_data['url'],))
                if cur.fetchone():
                    print(f"Article already exists: {article_data['title'][:50]}...")
                    return True
                
                # Insert new article
                insert_query = """
                INSERT INTO ai_research (title, summary, vendor, url, content_hash, 
                                       research_date, tags, category, source_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cur.execute(insert_query, (
                    article_data['title'],
                    article_data.get('summary', ''),
                    article_data.get('vendor', ''),
                    article_data['url'],
                    article_data.get('content_hash', ''),
                    datetime.now(),
                    article_data.get('tags', []),
                    article_data.get('category', 'general'),
                    article_data.get('source_type', 'web')
                ))
                
                conn.commit()
                print(f"Stored: {article_data['title'][:50]}...")
                return True
                
        except Exception as e:
            print(f"Database storage error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def research_ai_news(self):
        """Main research function"""
        print("Starting AI research...")
        
        # Fetch from RSS feeds
        articles = self.fetch_rss_feeds()
        
        processed_count = 0
        for article in articles:
            try:
                # Get additional content if needed
                if len(article['content']) < 200:
                    web_content = self.scrape_web_content(article['url'])
                    if web_content:
                        article['content'] = web_content
                
                # Analyze with AI
                analysis = self.analyze_content_with_ai(
                    article['title'], 
                    article['content'], 
                    article['url']
                )
                
                # Prepare data for storage
                article_data = {
                    'title': article['title'],
                    'url': article['url'],
                    'vendor': self.extract_vendor_from_url(article['url']),
                    'content_hash': self.generate_content_hash(article['content']),
                    'source_type': 'rss',
                    **analysis
                }
                
                # Store in database
                if self.store_research_result(article_data):
                    processed_count += 1
                    
            except Exception as e:
                print(f"Error processing article: {e}")
                continue
        
        print(f"Research completed. Processed {processed_count} articles.")

    def get_recent_research(self, limit: int = 10, vendor: Optional[str] = None) -> List[Dict]:
        """Get recent research results from database"""
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if vendor:
                    cur.execute("""
                        SELECT * FROM ai_research 
                        WHERE vendor = %s
                        ORDER BY research_date DESC 
                        LIMIT %s
                    """, (vendor, limit))
                else:
                    cur.execute("""
                        SELECT * FROM ai_research 
                        ORDER BY research_date DESC 
                        LIMIT %s
                    """, (limit,))
                
                return [dict(row) for row in cur.fetchall()]
                
        except Exception as e:
            print(f"Database query error: {e}")
            return []
        finally:
            conn.close()