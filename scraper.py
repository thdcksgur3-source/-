import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 마감/삭제 공고 검증 키워드
EXPIRED_KEYWORDS = [
    '마감된 공고', '접수가 마감', '존재하지 않는', '종료된 채용', 
    '찾을 수 없습니다', '삭제된 게시글', 'Closed', 'Expired'
]

# 1. 사람인 공고 크롤링 함수 (중복 체크 키 추가)
def scrape_saramin_jobs():
    new_jobs = []
    seen_keys = set() # 현회차 키워드 간 중복 방지용
    
    keywords = ['회계', '재무', '세무', '원가', '감사', '결산']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for kw in keywords:
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchmode=general&searchword={kw}+인턴"
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('.item_recruit')

            for item in items[:5]:
                title_elem = item.select_one('.job_tit a')
                corp_elem = item.select_one('.corp_name a')
                cond_elems = item.select('.job_condition span')

                if not title_elem or not corp_elem:
                    continue

                title = title_elem.get_text(strip=True)
                company = corp_elem.get_text(strip=True)
                rel_link = title_elem.get('href', '')
                apply_url = f"https://www.saramin.co.kr{rel_link}" if rel_link.startswith('/') else rel_link

                # 💡 핵심: (회사명 + 공고제목) 조합으로 고유 식별 키 생성
                unique_key = f"{company}_{title}".replace(" ", "")
                if unique_key in seen_keys:
                    continue
                seen_keys.add(unique_key)

                location = cond_elems[0].get_text(strip=True) if len(cond_elems) > 0 else '서울'
                type_info = cond_elems[1].get_text(strip=True) if len(cond_elems) > 1 else '인턴'

                # 메인 카테고리 분류
                main_category = 'GENERAL'
                if any(defense_kw in company or defense_kw in title for defense_kw in ['한화', 'LIG', 'KAI', '로템', '풍산', '방산', '방위']):
                    main_category = 'DEFENSE'
                elif any(big4_kw in company or big4_kw in title for big4_kw in ['삼일', '삼정', '안진', '한영', 'PwC', 'KPMG', 'Deloitte', 'EY']):
                    main_category = 'BIG4'

                sub_categories = []
                if '원가' in title or '원가' in kw: sub_categories.append('원가')
                if '회계' in title or '감사' in title or '결산' in title: sub_categories.append('회계')
                if '재무' in title or '자금' in title: sub_categories.append('재무')
                if '세무' in title or '세법' in title: sub_categories.append('세법')
                if not sub_categories: sub_categories = ['회계']

                job_item = {
                    "id": f"saramin_{hash(unique_key)}",
                    "uniqueKey": unique_key, # 중복 비교용 고유 키
                    "mainCategory": main_category,
                    "company": company,
                    "title": title,
                    "location": location,
                    "type": type_info,
                    "subCategories": sub_categories,
                    "keywords": [kw, "인턴", "사람인"],
                    "deadline": "공시 참조",
                    "description": f"{company}의 {title} 채용공고입니다. 사람인 공식 페이지를 통해 상세내용 확인 및 지원이 가능합니다.",
                    "qualifications": "상경계열, 회계/재무 관련 자격증 우대 및 채용 공고 참조",
                    "applyUrl": apply_url
                }
                new_jobs.append(job_item)
        except Exception as e:
            print(f"사람인 '{kw}' 검색 오류: {e}")

    return new_jobs

# 2. Cross 검증 함수
def validate_job_link(apply_url):
    if not apply_url or not apply_url.startswith('http'):
        return False

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(apply_url, headers=headers, timeout=5, allow_redirects=True)
        if response.status_code != 200:
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        for kw in EXPIRED_KEYWORDS:
            if kw in page_text:
                return False
                
        return True
    except Exception:
        return False

# 3. 네이버 메일 알림 함수
def send_email_notification(new_jobs):
    sender_email = os.environ.get('EMAIL_USER')
    sender_password = os.environ.get('EMAIL_PASS')
    receiver_email = sender_email

    if not sender_email or not sender_password:
        print("이메일 설정(EMAIL_USER/EMAIL_PASS)이 없어 메일 발송을 건너뜁니다.")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🛡️ [DefFinance] 신규 인턴 공고 {len(new_jobs)}건이 등록되었습니다!"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    html_content = "<h2>🛡️ DefFinance 실시간 채용공고 알림</h2><hr>"
    for job in new_jobs:
        cat_badge = "🛡️ 방산" if job.get('mainCategory') == 'DEFENSE' else ("🏢 Big 4" if job.get('mainCategory') == 'BIG4' else "💼 일반/대기업")
        html_content += f"""
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #e2e8f0; border-radius: 10px;">
            <p style="margin:0; font-size: 12px; color: #475569;"><b>[{cat_badge}] {job.get('company')}</b></p>
            <h3 style="margin: 5px 0; color: #1e293b;">{job.get('title')}</h3>
            <p style="font-size: 13px; color: #64748b; margin: 5px 0;">📍 {job.get('location')} | 마감일: {job.get('deadline')}</p>
            <a href="{job.get('applyUrl')}" style="display: inline-block; margin-top: 8px; padding: 6px 12px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-size: 12px;">채용 공고글 바로가기 ↗</a>
        </div>
        """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.naver.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"[{datetime.now()}] 네이버 메일 알림 발송 완료!")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")

# 4. 메인 업데이트 및 강력한 중복 제거 로직
def update_jobs_json():
    filename = 'jobs.json'
    existing_jobs = []
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_jobs = json.load(f)
            except:
                existing_jobs = []

    # 💡 기존 데이터 전체에 대해 중복 키(uniqueKey 및 URL) 집합 생성
    existing_keys = set()
    existing_urls = set()
    cleaned_existing_jobs = []

    # 기존 jobs.json 자체에 쌓인 중복 정리 (청소)
    for job in existing_jobs:
        u_key = job.get('uniqueKey') or f"{job.get('company')}_{job.get('title')}".replace(" ", "")
        u_url = job.get('applyUrl')
        
        if u_key not in existing_keys and u_url not in existing_urls:
            job['uniqueKey'] = u_key
            existing_keys.add(u_key)
            existing_urls.add(u_url)
            cleaned_existing_jobs.append(job)

    # 새로 수집된 공고
    fetched_jobs = scrape_saramin_jobs()
    new_jobs_added = []
    
    for job in fetched_jobs:
        u_key = job.get('uniqueKey')
        u_url = job.get('applyUrl')
        
        # 💡 회사명+제목 키 및 URL 모두에 중복이 없는 순수한 신규 공고만 선별
        if u_key not in existing_keys and u_url not in existing_urls:
            if validate_job_link(u_url):
                cleaned_existing_jobs.insert(0, job)
                new_jobs_added.append(job)
                existing_keys.add(u_key)
                existing_urls.add(u_url)
            
    # 정제된 데이터 파일 저장
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_existing_jobs, f, ensure_ascii=False, indent=2)
        
    if new_jobs_added:
        send_email_notification(new_jobs_added)
        print(f"신규 공고 {len(new_jobs_added)}건 수집 및 알림 완료. (기존 중복 청소 완료)")
    else:
        print("중복 정리 완료. 새로운 유효 공고가 없습니다.")

if __name__ == '__main__':
    update_jobs_json()
