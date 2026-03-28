import os
import requests
import random
import re
import base64
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 로컬 환경을 위한 dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 환경 변수 설정
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
HF_TOKEN = os.environ.get("HF_TOKEN")  # Hugging Face 토큰 (필수)

GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"


# ====================== '부의 지름길' 부동산 핵심 키워드 100선 ======================
FALLBACK_TOPICS = [
    # 서울 주요 재개발/재건축
    "한남뉴타운 3구역, 이주 단계에서 체크해야 할 투자 포인트",
    "성수전략정비구역, 압구정급 위상으로 변모하는 진행 현황",
    "노량진뉴타운, 여의도 배후 주거지로서의 압도적 가치",
    "은평구 갈현1구역, 대단지 프리미엄과 사업성 분석",
    "북아현뉴타운 2, 3구역 진행 단계와 매수 시점 잡기",
    "장위뉴타운 잔여 구역, 실거주와 투자를 동시에 잡는 법",
    "상계뉴타운, 4호선 연장과 창동·상계 신경제중심지 수혜",
    "미아뉴타운 재개발, 동북권 최대 주거 타운의 변신",
    "수색·증산뉴타운 입주권 vs 분양권, 세금 차이 정리",
    "영등포구 신길뉴타운, 신안산선 개통 후 가치 변화 예측",
    "거여·마천뉴타운, 위례신도시와 시너지 내는 정비사업",
    "동대문구 이문·휘경뉴타운 3구역(이문 아이파크 자이) 분석",
    "압구정 현대아파트 재건축, 신통기획으로 빨라진 사업 속도",
    "반포 주공 1단지 재건축, 단군 이래 최대 정비사업 진행 현황",
    "잠실 주공 5단지, 50층 높이로 재탄생하는 랜드마크",
    "여의도 시범·광장아파트, 재건축을 통한 금융 중심지 변모",
    "목동 신시가지 아파트 재건축 안전진단 통과 후 시세 변화",
    "상계 주공 단지들, 노후 계획도시 특별법 적용 가능성",
    "광진구 자양7구역 재건축, 한강변 입지의 미래 가치",
    "동작구 흑석뉴타운 11구역, 서반포라 불리는 이유",
    "강남구 대치 미도·선경아파트 재건축 통합 가이드",
    "서초구 방배동 재건축 구역별 특징과 투자 금액대 비교",
    "성북구 장위 10구역 사랑의교회 이슈 해결 후 사업 속도",
    "도봉구 창동 주공 18, 19단지 예비안전진단 통과 의미",
    "서대문구 홍은동·홍제동 재개발 구역 임장 보고서",
    "용산구 서계동·청파동 신통기획 후보지 임장 포인트",
    "중구 신당 10구역, 도심 재개발의 모범 사례 분석",
    "강서구 방배 5, 6구역 프리미엄과 추가 분담금 예상",
    "관악구 신림뉴타운 1, 2, 3구역 진행 현황 총정리",
    "금천구 독산동·시흥동 소규모 재건축(가로주택정비사업) 현황",

    # 경기/수도권 핵심 정비사업
    "광명뉴타운 11, 12구역 대장주 분석과 프리미엄 추이",
    "성남 원도심 재개발(산성구역, 상대원2구역) 사업성 분석",
    "수원 팔달뉴타운 재개발 완료 후 인프라 변화와 시세",
    "안양시 비산동·호계동 재개발 단지들의 입주권 투자법",
    "부천시 중동 신도시 재건축, 특별법 수혜 가능성 점검",
    "고양시 일산 신도시 재건축 선도지구 지정 요건 분석",
    "안산시 성포동·월피동 재건축과 신안산선 호재 정리",
    "구리시 수택동·인창동 재개발 구역별 단계별 특징",
    "의왕시 내손 다, 라구역 재개발 진행 현황과 가치 분석",
    "군포시 산본 신도시 노후 단지 정비사업 추진 방향",
    "평촌 신도시 재건축 선도지구 지정을 위한 주민 동의율",
    "하남시 덕풍동·신장동 정비사업과 3기 신도시 시너지",
    "남양주시 덕소뉴타운 한강변 입지의 희소성 분석",
    "용인시 수지구 리모델링 vs 재건축, 투자 가치 승자는?",
    "과천시 주공 아파트 재건축 잔여 단지(8, 9, 10단지) 현황",
    "시흥시 은행동·대야동 재개발 구역별 사업성 비교",
    "파주시 운정역 인근 재개발 후보지 선점 투자 전략",
    "김포시 북변구역 재개발(북변 3, 4, 5구역) 분석",
    "화성시 병점역 인근 재개발 추진 단지 임장기",
    "오산시 궐동 재개발 구역의 저평가 요인 분석",
    "평택시 합정동·세교동 정비사업과 삼성전자 호재",
    "이천시 증포동 인근 소규모 재건축 사업 진행 상황",
    "안성시 아양지구 인근 노후 단지 정비사업 전망",
    "양주시 덕정역 인근 GTX-C 호재와 재개발 가능성",
    "의정부시 장암구역·중앙구역 재개발 프리미엄 분석",
    "동두천시 생연동 인근 저가 재건축 아파트 공략법",
    "포천시 신읍동 인근 정비예정구역 진행 단계",
    "여주시 하동 재개발 사업 진행과 한강 조망 가치",
    "연천군 전곡읍 인근 노후 건물 정비사업 현황",
    "가평군·양평군 외곽 지역 소규모 주택 정비사업 트렌드",

    # 경매/공매 실전 기술
    "경매 초보자가 반드시 알아야 할 '대항력' 있는 임차인 구별법",
    "말소기준권리 6가지, 이것만 알면 권리분석 끝난다",
    "대법원 경매 정보지에서 꼭 확인해야 할 '주의사항' 문구들",
    "유치권 신고된 물건, 무조건 피해야 할까? 해결 가능성 분석",
    "지분 경매로 소액 투자하기: 공유물분할청구소송 활용법",
    "법정지상권 성립 여부 판단하는 3단계 체크리스트",
    "빌라 경매 낙찰 후 명도(내보내기) 협상 기술 5가지",
    "아파트 경매 입찰 전 미납 관리비 확인이 중요한 이유",
    "경매 잔금 대출(경락잔금대출) 한도와 금리 잘 받는 법",
    "명도 확인서와 인감증명서, 언제 주고받아야 안전할까?",
    "공매와 경매의 결정적 차이점 3가지와 세금 혜택",
    "법인 명의로 부동산 경매 입찰 시 장단점 총정리",
    "깡통전세 매물 경매 시 주의할 점: 선순위 임차인 배당 분석",
    "농지 취득 자격 증명(농취증) 발급 실패 시 보증금 몰수 피하는 법",
    "상가 경매 시 수익률 계산법: 공실 위험과 렌트프리 확인",
    "단독주택 경매 낙찰 후 리모델링 비용 산출 가이드",
    "토지 경매 투자의 핵심, 용도지역과 도로 조건 확인법",
    "유찰된 물건의 함정: 3회 이상 유찰된 매물 분석 노하우",
    "입찰표 작성 시 실수하여 보증금 날리는 사례 방지법",
    "경매 낙찰 후 취득세, 양도세 등 세금 절약하는 팁",

    # 정책/세금/심화
    "2026년 달라진 부동산 취득세 중과 세율 완벽 정리",
    "1주택자 일시적 2주택 비과세 혜택 기간과 조건",
    "양도소득세 장기보유특별공제 혜택 극대화하는 법",
    "상속받은 부동산 양도 시 취득가액 산정 기준 주의사항",
    "증여세 절감하는 '부담부증여' 전략의 실질적인 수익성",
    "종부세 합산배제 신청 방법과 대상 주택 확인하기",
    "주택임대사업자 등록 혜택과 의무 사항(2026년 기준)",
    "전세자금대출 규제 변화와 무주택자 내 집 마련 전략",
    "생애 최초 주택 구입자 취득세 감면 혜택 받는 법",
    "주택담보대출(DSR) 규제가 정비사업 시장에 미치는 영향",
    "재개발 입주권 보유 시 주택 수 산정 기준 총정리",
    "관리처분인가 후 취득한 입주권의 토지 취득세율 계산법",
    "재건축 초과이익 환수제 면제 금액과 산정 방식 변화",
    "노후 계획도시 특별법 통과 후 1기 신도시 투자 유망 단지",
    "GTX 노선별 개통 일정과 인근 정비사업지의 상관관계",
    "역세권 청년주택 개발 호재가 있는 노후 주거지 분석",
    "실거주 의무 폐지 여부에 따른 분양권 전매 제한 정리",
    "금리 인하 시기에 유리한 부동산 대출 갈아타기 전략",
    "아파트 브랜드 순위가 재건축 분담금에 미치는 영향",
    "부동산 하락기에도 살아남는 '똘똘한 한 채' 선별 기준"
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
        request = service.posts().list(blogId=blog_id, maxResults=100, fetchBodies=False)
        response = request.execute()
        return [item.get('title', '').lower() for item in response.get('items', [])]
    except Exception as e:
        print(f"⚠️ 기존 발행 글 목록 가져오기 실패: {e}")
        return []

def get_real_estate_topic():
    published_titles = get_published_titles()
    random.shuffle(FALLBACK_TOPICS)
    for topic in FALLBACK_TOPICS:
        topic_lower = topic.lower()
        is_duplicate = any(topic_lower in pub or pub in topic_lower for pub in published_titles if pub)
        if not is_duplicate:
            return topic
    return "2026년 하반기 부동산 시장 핵심 전망과 투자 전략"

# ====================== Hugging Face 이미지 생성 (재시도 로직 강화) ======================
def generate_image_hf(prompt):
    """Hugging Face API를 사용하되, 로딩(503) 에러와 타임아웃을 방어하는 강력한 재시도 로직 적용"""
    print(f"🎨 Hugging Face 이미지 생성 시작...")
    
    if not HF_TOKEN:
        print("❌ HF_TOKEN이 없습니다. 환경변수(.env 또는 Github Secrets)를 확인해주세요.")
        return None

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    
    # 모델 1순위 (FLUX), 2순위 (SDXL - 빠르고 안정적임)
    models = [
        "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    ]
    
    for model_url in models:
        model_name = model_url.split('/')[-1]
        print(f"📍 시도 중인 모델: {model_name}")
        max_retries = 6 # 최대 6번 재시도 
        
        for attempt in range(max_retries):
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=40)
                
                if response.status_code == 200:
                    image_bytes = response.content
                    print(f"✅ 이미지 생성 성공! (크기: {len(image_bytes)//1024}KB)")
                    return image_bytes
                    
                elif response.status_code == 503:
                    # 모델이 서버 메모리에 로드되는 중 (Cold Start)
                    try:
                        estimated_time = response.json().get('estimated_time', 10)
                    except:
                        estimated_time = 10
                    wait_time = min(estimated_time, 15) # 너무 길면 최대 15초씩 끊어서 대기
                    print(f"   ⏳ 모델 로딩 중... {wait_time:.1f}초 대기 후 재시도 ({attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    print(f"   ⚠️ API 에러 ({response.status_code}): {response.text}")
                    break # 503이 아닌 다른 에러면 이 모델은 포기하고 2순위 모델로 넘어감
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ 타임아웃 발생. 재시도 중... ({attempt+1}/{max_retries})")
                time.sleep(5)
            except Exception as e:
                print(f"   ❌ 예기치 않은 오류: {e}")
                break
                
    print("❌ 모든 모델에서 이미지 생성에 실패했습니다.")
    return None

# ====================== 콘텐츠 생성 ======================
def generate_content(topic):
    print(f"✍️ 부동산 심층 분석 글 생성 중: {topic}")

    prompt = f"""
    당신은 2026년 대한민국 최고의 부동산 실전 투자 블로그 '부의 지름길'의 수석 분석가입니다.
    주제: "{topic}" 에 대해 독자가 완벽히 이해하고 투자에 참고할 수 있는 **심층 분석(약 3,000자 이상)** 블로그 글을 작성해주세요.

    --- CRITICAL REQUIREMENTS ---
    1. 어투: 신뢰감 있고 전문적이며 정중한 어투 사용
    2. 글의 깊이: 구체적인 수치, 역사적 배경, 장단점, 투자 시뮬레이션 등을 상세하게 작성
    3. Formatting: ONLY HTML tags 사용. 절대 Markdown 코드 블록(```html, ``` 등)을 출력하지 마세요. 순수 텍스트로 바로 시작하세요.

    --- Structure your response EXACTLY like this ---
    [IMAGE_PROMPT: (이 블로그 썸네일에 어울리는 고품질 실사풍 영문 프롬프트를 1~2문장으로 작성. 반드시 영어로만 작성. 예: A highly detailed, photorealistic wide-angle shot of a luxury modern apartment complex in Seoul during sunset, wealth concept, cinematic lighting, 8k)]
    [TAGS: 태그1, 태그2, 태그3, 태그4]

    <article>
    <header><h1>[이모지가 포함된 매력적인 제목]</h1></header>
    <section class="introduction">
        <p>안녕하십니까, 부의 지름길 수석 분석가입니다. [서론]</p>
    </section>
    <section>
        <h2>핵심 투자 포인트 요약 💡</h2>
        <ul><li>[포인트 1]</li><li>[포인트 2]</li><li>[포인트 3]</li></ul>
    </section>
    <section>
        <h2>심층 입지 분석 및 현재 진행 현황 🏢</h2>
        <p>[상세 내용]</p>
    </section>
    <section>
        <h2>수익성 분석 및 예상 투자금 시뮬레이션 💰</h2>
        <p>[상세 내용]</p>
    </section>
    <section>
        <h2>투자 시 반드시 주의해야 할 리스크 ⚠️</h2>
        <p>[상세 내용]</p>
    </section>
    <section class="conclusion">
        <h2>부의 지름길 최종 코멘트 🧭</h2>
        <p>[결론]</p>
        <p><strong>*본 포스팅은 투자 참고용이며, 모든 투자의 책임은 본인에게 있습니다.*</strong></p>
    </section>
    </article>
    """

    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_TEXT_URL, json=payload, timeout=120)
        response.raise_for_status()
        content = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        # 가끔 생성되는 마크다운 잔재 완벽 제거
        content = content.replace('```html', '').replace('```', '').strip()
        content = convert_markdown_to_html(content)

        # 1. 이미지 프롬프트 추출
        img_match = re.search(r'\[IMAGE_PROMPT:\s*(.*?)\]', content)
        image_prompt = img_match.group(1).strip() if img_match else f"Modern luxury real estate in Seoul, professional architectural photography, high quality"

        # 2. 태그 추출
        tag_match = re.search(r'\[TAGS:\s*(.*?)\]', content)
        dynamic_tags = [t.strip() for t in tag_match.group(1).split(',')] if tag_match else []

        # 3. 본문 및 제목 추출
        article_start = content.find('<article>')
        body = content[article_start:].strip() if article_start != -1 else content
        title = body[body.find('<h1>') + 4 : body.find('</h1>')].strip() if '<h1>' in body else topic

        print(f"✅ 글 생성 성공: {title[:50]}...")
        print(f"🎨 추출된 이미지 프롬프트: {image_prompt}")
        return title, body, dynamic_tags, image_prompt

    except Exception as e:
        print(f"❌ 텍스트 생성 오류: {e}")
        return None, None, [], None

def post_to_blogger(title, content, dynamic_tags, image_bytes=None):
    if not title or not content:
        return

    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]

    labels = ["부동산투자", "부의지름길", "재테크"] + dynamic_tags
    labels = list(dict.fromkeys(labels))[:6]
    rating = round(random.uniform(4.7, 4.9), 1)

    # 이미지 처리
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode('utf-8')
        img_tag = f'<img src="data:image/jpeg;base64,{b64}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.12); margin-bottom: 30px;"/>'
    else:
        img_tag = ''

    styled_content = f"""
    <style>
      .wealth-content {{ font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; color: #333; line-height: 1.8; letter-spacing: -0.5px; word-break: keep-all; }}
      .wealth-content h2 {{ margin-top: 60px; margin-bottom: 25px; font-size: 1.6em; border-bottom: 2px solid #1a365d; padding-bottom: 10px; font-weight: 800; color: #1a365d; }}
      .wealth-content h3 {{ margin-top: 40px; margin-bottom: 20px; font-size: 1.3em; color: #2d3748; font-weight: bold; background-color: #edf2f7; padding: 10px 15px; border-left: 4px solid #3182ce; }}
      .wealth-content p {{ margin-bottom: 25px; font-size: 16px; text-align: justify; }}
      .wealth-content ul {{ margin-bottom: 35px; background-color: #fafafa; padding: 25px 25px 25px 45px; border-radius: 8px; border: 1px solid #e2e8f0; }}
      .wealth-content li {{ margin-bottom: 12px; font-size: 16px; font-weight: 500; }}
      .vibe-rating {{ text-align: right; margin-top: 60px; padding-top: 20px; border-top: 2px dashed #ddd; font-size: 1.45em; font-weight: bold; color: #f39c12; }}
    </style>

    <div class="wealth-content">
      {img_tag}
      {content}
      <div class="vibe-rating">
        ⭐ {rating} / 5.0
      </div>
    </div>
    """

    body = {"kind": "blogger#post", "title": title[:100], "content": styled_content, "labels": labels}

    try:
        service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ 포스팅 성공! 제목: {title[:60]}... | 별점: {rating}")
    except Exception as e:
        print(f"❌ Blogger 포스팅 실패: {e}")

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print("🚀 부의 지름길 부동산 자동 포스팅 시작")
    print(f" 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    topic = get_real_estate_topic()
    print(f"📌 선정된 주제: {topic}\n")

    # 1. Gemini로 글, 태그, 영문 이미지 프롬프트 한 번에 생성
    title, body, dynamic_tags, image_prompt = generate_content(topic)

    if title and body:
        # 2. 추출된 영문 프롬프트로 Hugging Face 이미지 생성
        image_bytes = None
        if image_prompt:
            image_bytes = generate_image_hf(image_prompt)

        # 3. 블로거에 포스팅
        post_to_blogger(title, body, dynamic_tags, image_bytes)
    else:
        print("❌ 콘텐츠 생성에 실패하여 포스팅을 취소합니다.")

    print(f"\n{'='*70}")
    print(f"🏁 자동 포스팅 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")