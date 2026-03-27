import os
import requests
import time
import random
import re
import base64
from datetime import datetime
import xml.etree.ElementTree as ET

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 로컬 환경을 위한 dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
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

def convert_markdown_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
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

def get_published_titles():
    try:
        service = get_blogger_service()
        blog_id = os.environ["BLOGGER_BLOG_ID"]
        request = service.posts().list(blogId=blog_id, maxResults=50, fetchBodies=False)
        response = request.execute()
        return [item.get('title', '').lower() for item in response.get('items', [])]
    except Exception as e:
        print(f"⚠️ 기존 발행 글 목록 가져오기 실패: {e}")
        return []

def get_vibe_coding_topic():
    published_titles = get_published_titles()
    random.shuffle(FALLBACK_TOPICS)
    for topic in FALLBACK_TOPICS:
        topic_lower = topic.lower()
        is_duplicate = any(topic_lower in pub or pub in topic_lower for pub in published_titles if pub)
        if not is_duplicate:
            return topic
    return "2026 AI Coding Trends"

# ====================== (완벽 해결) 이미지 생성 및 다이렉트 업로드 ======================
def generate_and_upload_image(image_prompt):
    print(f"🎨 구글 Imagen 3로 이미지 생성 중... (프롬프트: {image_prompt[:50]}...)")
    
    headers = {'Content-Type': 'application/json'}
    safe_prompt = re.sub(r'[^a-zA-Z0-9\s,]', '', image_prompt).strip()
    payload = {
        "instances": [{"prompt": f"A high-quality, vibrant flat design illustration for a tech blog. {safe_prompt}. Modern tech aesthetic, clean lines, highly detailed."}],
        "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}
    }
    
    try:
        # 1. 구글 API로 이미지 생성 (Base64)
        response = requests.post(GEMINI_IMAGE_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        base64_img = response.json()['predictions'][0]['bytesBase64Encoded']
        image_bytes = base64.b64decode(base64_img)
        print("✅ 구글 이미지 생성 완료! 호스팅 서버로 업로드 중...")
        
        # 2. 무료 이미지 호스팅(Catbox)에 업로드하여 절대 깨지지 않는 영구 URL 획득 (블로거 필터링 완벽 우회)
        files = {'fileToUpload': ('thumbnail.jpg', image_bytes, 'image/jpeg')}
        data = {'reqtype': 'fileupload'}
        upload_resp = requests.post('https://catbox.moe/user/api.php', files=files, data=data, timeout=30)
        upload_resp.raise_for_status()
        
        final_url = upload_resp.text.strip()
        print(f"✅ 이미지 호스팅 업로드 성공: {final_url}")
        return final_url
        
    except Exception as e:
        print(f"❌ 이미지 생성/업로드 실패: {e}")
        # 실패 시 깨지지 않는 깔끔한 기본 IT 이미지 주소 반환
        return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024&q=80"

def generate_content(topic):
    print(f"✍️ 글, 태그, 프롬프트 동시 생성 중: {topic}...")
    
    prompt = f"""
    당신은 2026년 최고 인기 AI 코딩 블로그 'AI 코딩 랩'의 전문 강사 'VibeCoder'입니다.
    주제: "{topic}" 에 대해 **실전 가이드** 블로그 글을 작성해주세요.
    
    --- CRITICAL REQUIREMENTS ---
    1. **어투:** "안녕하세요! VibeCoder입니다! 👋", "바로 시작해 볼까요? 🔥" 등 매우 활기차고 트렌디한 어투.
    2. **가독성:** 문단을 짧게 끊어 쓰고, 설명을 구체적이고 길게 풀어주세요.
    3. **Image Prompt:** 썸네일 생성을 위해 이 글을 표현하는 영단어 나열. (예: developer, AI coding, neon blue, flat design)
    4. **Tags:** 이 글에 관련된 구체적인 키워드 3개. (예: Cursor, MVP제작, AI자동화)
    5. **Formatting:** ONLY HTML tags (<h2>, <h3>, <p>, <ul>, <strong> 등). DO NOT use Markdown.
    
    --- Structure your response EXACTLY like this ---
    
    [FEATURED_IMAGE_PROMPT: (여기에 영어 단어 프롬프트 삽입)]
    [TAGS: 태그1, 태그2, 태그3]
    
    <article>
    <header><h1>[이모지가 포함된 제목]</h1></header>
    <section class="introduction"><p>👋 [서론]</p></section>
    <section><h2>주요 포인트 5가지 🔥</h2><ul><li>🚀 [포인트]</li></ul></section>
    <section><h2>실전 가이드 단계별 따라 하기 🛠️</h2>
    <h3>1️⃣ Step 1: [소제목]</h3><p>[설명]</p>
    ...
    </section>
    <section class="conclusion"><h2>Final Thoughts 💡</h2><p>[마무리]</p></section>
    </article>
    """
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_TEXT_URL, json=payload, timeout=90)
        response.raise_for_status()
        content = response.json()['candidates'][0]['content']['parts'][0]['text']
        content = convert_markdown_to_html(content.replace('```html', '').replace('```', ''))
        
        image_prompt, dynamic_tags = "", []
        
        img_match = re.search(r'\[FEATURED_IMAGE_PROMPT:\s*(.*?)\]', content)
        if img_match: image_prompt = img_match.group(1).strip()
            
        tag_match = re.search(r'\[TAGS:\s*(.*?)\]', content)
        if tag_match: dynamic_tags = [t.strip() for t in tag_match.group(1).split(',')]
        
        article_start = content.find('<article>')
        body = content[article_start:].strip() if article_start != -1 else content
        title = body[body.find('<h1>')+4 : body.find('</h1>')].strip() if '<h1>' in body else topic
        
        return title, body, image_prompt, dynamic_tags
        
    except Exception as e:
        print(f"❌ 텍스트 생성 오류: {e}")
        return None, None, "", []

def post_to_blogger(title, content, image_url, dynamic_tags):
    if not title or not content: return

    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    
    labels = ["AI Coding", "VibeCoding"] + dynamic_tags
    labels = list(dict.fromkeys(labels))[:6]
    
    rating = round(random.uniform(4.7, 4.9), 1)
    
    # ====================== (디자인 혁신) 가독성 극대화 CSS ======================
    styled_content = f"""
    <style>
      .vibe-content {{ font-family: 'Noto Sans KR', sans-serif; color: #222; line-height: 2.0; letter-spacing: -0.3px; }}
      
      /* H2: 굵고 여백을 넓게 주어 문단을 확실히 나눔 */
      .vibe-content h2 {{ margin-top: 65px; margin-bottom: 25px; font-size: 1.7em; border-bottom: 3px solid #ff6b6b; padding-bottom: 12px; font-weight: 800; }}
      
      /* H3: 시원한 배경색과 좌측 포인트 컬러로 눈에 확 띄게 만듦 */
      .vibe-content h3 {{ margin-top: 50px; margin-bottom: 20px; font-size: 1.4em; color: #2c3e50; font-weight: bold; background-color: #f8f9fa; padding: 12px 18px; border-left: 5px solid #1a73e8; border-radius: 6px; }}
      
      /* P (본문): 글씨를 키우고 아래 여백을 넉넉히 주어 답답하지 않게 함 */
      .vibe-content p {{ margin-bottom: 25px; font-size: 17px; word-break: keep-all; }}
      
      /* 리스트: 박스 형태로 감싸서 깔끔하게 정리 */
      .vibe-content ul {{ margin-bottom: 40px; background-color: #fdfdfd; padding: 25px 25px 25px 45px; border-radius: 10px; border: 1px solid #eaeaea; }}
      .vibe-content li {{ margin-bottom: 15px; font-size: 17px; }}
      
      /* 별점 둥둥 떠있는 느낌으로 마무리 */
      .vibe-rating {{ text-align: right; margin-top: 80px; padding-top: 25px; border-top: 2px dashed #ddd; font-size: 1.4em; font-weight: bold; color: #f39c12; }}
    </style>
    
    <div class="vibe-content">
      <div style="text-align: center; margin-bottom: 50px;">
        <img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 14px; box-shadow: 0 8px 20px rgba(0,0,0,0.15);"/>
      </div>
      
      {content}
      
      <div class="vibe-rating">
        ⭐⭐⭐⭐⭐ {rating} / 5.0
      </div>
    </div>
    """
    
    body = {"kind": "blogger#post", "title": title[:100], "content": styled_content, "labels": labels}
    
    try:
        service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ 포스팅 성공! 태그: {labels}")
    except Exception as e:
        print(f"❌ Blogger 포스팅 실패: {e}")

if __name__ == "__main__":
    print(f"\n{'='*70}\n🚀 Vibe Coding Auto Post 시작\n{'='*70}\n")
    topic = get_vibe_coding_topic()
    title, body, image_prompt, dynamic_tags = generate_content(topic)
    
    if title and body:
        # 이미지 생성 및 다이렉트 호스팅 업로드 (가장 확실한 방법)
        final_image_url = generate_and_upload_image(image_prompt)
        post_to_blogger(title, body, final_image_url, dynamic_tags)
    else:
        print("\n❌ 콘텐츠 생성에 실패했습니다.")
