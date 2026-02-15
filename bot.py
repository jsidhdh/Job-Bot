import asyncio
import os
import re
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from playwright.async_api import async_playwright

# --- الإعدادات ---
EMAIL_USER = "oedn305@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") 
DATABASE_FILE = "applied_emails.txt"
BLACKLIST_FILE = "blacklist.txt"

def get_cv_path():
    for file in os.listdir('.'):
        if file.lower().endswith('.pdf'):
            return file
    return None

CV_PATH = get_cv_path()

def is_valid_email(email):
    """فلترة الإيميلات الوهمية والأرقام المكررة قبل الإرسال"""
    email = email.lower().strip()
    # استبعاد الإيميلات التي تبدأ بـ 22 أو أرقام مشبوهة أو خدمات تقنية
    bad_prefixes = ['22@', '123@', 'test@', 'noreply@', 'support@']
    bad_domains = ['google', 'facebook', 'sentry', 'w3.org', 'example', 'instagram', 'twitter']
    
    if any(email.startswith(p) for p in bad_prefixes): return False
    if any(d in email for d in bad_domains): return False
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email): return False
    return True

async def send_email_with_cv(target_email):
    # تنظيف الإيميل من أي رموز مخفية نهائياً
    clean_email = "".join(c for c in target_email if ord(c) < 128).strip()
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"Request for Job - High School Graduate - {random.randint(1000, 9999)}"
        
        body = "السلام عليكم ورحمة الله وبركاته،\n\nأرفق لكم سيرتي الذاتية لطلب الانضمام لفريقكم العمل (مؤهل ثانوي). أتطلع لسماع ردكم.\n\nمع الشكر والتقدير."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if CV_PATH:
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="Resume.pdf"') 
                msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        with open(BLACKLIST_FILE, "a") as f:
            f.write(target_email + "\n")
        print(f"⚠️ فشل وتم الحظر: {target_email} | الخطأ: {e}")
        return False

async def get_fresh_emails(page):
    # كلمات بحث تستهدف إيميلات التوظيف (HR) الحقيقية
    queries = [
        'site:sa.opensooq.com "أرسل السيرة" "ثانوي"',
        'site:mourjan.com "توظيف" "ثانوي" "gmail"',
        '"hr@" وظائف ثانوي السعودية 2026',
        '"jobs@" شركة ثانوي الدمام 2026',
        '"careers@" وظيفة ثانوي الرياض 2026',
        'site:linkedin.com/posts "ثانوي" "إيميل" "السعودية"'
    ]
    found_emails = set()
    for query in queries:
        try:
            print(f"🔎 قنص أهداف ذكية: {query[:40]}...")
            # جلب نتائج الشهر الأخير فقط لضمان وظائف حقيقية tbs=qdr:m
            await page.goto(f'https://www.google.com/search?q={query}&num=50&tbs=qdr:m')
            await asyncio.sleep(random.randint(5, 7))
            content = await page.content()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                if is_valid_email(e):
                    found_emails.add(e.lower().strip())
        except: continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print(f"📁 السيفي المعتمد: {CV_PATH}")
        print("🚀 انطلاق نسخة القنص الذكي - 2026")
        
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        discovered_emails = await get_fresh_emails(page)
        
        ignore_list = set()
        for f_name in [DATABASE_FILE, BLACKLIST_FILE]:
            if os.path.exists(f_name):
                with open(f_name, "r") as f:
                    ignore_list.update(f.read().splitlines())

        to_apply = [e for e in discovered_emails if e not in ignore_list]
        print(f"🎯 المستهدف اليوم بعد التنظيف: {len(to_apply)} جهة حقيقية.")

        success_count = 0
        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم التقديم بنجاح: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                await asyncio.sleep(random.randint(20, 40))

        await browser.close()
        print(f"🏁 تم إرسال {success_count} سيرة ذاتية بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
