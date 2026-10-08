import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email_notification(new_jobs):
    sender_email = os.environ.get('EMAIL_USER')
    sender_password = os.environ.get('EMAIL_PASS')
    receiver_email = sender_email  # 네이버 본인 메일함으로 수신

    if not sender_email or not sender_password:
        print("이메일 계정 정보(EMAIL_USER/EMAIL_PASS)가 설정되지 않아 메일 발송을 건너뜁니다.")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🛡️ [DefFinance] 신규 인턴 공고 {len(new_jobs)}건이 등록되었습니다!"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    html_content = "<h2>🛡️ DefFinance 신규 채용공고 알림</h2><hr>"
    for job in new_jobs:
        cat_badge = "🛡️ 방산" if job.get('mainCategory') == 'DEFENSE' else "🏢 Big 4"
        html_content += f"""
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #e2e8f0; border-radius: 10px;">
            <p style="margin:0; font-size: 12px; color: #475569;"><b>[{cat_badge}] {job.get('company')}</b></p>
            <h3 style="margin: 5px 0; color: #1e293b;">{job.get('title')}</h3>
            <p style="font-size: 13px; color: #64748b; margin: 5px 0;">📍 {job.get('location')} | 마감일: {job.get('deadline')}</p>
            <a href="{job.get('applyUrl')}" style="display: inline-block; margin-top: 8px; padding: 6px 12px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-size: 12px;">공식 지원 페이지 바로가기 ↗</a>
        </div>
        """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.naver.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"[{datetime.now()}] 네이버 메일로 신규 공고 알림 발송 완료!")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")

def update_jobs_json():
    filename = 'jobs.json'
    existing_jobs = []
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_jobs = json.load(f)
            except:
                existing_jobs = []

    # 실제 크롤링 수집 데이터 (예시)
    fetched_jobs = []

    existing_urls = {j.get('applyUrl') for j in existing_jobs}
    new_jobs_added = []
    
    for job in fetched_jobs:
        if job.get('applyUrl') not in existing_urls:
            existing_jobs.insert(0, job)
            new_jobs_added.append(job)
            
    if new_jobs_added:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_jobs, f, ensure_ascii=False, indent=2)
        
        send_email_notification(new_jobs_added)
        print(f"신규 공고 {len(new_jobs_added)}건 업데이트 및 알림 완료.")
    else:
        print("새로운 공고가 없습니다.")

if __name__ == '__main__':
    update_jobs_json()
