import os
import re
import requests
from bs4 import BeautifulSoup
import smtplib
import time
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY")
DB_FILE = "applied_emails.txt"

def get_cv_file():
    return next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

def send_cv_to_company(company_email):
    """إرسال السيفي بنظام التشفير لضمان الوصول"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Job Applicant <{MY_EMAIL}>"
        msg['To'] = company_email
        msg['Subject'] = f"طلب توظيف (ثانوية عامة) - جاهز للمباشرة - كود {random.randint(100,999)}"
        body = "السلام عليكم، أتقدم بطلبي للعمل في شركتكم الموقرة (لحملة الثانوية). السيرة الذاتية مرفقة."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        cv_path = get_cv_file()
        if cv_path:
            with open(cv_path, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="CV_Application.pdf"')
                msg.attach(part)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except: return False

def deep_scan():
    """البحث بعمق في صفحات الوظائف لآخر 3 شهور"""
    print("🔎 جاري تشغيل الرادار العميق لآخر 3 شهور...")
    
    # 1. قائمة إيميلات احتياطية (شركات توظف ثانوي دائماً) لضمان عدم خروج البوت بـ 0 نتائج
    backup_emails = [
        "recruitment@nesma.com", "hr@sraco.com.sa", "careers@alfanar.com",
        "jobs@zamilindustrial.com", "hr@tamimi-group.com", "cv@znth.com.sa",
        "jobs@daralriyadh.com", "recruitment@sendan.com.sa", "jobs@catcon.com.sa"
    ]
    
    found_emails = set(backup_emails)

    # 2. محاولة سحب إيميلات من المواقع (توسيع نطاق البحث)
    search_urls = [
        "https://www.wadhefa.com/news/",
        "https://www.ewdifh.com/jobs/",
        "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-لحملة-الثانوية"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in search_urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            # استخراج أي إيميل يظهر في الصفحة
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            for email in emails:
                if not any(d in email for d in ["tanqeeb", "google", "wadhefa", "ewdifh"]):
                    found_emails.add(email.lower())
        except: continue

    print(f"✅ تم تجهيز قائمة بـ {len(found_emails)} إيميل (منها شركات نشطة حالياً).")

    # 3. التقديم الآلي
    applied = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: applied = f.read().splitlines()

    success = 0
    for email in found_emails:
        if email not in applied:
            print(f"📧 جاري تقديم السيفي إلى: {email}...")
            if send_cv_to_company(email):
                print("✅ تم الإرسال!")
                with open(DB_FILE, 'a') as f: f.write(email + "\n")
                success += 1
                time.sleep(20) # وقت راحة لضمان عدم الحظر
            if success >= 10: break

    if success == 0:
        print("📭 تم مراسلة جميع الشركات المتاحة مسبقاً.")

if __name__ == "__main__":
    deep_scan()
