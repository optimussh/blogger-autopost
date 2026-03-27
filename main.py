import os
import requests
import time
import random
import re
import json
from datetime import datetime
import xml.etree.ElementTree as ET

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 로컬 환경을 위한 dotenv (GitHub Actions에서는 없어도 패스하도록 설정)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# 텍스트 생성용 모델 (글쓰기)
GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
# 이미지 생성용 모델 (썸네일) - 구글 Imagen / Gemini Image API
GEMINI_IMAGE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={GEMINI_API_KEY}"

# ====================== 2026년 3월 기준 가장 터지는 Vibe Coding Fallback 풀 (60개) ======================
# 🚨 주의: 파이썬은 이 부분의 줄 맞춤(들여쓰기)에 엄청 예민합니다. 아래와 같이 똑같이 맞춰야 합니다.
FALLBACK_TOPICS = [
"Claude Code Opus 4.6으로 하루 만에 MVP 만들기: Agent Teams 실전 가이드",
    "Cursor IDE 2026 완전 정복: Composer 모드로 3배 빠른 풀스택 개발",
    "Windsurf AI IDE vs Cursor: 2026년 어떤 걸 골라야 할까? 가격·성능 비교",
    "Lovable.dev로 코드 없이 SaaS 앱 30분 만에 뚝딱 만드는 법",
    "Google Antigravity 무료로 Claude Opus 4.6까지 쓰는 실전 팁",
    "Claude Code vs Windsurf: Agentic 워크플로우 누가 더 강할까?",
    "2026 AI 코딩 도구 가격 총정리: 월 2만원으로 최고 성능 내는 조합",
    "Cursor Composer로 대형 코드베이스 리팩토링 없이 정리하는 법",
    "Vibe Coding 초보자 로드맵: 챗봇 → AI Agent까지 5단계",
    "Gemini Code Assist 실전 가이드: Google Cloud에서 가장 강력한 코딩 도구",
    "Claude Opus 4.6 1M 컨텍스트로 대형 프로젝트 관리하는 실전 팁",
    "Windsurf Arena Mode로 여러 AI 모델 동시에 비교하며 코딩하기",
    "Lovable + Supabase + Vercel로 완전 무코드 MVP 배포하는 방법",
    "AI 코딩 도구로 기술 부채 쌓이지 않게 하는 7가지 실전 방법",
    "Claude Code vs OpenAI Codex: 2026년 코딩 에이전트 대전",
    "2026 개발자 생산성 5배 높이는 Vibe Coding 워크플로우 구축법",
    "Cursor vs GitHub Copilot X: 2026년 진짜 승자는?",
    "Claude Code Agent로 버그 자동 수정하고 테스트까지 끝내는 법",
    "Antigravity 초보자 추천 설정: 완전 무��� AI 코딩 시작하기",
    "Vibe Coding으로 Micro-SaaS, Standalone 앱, Remix 템플릿 만들기",
    "Windsurf Plan Mode로 복잡한 멀티파일 작업 자동화하는 실전 가이드",
    "Claude 4.6 Sonnet vs Opus: 비용 절감하면서 성능 내는 선택법",
    "Lovable.dev 2026 가격 비교: 진짜 돈 값 하는가?",
    "AI Agent로 20시간 걸리는 작업을 50% 성공률로 끝내는 방법",
    "Cursor IDE에서 Claude Opus 4.6 쓰는 최고의 프롬프트 템플릿 10개",
    "2026 Agentic Coding 트렌드: Orchestration과 Multi-Agent 완전 정리",
    "Gemini 3.1 Pro Code Assist로 Google Cloud 풀스택 앱 빠르게 만들기",
    "Vibe Coding에서 Production 코드로 넘어가기: 보안·아키텍처 실전 팁",
    "Windsurf Cascade AI Agent로 병렬 개발하는 실전 워크플로우",
    "Claude Code로 기술 부채 없이 빠르게 MVP 출시하는 단계별 가이드",
    "Antigravity + Claude Opus 조합으로 무���로 최고 성능 내는 법",
    "Cursor에서 AI로 전체 리팩토링 하는 단계별 실전 가이드",
    "2026년 개발자 필수 AI 스택: Cursor + Claude Code + Lovable 조합",
    "Lovable로 만든 앱을 실제 수익 나는 Micro-SaaS로 키우는 법",
    "AI 코딩 도구 보안 가이드: 취약점 자동 검사와 방어 전략",
    "Claude Code Agent Skills 2026 최신 기능 완전 정복",
    "Windsurf Wave 업데이트 후 달라진 점과 실전 활용법",
    "Vibe Coding으로 게임·웹앱·SaaS 3개 동시 제작하기",
    "Gemini vs Claude Code: 2026 코딩 성능·가격·속도 비교표",
    "Cursor IDE Pro vs Free: 과연 돈 주고 쓸 가치가 있을까?",
    "AI로 10배 빠른 개발하면서 코드 품질 유지하는 비법",
    "Lovable.dev vs Bolt.new vs v0: 2026년 최고의 Vibe 플랫폼 비교",
    "Claude Code로 대형 리팩토링 1시간 만에 끝내는 단계별 가이드",
    "Antigravity 무료 플랜 한계와 극복하는 실전 팁",
    "2026 AI IDE 전쟁: Cursor · Windsurf · Claude Code 승자 예측",
    "Vibe Coding 초보자를 위한 첫 프로젝트 5가지 추천",
    "Windsurf로 멀티 에이전트 동시에 작업하는 실전 팁",
    "Claude Opus 4.6 128K 출력 토큰을 제대로 활용하는 사례 모음",
    "AI 코딩 도구로 월 500만원 버는 Micro-SaaS 만드는 실전 가이드",
    "Cursor Composer + Claude Code 최고의 협업 워크플로우",
    "2026년 AI 코딩 도구로 기술 부채 없이 지속 가능한 개발하기",
    "Lovable 노코드 → 실제 코드로 넘어가기 실전 전환 가이드",
    "Gemini Code Assist + Google Cloud로 풀스택 앱 1시간 제작하기",
    "Vibe Coding의 미래: Agentic Coding이 가져올 개발자 역할 변화",
    "Claude Code vs Antigravity: 대형 코드베이스 작업 비교 2026",
    "Windsurf vs Cursor: Agentic 개발 속도와 안정성 비교",
    "2026 AI 코딩 트렌드: Human-in-the-Loop vs Fully Agentic",
    "Claude Code로 SWE-bench 고득점 내는 실전 프롬프트 전략",
    "Lovable로 빠른 프로토타입 검증 후 Cursor로 프로덕션 전환하기",
    "2026 개발자 생산성 도구 스택: Claude Code + Cursor + Lovable 조합"
]
# ====================== 유틸리티 함수 ======================
def load_published_topics():
    if os.path.exists("published_topics.json"):
        with open("published_topics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_published_topic(topic):
    topics = load_published_topics()
    topics.append({"topic": topic, "date": datetime.now().isoformat()})
    if len(topics) > 40:
        topics = topics[-40:]
    with open("published_topics.json", "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)

def is_duplicate(topic):
    topics = load_published_topics()
    topic_lower = topic.lower()
    return any(t["topic"].lower() in topic_lower or topic_lower in t["topic"].lower() for t in topics)

def convert_markdown_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

# ====================== (기능 추가) 구글 API로 이미지 생성 ======================
def generate_google_image(image_prompt):
    print(f"🎨 구글 API로 썸네일 이미지 생성 중... (프롬프트: {image_prompt[:50]}...)")
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "instances": [
            {"prompt": f"A high-quality, vibrant flat design illustration for a tech blog. {image_prompt}. Modern tech aesthetic, clean lines, highly detailed."}
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9"
        }
    }
    
    try:
        response = requests.post(GEMINI_IMAGE_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # 구글 API는 이미지를 Base64 문자열로 반환합니다.
        base64_img = data['predictions'][0]['bytesBase64Encoded']
        print("✅ 이미지 생성 완료!")
        
        # HTML <img> 태그에 바로 넣을 수 있는 Data URI 형태로 반환
        return f"data:image/jpeg;base64,{base64_img}"
        
    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
        return None

# ====================== 구글 Blogger 연동 ======================
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

def get_vibe_coding_topic():
    print("🔍 Vibe Coding 주제 선택 중...")
    random.shuffle(FALLBACK_TOPICS)
    published_set = {t["topic"].lower() for t in load_published_topics()}
    
    for topic in FALLBACK_TOPICS:
        if topic.lower() not in published_set and not is_duplicate(topic):
            print(f"✅ 선택된 Vibe Coding 주제: {topic}")
            return topic, "AI Coding Tools"
    
    return "2026 AI Coding Trends", "AI Coding Tools"

# ====================== (프롬프트 정교화) 콘텐츠 생성 ======================
def generate_content(topic, category):
    print(f"✍️ 글 작성 및 동적 이미지 프롬프트 생성 중: {topic}...")
    
    prompt = f"""
    당신은 2026년 가장 터지는 AI 코딩 전문 블로그 'AI 코딩 랩'의 전문 강사이자 'Vibe 코딩 스쿨'의 창립자 'VibeCoder'입니다.
    
    주제: "{topic}" 에 대해 **실전 가이드** 블로그 글을 작성해주세요.
    
    --- CRITICAL REQUIREMENTS ---
    1. **어투:** "안녕하세요! VibeCoder입니다! 👋", "자, 오늘 바로 시작해 볼까요? 🔥" 처럼 독자에게 직접 말하는 듯한 활기찬 어투.
    2. **단락 구조:** 초보자도 바로 따라 할 수 있게 소제목(H2, H3)에 이모지와 숫자를 매겨 단계별 가이드 스타일로 작성하세요.
    3. **Formatting:** Use ONLY HTML tags. DO NOT use Markdown. 적극적으로 <strong>bold</strong>, <ul>, <li>, <blockquote> 태그를 사용하세요.
    4. **Image Prompt (중요):** 당신이 작성한 글의 핵심 주제를 가장 잘 표현할 수 있는 썸네일 이미지 프롬프트를 **반드시 '영어'로** 작성해 주세요. 
       (예시: A vibrant illustrative flat design of a developer building a full-stack app using Cursor IDE, neon blue and purple tones)
    
    --- Structure your response EXACTLY like this ---
    
    [META_DESCRIPTION: 150-160자 SEO 설명]
    [URL_SLUG: keyword-rich-url-slug]
    [FEATURED_IMAGE_PROMPT: (여기에 영어로 작성된 동적 이미지 프롬프트 삽입)]
    
    <article>
    <header>
    <h1>[이모지가 포함된 SEO 최적화된 제목]</h1>
    </header>
    
    <section class="introduction">
    <p>👋 [활기차고 실전적인 서론]</p>
    </section>
    
    <section>
    <h2>주요 포인트 5가지 🔥</h2>
    <ul>
    <li>🚀 [포인트]</li>
    ...
    </ul>
    </section>
    
    <section>
    <h2>실전 가이드 단계별 따라 하기 🛠️</h2>
    <h3>1️⃣ Step 1: [Vibe 스타일 소제목]</h3>
    <p>[상세 설명 + 코드 예시 등]</p>
    ...
    </section>
    
    <section class="conclusion">
    <h2>Final Thoughts & CTA 💡</h2>
    <p>[마무리 및 행동 촉구]</p>
    </section>
    </article>
    """
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_TEXT_URL, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        
        content = result['candidates'][0]['content']['parts'][0]['text']
        content = content.replace('```html', '').replace('```', '')
        content = convert_markdown_to_html(content)
        
        seo_data = {}
        featured_image_prompt = None
        
        # 정규식으로 데이터 추출
        meta_match = re.search(r'\[META_DESCRIPTION:\s*(.*?)\]', content)
        if meta_match: seo_data['meta_description'] = meta_match.group(1).strip()
        
        slug_match = re.search(r'\[URL_SLUG:\s*(.*?)\]', content)
        if slug_match: seo_data['url_slug'] = slug_match.group(1).strip()
        
        # 글의 내용에 맞춰 AI가 스스로 짠 이미지 프롬프트 추출
        image_prompt_match = re.search(r'\[FEATURED_IMAGE_PROMPT:\s*(.*?)\]', content)
        if image_prompt_match: featured_image_prompt = image_prompt_match.group(1).strip()
        
        # HTML 본문 추출
        article_start = content.find('<article>')
        article_end = len(content)
        body = content[article_start:article_end].strip() if article_start != -1 else content
        
        # 제목 추출
        start = body.find('<h1>') + 4
        end = body.find('</h1>')
        title = body[start:end].strip() if start > 3 and end > start else topic
        
        return title, body, category, seo_data, featured_image_prompt
        
    except Exception as e:
        print(f"❌ 텍스트 생성 중 오류: {e}")
        return None, None, None, {}, None

def post_to_blogger(title, content, category, seo_data=None, base64_image_data=None):
    if not title or not content:
        return

    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    
    labels = [category, "VibeCoding", "AI Tools"]
    
    # 생성된 Base64 이미지를 HTML 최상단에 삽입
    final_content = ""
    if base64_image_data:
        final_content += f'<div style="text-align: center; margin-bottom: 20px;"><img src="{base64_image_data}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" /></div>\n\n'
    
    final_content += content
    
    body = {
        "kind": "blogger#post",
        "title": title[:100],
        "content": final_content,
        "labels": labels
    }
    
    try:
        result = service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ Published successfully: {result.get('url', 'URL not available')}")
        save_published_topic(title)
    except Exception as e:
        print(f"❌ Blogger 포스팅 실패: {e}")

# ====================== 메인 실행 흐름 ======================
if __name__ == "__main__":
    print(f"\n{'='*70}\n🚀 Vibe Coding Auto Post 시작\n{'='*70}\n")
    
    topic, category = get_vibe_coding_topic()
    title, body, cat, seo_data, featured_image_prompt = generate_content(topic, category)
    
    if title and body:
        base64_image_data = None
        
        # AI가 뽑아준 프롬프트가 있다면, 구글 이미지 API로 썸네일 생성!
        if featured_image_prompt:
            base64_image_data = generate_google_image(featured_image_prompt)
        
        # 글과 이미지를 합쳐서 포스팅
        post_to_blogger(title, body, cat, seo_data, base64_image_data)
        print(f"\n🎉 모든 과정 완료! 포스팅 주제: {topic}")
    else:
        print("\n❌ 콘텐츠 생성에 실패했습니다.")
