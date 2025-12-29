import os
from dotenv import load_dotenv
import requests
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import xml.etree.ElementTree as ET
import random
from datetime import datetime
import markdown
import re

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

# 2. Convert Markdown to HTML
def convert_markdown_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Convert italic: *text* or _text_ to <em>text</em>
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    return text

def get_blogger_service():
    creds = Credentials(
        None, 
        refresh_token=os.environ["G_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["G_CLIENT_ID"],
        client_secret=os.environ["G_CLIENT_SECRET"],
        scopes=['https://www.googleapis.com/auth/blogger']
    )
    return build('blogger', 'v3', credentials=creds)

def get_random_trending_topic():
    rss_feeds = {
        "Top Stories": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        "Business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
        "Technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
        "Entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US&ceid=US:en",
        "Sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-US&gl=US&ceid=US:en",
        "Science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US&ceid=US:en",
        "Health": "https://news.google.com/rss/headlines/section/topic/HEALTH?hl=en-US&gl=US&ceid=US:en"
    }
    
    category_name, rss_url = random.choice(list(rss_feeds.items()))
    print(f"🔍 Searching category: {category_name}...")
    
    try:
        response = requests.get(rss_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            trends = []
            for item in root.findall('.//item')[:15]:
                title = item.find('title').text
                clean_title = title.split(' - ')[0]
                trends.append(clean_title)
            
            if not trends: return None, None
            return random.choice(trends), category_name
        else:
            print(f"Error fetching RSS: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Exception fetching news: {e}")
        return None, None

def generate_content(topic, category):
    print(f"✍️ Writing blog post about: {topic}...")
    
    prompt = f"""
    You are an expert SEO content writer and professional blogger. Write a comprehensive, SEO-optimized blog post about this trending news story: "{topic}".
    The category is: {category}.
    
    CRITICAL: Use ONLY HTML tags for formatting. DO NOT use Markdown syntax like **bold** or _italic_. Use <strong>bold</strong> and <em>italic</em> instead.
    
    SEO REQUIREMENTS:
    1. Title: Create an engaging, keyword-rich H1 title (50-60 characters) that includes the main topic
    2. Meta Description: Write a compelling 150-160 character summary that includes primary keywords
    3. URL Slug: Suggest a clean, keyword-rich URL slug (lowercase, hyphens, no special chars)
    4. Primary Keywords: Identify 3-5 main keywords related to this topic
    5. Content Length: Minimum 800-1200 words for better ranking
    6. Heading Structure: Use proper H2 and H3 tags hierarchically
    7. Internal/External Links: Include 2-3 relevant external authority links
    8. Images: Suggest 2-3 relevant images with descriptive alt text
    9. FAQ Section: Add 3-5 common questions with answers
    10. Call-to-Action: End with engagement prompt
    
    Structure your response EXACTLY like this:
    
    META_DESCRIPTION: [150-160 char description with keywords]
    URL_SLUG: [keyword-rich-url-slug]
    PRIMARY_KEYWORDS: keyword1, keyword2, keyword3, keyword4, keyword5
    FOCUS_KEYPHRASE: [main 2-3 word phrase]
    
    <article>
    <header>
    <h1>[SEO-Optimized Title with Primary Keyword]</h1>
    <p class="meta"><strong>Category: {category}</strong> | <time datetime="2025-12-28">December 28, 2025</time> | 5 min read</p>
    </header>
    
    <section class="introduction">
    <p>[Engaging opening paragraph with focus keyphrase in first 100 words. Hook the reader and include primary keywords naturally.]</p>
    <p>[Second paragraph expanding on the topic with supporting keywords.]</p>
    </section>
    
    <section>
    <h2>What is [Topic]?</h2>
    <p>[Detailed explanation with keywords. 200-300 words with natural keyword density 1-2%.]</p>
    <p>[Include an external link to an authority source: <a href="URL" rel="nofollow noopener" target="_blank">source text</a>]</p>
    </section>
    
    <section>
    <h2>Key Details and Background</h2>
    <h3>The Full Story</h3>
    <p>[Comprehensive details about the topic. Use bullet points with <ul><li> tags for readability.]</p>
    <h3>Recent Developments</h3>
    <p>[Latest updates and information.]</p>
    </section>
    
    <section>
    <h2>Why This Matters</h2>
    <p>[Analysis of significance and impact. Include secondary keywords naturally.]</p>
    <p>[Add another external authority link for credibility.]</p>
    </section>
    
    <section>
    <h2>Expert Analysis and Insights</h2>
    <p>[In-depth analysis with unique perspective. Add value beyond basic news reporting.]</p>
    </section>
    
    <section class="faq">
    <h2>Frequently Asked Questions</h2>
    <div itemscope itemtype="https://schema.org/FAQPage">
    <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
    <h3 itemprop="name">Q: [Question about topic]?</h3>
    <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
    <p itemprop="text">[Detailed answer with keywords]</p>
    </div>
    </div>
    [Repeat for 3-5 questions]
    </div>
    </section>
    
    <section class="conclusion">
    <h2>Final Thoughts</h2>
    <p>[Summary with primary keywords. Reinforce main points.]</p>
    <p><strong>What do you think about [topic]? Share your thoughts in the comments below!</strong></p>
    </section>
    
    <section class="related-topics">
    <h2>Related Topics You Might Like</h2>
    <ul>
    <li><a href="#">[Related topic 1]</a></li>
    <li><a href="#">[Related topic 2]</a></li>
    <li><a href="#">[Related topic 3]</a></li>
    </ul>
    </section>
    </article>
    
    IMAGE_SUGGESTIONS:
    1. Alt: "[Descriptive alt text with keywords]" | Caption: "[Image caption]"
    2. Alt: "[Descriptive alt text with keywords]" | Caption: "[Image caption]"
    3. Alt: "[Descriptive alt text with keywords]" | Caption: "[Image caption]"
    
    Return the complete response with all sections.
    """
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                ]
            }
            
            response = requests.post(GEMINI_API_URL, json=payload, timeout=60)
            
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"⏳ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Rate limit exceeded after {max_retries} attempts")
                    return None, None, None, {}
            
            response.raise_for_status()
            result = response.json()
            
            if 'candidates' not in result or len(result['candidates']) == 0:
                print(f"⚠️ No candidates in response. Response: {result}")
                
                if 'promptFeedback' in result:
                    feedback = result['promptFeedback']
                    if 'blockReason' in feedback:
                        print(f"❌ Content blocked: {feedback['blockReason']}")
                        print(f"   Safety ratings: {feedback.get('safetyRatings', 'N/A')}")
                        if attempt < max_retries - 1:
                            print(f"🔄 Trying again with a different topic...")
                            time.sleep(2)
                            continue
                        return None, None, None, {}
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"⏳ Empty response. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None, None, None, {}
            
            candidate = result['candidates'][0]
            if 'content' not in candidate:
                print(f"⚠️ Content generation blocked by safety filters")
                print(f"   Finish reason: {candidate.get('finishReason', 'UNKNOWN')}")
                print(f"   Safety ratings: {candidate.get('safetyRatings', 'N/A')}")
                
                if attempt < max_retries - 1:
                    print(f"🔄 Trying again...")
                    time.sleep(2)
                    continue
                return None, None, None, {}
            
            content = candidate['content']['parts'][0]['text'].replace('```html', '').replace('```', '')
            
            # Convert any remaining Markdown to HTML
            content = convert_markdown_to_html(content)
            
            seo_data = {}
            try:
                # Extract meta description
                if 'META_DESCRIPTION:' in content:
                    meta_start = content.find('META_DESCRIPTION:') + len('META_DESCRIPTION:')
                    meta_end = content.find('\n', meta_start)
                    seo_data['meta_description'] = content[meta_start:meta_end].strip()
                
                # Extract URL slug
                if 'URL_SLUG:' in content:
                    slug_start = content.find('URL_SLUG:') + len('URL_SLUG:')
                    slug_end = content.find('\n', slug_start)
                    seo_data['url_slug'] = content[slug_start:slug_end].strip()
                
                # Extract primary keywords
                if 'PRIMARY_KEYWORDS:' in content:
                    kw_start = content.find('PRIMARY_KEYWORDS:') + len('PRIMARY_KEYWORDS:')
                    kw_end = content.find('\n', kw_start)
                    seo_data['keywords'] = content[kw_start:kw_end].strip()
                
                if 'FOCUS_KEYPHRASE:' in content:
                    focus_start = content.find('FOCUS_KEYPHRASE:') + len('FOCUS_KEYPHRASE:')
                    focus_end = content.find('\n', focus_start)
                    seo_data['focus_keyphrase'] = content[focus_start:focus_end].strip()
                
                start = content.find('<h1>') + 4
                end = content.find('</h1>')
                title = content[start:end]
                
                # Extract body (everything after metadata lines and before IMAGE_SUGGESTIONS)
                article_start = content.find('<article>')
                if article_start == -1:
                    article_start = content.find('<h1>')
                
                article_end = content.find('IMAGE_SUGGESTIONS:')
                if article_end == -1:
                    article_end = len(content)
                
                body = content[article_start:article_end].strip()
                
            except Exception as e:
                print(f"⚠️ Error parsing SEO data: {e}")
                title = topic
                body = content
                seo_data = {}
                
            return title, body, category, seo_data
            
        except requests.exceptions.HTTPError as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"⏳ HTTP Error. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Gemini API Error: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response: {e.response.text}")
                return None, None, None, {}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None, None, None, {}
    
    return None, None, None, {}

def post_to_blogger(title, content, category, seo_data=None):
    if not title or not content:
        print("❌ Content generation failed. Skipping post.")
        return

    if seo_data is None:
        seo_data = {}

    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    today = datetime.now().strftime('%Y')
    
    labels = [category, "News", "Trending", today]
    if seo_data.get('keywords'):
        keywords_list = [kw.strip() for kw in seo_data['keywords'].split(',')[:5]]
        labels.extend(keywords_list)
    
    if seo_data.get('focus_keyphrase'):
        labels.append(seo_data['focus_keyphrase'])
    
    labels = list(dict.fromkeys(labels))[:20]
    
    # SEO-optimized title
    seo_title = title
    if seo_data.get('focus_keyphrase') and seo_data['focus_keyphrase'].lower() not in title.lower():
        seo_title = f"{title} - {seo_data['focus_keyphrase']}"
    
    body = {
        "kind": "blogger#post",
        "title": seo_title[:100],
        "content": content,
        "labels": labels
    }
    
    try:
        posts = service.posts()
        result = posts.insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ Published: {result['url']}")
        
        if seo_data:
            print("\n📊 SEO Optimization Applied:")
            if seo_data.get('meta_description'):
                print(f"  📝 Meta Description: {seo_data['meta_description'][:50]}...")
            if seo_data.get('focus_keyphrase'):
                print(f"  🎯 Focus Keyphrase: {seo_data['focus_keyphrase']}")
            if seo_data.get('keywords'):
                print(f"  🔑 Keywords: {seo_data['keywords']}")
            if seo_data.get('url_slug'):
                print(f"  🔗 Suggested URL: {seo_data['url_slug']}")
            print(f"  🏷️  Total Labels: {len(labels)}")
    except Exception as e:
        print(f"❌ Error posting to Blogger: {e}")

if __name__ == "__main__":
    max_topic_attempts = 5
    
    for attempt in range(max_topic_attempts):
        print(f"\n{'='*60}")
        print(f"📝 Attempt {attempt + 1}/{max_topic_attempts}")
        print(f"{'='*60}\n")
        
        topic, category = get_random_trending_topic()
        if not topic:
            print("❌ Could not find any trends. Retrying...")
            time.sleep(3)
            continue
        
        title, body, cat, seo_data = generate_content(topic, category)
        
        if title and body:
            post_to_blogger(title, body, cat, seo_data)
            print(f"\n✅ Successfully completed blog post generation!")
            break
        else:
            print(f"\n⚠️ Content generation failed for topic: '{topic}'")
            if attempt < max_topic_attempts - 1:
                print(f"🔄 Trying with a different trending topic...\n")
                time.sleep(3)
            else:
                print(f"\n❌ Failed after {max_topic_attempts} attempts. Please try again later.")
                exit(1)