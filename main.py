import os
import requests
import random
import re
import base64
import time
import json
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 로컬 환경을 위한 dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ====================== 환경 변수 설정 ======================
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
HF_TOKEN = os.environ.get("HF_TOKEN")
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY")

GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# ====================== 유틸리티 함수 ======================
def convert_markdown_to_html(text):
    """마크다운 형식을 HTML로 변환하여 구조화된 데이터 점수 확보"""
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
    """중복 포스팅 방지를 위해 기존 글 목록 조회"""
    try:
        service = get_blogger_service()
        blog_id = os.environ["BLOGGER_BLOG_ID"]
        request = service.posts().list(blogId=blog_id, maxResults=100, fetchBodies=False)
        response = request.execute()
        return [item.get('title', '').lower() for item in response.get('items', [])]
    except Exception as e:
        print(f"⚠️ 기존 발행 글 목록 가져오기 실패: {e}")
        return []

def get_real_estate_topic(json_path="topics.json"):
    """JSON 파일에서 카테고리별 주제를 로드하여 미발행 주제 선정"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            topics_dict = json.load(f)
    except Exception as e:
        print(f"❌ {json_path} 로드 실패: {e}")
        return "부동산 투자", "2026년 부동산 시장 핵심 전망"

    published_titles = get_published_titles()
    all_topics = []
    for category, topics in topics_dict.items():
        for topic in topics:
            all_topics.append((category, topic))
            
    random.shuffle(all_topics)
    for category, topic in all_topics:
        if not any(topic.lower() in pub for pub in published_titles):
            return category, topic
    return "부동산 투자", "2026년 하반기 부동산 시장 핵심 전략"

# ====================== 이미지 생성 및 업로드 ======================
def generate_image_hf(prompt):
    print(f"🎨 이미지 생성 시작...")
    if not HF_TOKEN: return None
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": f"A high-quality, professional real estate and wealth growth illustration, {prompt}, 4k resolution, cinematic lighting."}
    
    models = [
        "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
        "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    ]
    
    for model_url in models:
        for attempt in range(3):
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=45)
                if response.status_code == 200: return response.content
                elif response.status_code == 503: time.sleep(10); continue
                else: break
            except: continue
    return None

def upload_image_to_imgbb(image_bytes):
    if not IMGBB_API_KEY or not image_bytes: return None
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY, "image": base64.b64encode(image_bytes).decode('utf-8')}
        response = requests.post(url, data=payload, timeout=30)
        return response.json()["data"]["url"]
    except: return None

# ====================== 콘텐츠 생성 (구글 승인 & SEO 최적화) ======================
def generate_content(category, topic):
    print(f"✍️ [SEO & AdSense 모드] 심층 분석 리포트 생성 중: {topic}")
    
    prompt = f"""
    당신은 대한민국 최고의 부동산 실전 투자 블로그 '부의 지름길'의 수석 애널리스트입니다. 
    주제: "{topic}" (카테고리: {category})
    
    --- MISSION ---
    구글 애드센스 승인과 검색 상위 노출을 위해 4,000자 이상의 압도적 퀄리티를 가진 리포트를 작성하세요.

    --- SEO & 전문성 가이드라인 ---
    1. 분량: 공백 제외 4,000자 이상의 매우 상세한 정보.
    2. 전문 데이터: 2026년 현재 시행 중인 부동산 법령, 구체적 수치(용적률, 공시지가, 취득세율 등) 인용.
    3. 구조: HTML 태그(h2, h3, p, strong, table, blockquote)를 적극 사용.
    4. 독창성: AI 말투 지양. 실제 발로 뛴 임장 보고서처럼 생생한 통찰력을 포함할 것.
    5. FAQ: 검색자가 궁금해할 질문 3가지와 답변을 포함하여 스키마 데이터 가점 확보.

    --- 출력 구조 (엄수) ---
    [FEATURED_IMAGE_PROMPT: (영문 프롬프트 10단어)]
    [TAGS: 태그1, 태그2, 태그3]
    [META_DESC: (150자 이내의 검색 결과 요약문)]

    <article>
        <header><h1>[강력한 클릭 유도 제목]</h1></header>
        <section>
            <h2>들어가며: {topic} 분석의 필요성</h2>
            <p>[전문적이고 공감대 형성하는 서론]</p>
        </section>
        <section>
            <h2>1. 정책 및 핵심 지표 정밀 분석</h2>
            <p>[상세 내용]</p>
            <blockquote>이 섹션의 핵심 내용을 한 줄로 요약하는 전문가의 한마디</blockquote>
        </section>
        <section>
            <h2>2. 실전 투자 수익 시뮬레이션</h2>
            <table border="1" style="width:100%; border-collapse: collapse; margin: 20px 0; text-align: center;">
                [주제 관련 비교 데이터 또는 수치 테이블]
            </table>
        </section>
        <section>
            <h2>3. 자주 묻는 질문(FAQ) ❓</h2>
            <h3>Q1. [질문 1]</h3><p>A1. [상세 답변]</p>
            <h3>Q2. [질문 2]</h3><p>A2. [상세 답변]</p>
            <h3>Q3. [질문 3]</h3><p>A3. [상세 답변]</p>
        </section>
        <section>
            <h2>마치며: 수석 분석가의 최종 제언</h2>
            <p>[인사이트 가득한 결론]</p>
        </section>
    </article>
    """

    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_TEXT_URL, json=payload, timeout=180)
        response.raise_for_status()
        content = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        content = content.replace('```html', '').replace('```', '').strip()
        content = convert_markdown_to_html(content)

        img_match = re.search(r'\[FEATURED_IMAGE_PROMPT:\s*(.*?)\]', content)
        image_prompt = img_match.group(1).strip() if img_match else "Modern luxury real estate Seoul"

        tag_match = re.search(r'\[TAGS:\s*(.*?)\]', content)
        dynamic_tags = [t.strip() for t in tag_match.group(1).split(',')] if tag_match else []

        article_start = content.find('<article>')
        body = content[article_start:].strip() if article_start != -1 else content
        title = body[body.find('<h1>')+4 : body.find('</h1>')].strip() if '<h1>' in body else topic

        return title, body, dynamic_tags, image_prompt
    except Exception as e:
        print(f"❌ 텍스트 생성 실패: {e}")
        return None, None, [], None

# ====================== 블로거 포스팅 (부의 지름길 전용 디자인) ======================
def post_to_blogger(title, content, main_category, dynamic_tags, image_url=None):
    if not title or not content: return
    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]

    labels = ["부의지름길", main_category] + dynamic_tags
    labels = list(dict.fromkeys(labels))[:6]
    
    rating_val = round(random.uniform(4.8, 5.0), 1)
    rates_count = random.randint(180, 2450)

    styled_content = f"""
    <style>
      .wealth-container {{ font-family: 'Noto Sans KR', sans-serif; color: #333; line-height: 1.9; letter-spacing: -0.5px; word-break: keep-all; }}
      .wealth-container h2 {{ margin-top: 60px; margin-bottom: 25px; font-size: 1.7em; border-bottom: 3px solid #1a365d; padding-bottom: 12px; font-weight: 800; color: #1a365d; }}
      .wealth-container h3 {{ margin-top: 40px; margin-bottom: 15px; font-size: 1.4em; color: #2c5282; font-weight: 700; background: #f0f4f8; padding: 12px 18px; border-radius: 8px; }}
      .wealth-container p {{ margin-bottom: 25px; font-size: 17px; text-align: justify; }}
      .wealth-container blockquote {{ border-left: 5px solid #1a365d; background: #f9fafb; padding: 20px; font-style: italic; color: #4a5568; margin: 30px 0; }}
      
      .wealth-callout {{
        background-color: #f8fafc; border: 2px solid #e2e8f0; border-left: 8px solid #1a365d;
        padding: 30px; border-radius: 12px; margin: 60px 0 40px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
      }}
      .wealth-callout-title {{ display: block; font-size: 1.25em; font-weight: 800; color: #1a365d; margin-bottom: 15px; }}
      .wealth-callout-text {{ font-size: 16px; color: #4a5568; }}
      .wealth-callout-text strong {{ color: #c53030; }}

      .wealth-footer {{
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 50px; padding-top: 25px; border-top: 1px solid #edf2f7;
      }}
      .wealth-brand {{ font-weight: 900; color: #1a365d; font-size: 1.1em; }}
      .wealth-rating {{ color: #ecc94b; font-size: 1.1em; }}
      .wealth-rating span {{ color: #a0aec0; font-size: 0.85em; margin-left: 5px; }}
    </style>
    
    <div class="wealth-container">
      {f'<div style="text-align: center; margin-bottom: 50px;"><img src="{image_url}" alt="{title}" style="max-width: 100%; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);"/></div>' if image_url else ''}
      
      {content}
      
      <div class="wealth-callout">
        <span class="wealth-callout-title">🏛️ 평범한 월급쟁이에서 자산가로 가는 '부의 지름길'</span>
        <p class="wealth-callout-text">
          부동산의 흐름을 읽지 못하면 자본주의의 파도에 휩쓸리기 쉽습니다. <strong>부의 지름길</strong>은 단순한 뉴스를 넘어, 당신의 자산을 지키고 증식시킬 실전 인사이트를 제공합니다.<br>
          혼란스러운 시장 속에서도 흔들리지 않는 <strong>명확한 투자 지도</strong>, 지금 바로 매일 업데이트되는 전문 리포트로 확인하세요. 🏠💰
        </p>
      </div>
      
      <div class="wealth-footer">
        <div class="wealth-brand">Shortcut to Wealth.</div>
        <div class="wealth-rating">⭐⭐⭐⭐⭐ <span>{rating_val} / {rates_count} Reviews</span></div>
      </div>
    </div>
    """

    body = {"kind": "blogger#post", "title": title[:100], "content": styled_content, "labels": labels}
    try:
        service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ 포스팅 성공: {title[:50]}...")
    except Exception as e:
        print(f"❌ 포스팅 실패: {e}")

# ====================== 메인 실행부 ======================
if __name__ == "__main__":
    print(f"\n{'='*70}\n🚀 부의 지름길 전문 리포트 자동 발행 시스템\n{'='*70}\n")
    
    main_cat, sub_topic = get_real_estate_topic()
    post_title, post_body, tags, img_prompt = generate_content(main_cat, sub_topic)
    
    if post_title and post_body:
        img_bytes = generate_image_hf(img_prompt)
        final_img_url = upload_image_to_imgbb(img_bytes)
        post_to_blogger(post_title, post_body, main_cat, tags, final_img_url)
    else:
        print("❌ 콘텐츠 생성 중단.")