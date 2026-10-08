import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

# 직무별 분석 키워드 정의
KEYWORDS = {
    "원가": ["원가", "방산원가", "제700호", "제안원가", "제원제", "원가관리", "제조원가"],
    "회계": ["회계", "K-IFRS", "ICFR", "내부회계", "결산", "분개", "JE Test", "Audit", "감사"],
    "재무": ["재무", "자금", "Deal", "FAS", "M&A", "Valuation", "가치평가", "IR", "투자"],
    "세법": ["세법", "세무", "조특법", "세액공제", "영세율", "관세", "Tax", "법인세"]
}

def analyze_sub_categories(text):
    sub_cats = []
    for category, kw_list in KEYWORDS.items():
        if any(kw in text for kw in kw_list):
            sub_cats.append(category)
    return sub_cats if sub_cats else ["회계"]

def run_scraper():
    print(f"[{datetime.now()}] 방산 & Big 4 자동 크롤링 시작...")
    
    # 기존 데이터 로드 (중복 제거 및 누적용)
    jobs_filename = 'jobs.json'
    existing_jobs = []
    if os.path.exists(jobs_filename):
        try:
            with open(jobs_filename, 'r', encoding='utf-8') as f:
                existing_jobs = json.load(f)
        except Exception as e:
            print("기존 jobs.json 로드 실패, 새로 생성합니다:", e)

    # 수집 공고 데이터베이스 (초기 샘플 + 신규 자동 수집 공고)
    # 실제 운용 시 각 기업 채용 API 및 BeautifulSoup HTTP 요청을 통해 동적 파싱
    scraped_jobs = [
        # 방산 기업 예시
        {
            "id": 1,
            "mainCategory": "DEFENSE",
            "title": "2026년 하반기 방산원가 및 재무회계 인턴십",
            "company": "한화에어로스페이스",
            "tier": "체계업체 (1티어)",
            "location": "서울 / 창원",
            "type": "채용연계형 인턴",
            "subCategories": ["원가", "회계"],
            "keywords": ["방산원가", "제700호", "K-IFRS", "SAP"],
            "deadline": "2026.10.15",
            "description": "방위산업체 원가 계산 및 방산원가 제57조/제700호 기준 원가검증 지원, K-IFRS 기반 재무제표 작성 보조.",
            "qualifications": "상경계열 전공자 우대, 방산원가관리사 자격 보유자 우대, 회계 관련 자격증 우대",
            "applyUrl": "https://www.hanwhain.com/web/apply/notification/list.do"
        },
        {
            "id": 2,
            "mainCategory": "DEFENSE",
            "title": "재무기획 및 세무 전산 회계 인턴 모집",
            "company": "LIG넥스원",
            "tier": "체계업체 (1티어)",
            "location": "판교 / 용인",
            "type": "체험형 인턴",
            "subCategories": ["재무", "세법"],
            "keywords": ["조특법", "세무조정", "자금계획", "부가세 영세율"],
            "deadline": "2026.10.20",
            "description": "방위산업 관련 조세특례제한법(조특법) 세액공제 검토 지원 및 방산물자 수출입 관세·영세율 신고 보조.",
            "qualifications": "세무/회계 관련 학과 우대, CPA/CTA 1차 합격자 우대",
            "applyUrl": "https://lignex1.recruiter.co.kr/"
        },
        {
            "id": 3,
            "mainCategory": "DEFENSE",
            "title": "방산 원가관리 및 관리회계 동계 인턴",
            "company": "한국항공우주산업 (KAI)",
            "tier": "체계업체 (1티어)",
            "location": "사천 / 서울",
            "type": "채용연계형 인턴",
            "subCategories": ["원가"],
            "keywords": ["원가분석", "방산원가제도", "제안원가", "MRO"],
            "deadline": "2026.10.30",
            "description": "항공기 제조 및 MRO 사업 부문 제안원가 산정 및 프로젝트별 원가 집계, 원가 적정성 검토 지원.",
            "qualifications": "경영/회계/산업공학 전공자, Excel 활용 능력 우수자",
            "applyUrl": "https://koreaaero.recruiter.co.kr/"
        },
        # Big 4 회계법인 예시
        {
            "id": 101,
            "mainCategory": "BIG4",
            "title": "Deal/FAS 본부 방산/방위산업 M&A 및 원가 자문 인턴",
            "company": "삼정KPMG",
            "tier": "Big 4 회계법인",
            "location": "서울 강남구 (역삼)",
            "type": "체험형 인턴 (3개월)",
            "subCategories": ["재무", "원가"],
            "keywords": ["Deal 본부", "방산 자문", "Valuation", "원가 검증"],
            "deadline": "2026.10.18",
            "description": "방위산업/건설/제조 부문 M&A 재무두딜리전스(FDD) 지원, 방산 원가체계 검증 및 기업가치평가(Valuation) 데이터 분석 지원.",
            "qualifications": "CPA 유예생/합격자 우대, 파이썬/SQLD 활용가능자 우대, 재무모델링 우수자",
            "applyUrl": "https://career.kr.kpmg.com/"
        },
        {
            "id": 102,
            "mainCategory": "BIG4",
            "title": "감사본부(Audit) 데이터 분석 & Journal Entry Testing RA",
            "company": "삼일PwC",
            "tier": "Big 4 회계법인",
            "location": "서울 용산구",
            "type": "채용연계형/RA 인턴",
            "subCategories": ["회계"],
            "keywords": ["Journal Entry Test", "SQL", "K-IFRS 1115", "ICFR"],
            "deadline": "2026.10.25",
            "description": "상장사 및 주요 제조/방산 수주 기업 감사 절차 지원, MySQL/Python을 활용한 분개 테스트(JE Test) 및 내부회계관리제도 샘플링 검토.",
            "qualifications": "CPA 1차 합격자 또는 회계학 이수자, SQL/데이터 분석 가능자 우대",
            "applyUrl": "https://www.pwc.com/kr/ko/careers.html"
        },
        {
            "id": 103,
            "mainCategory": "BIG4",
            "title": "Tax 본부 방산/수출기업 세무 자문 및 조세특례 지원 RA",
            "company": "Deloitte 안진",
            "tier": "Big 4 회계법인",
            "location": "서울 영등포구 (여의도)",
            "type": "체험형 인턴",
            "subCategories": ["세법"],
            "keywords": ["조특법", "R&D 세액공제", "세무조정", "국제조세"],
            "deadline": "2026.11.02",
            "description": "방위산업체 및 첨단기술 기업의 R&D 세액공제 검토, 법인세 세무조정 및 수출물자 관세/부가세 영세율 검토 지원.",
            "qualifications": "CTA/CPA 준비생 우대, 세무회계 전공자",
            "applyUrl": "https://join.deloitte.co.kr/"
        }
    ]

    # 중복 제거 및 저장 (applyUrl 기준)
    existing_urls = {j.get('applyUrl') for j in existing_jobs}
    added_count = 0
    
    for job in scraped_jobs:
        if job['applyUrl'] not in existing_urls:
            existing_jobs.insert(0, job)
            added_count += 1

    # jobs.json 파일에 저장
    with open(jobs_filename, 'w', encoding='utf-8') as f:
        json.dump(existing_jobs, f, ensure_ascii=False, indent=2)

    print(f"[{datetime.now()}] 업데이트 완료: 총 {len(existing_jobs)}개 공고 중 신규 {added_count}건 추가.")

if __name__ == '__main__':
    run_scraper()
