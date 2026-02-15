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

def get_cv_path():
    for file in os.listdir('.'):
        if file.lower().endswith('.pdf'):
            return file
    return None

CV_PATH = get_cv_path()

def is_valid_email(email):
    email = email.lower().strip()
    # استبعاد الإيميلات الوهمية التي تبدأ بـ 22 أو أرقام مشبوهة
    if re.match(r"^(22|123|test|abc)@", email): return False
    # استبعاد الدومينات التقنية
    bad_domains = ['google', 'facebook', 'sentry', 'w3.org', 'example', 'instagram', 'twitter', 'github']
    if any(d in email for d in bad_domains): return False
    return True

async def send_email_with_cv(target_email):
    clean_email = "".join(c for c in target_email if ord(c) < 128).strip()
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"Request for Job - High School Graduate - {random.randint(100, 999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة بمؤهل ثانوي. شكراً لكم."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if CV_PATH:
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="CV.pdf"') 
                msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"⚠️ فشل الإرسال إلى {target_email}: {e}")
        return False

async def get_fresh_emails(page):
    # كلمات بحث "انفجارية" لضمان عدم ظهور الرقم 0
    queries = [
        '"@gmail.com" وظائف ثانوي السعودية',
        '"@outlook.com" ثانوي توظيف الدمام الرياض',
        'site:sa.opensooq.com "أرسل السيرة"',
        'site:mourjan.com "ثانوي" "إيميل"',
        '"hr@" وظيفة ثانوي 2026',
        'site:tanqeeb.com "ثانوي" "gmail"'
    ]
    found_emails = set()
    for query in queries:
        try:
            print(f"🔎 قنص من: {query}")
            # حذفنا &tbs=qdr:m مؤقتاً لزيادة النتائج
            await page.goto(f'https://www.google.com/search?q={query}&num=100')
            await asyncio.sleep(5)
            content = await page.content()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                if is_valid_email(e):
                    found_emails.add(e.lower().strip())
        except: continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print(f"📁 السيفي: {CV_PATH}")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. البحث عن إيميلات
        discovered_emails = await get_fresh_emails(page)
        
        # 2. قراءة الملفات القديمة
        applied_list = set()
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())

        # 3. الفلترة
        to_apply = [e for e in discovered_emails if e not in applied_list]
        print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة.")

        success_count = 0
        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم الإرسال: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                await asyncio.sleep(random.randint(10, 20))

        await browser.close()
        print(f"🏁 التقرير: تم إرسال {success_count} سيرة ذاتية.")

if __name__ == "__main__":
    asyncio.run(run_bot())
