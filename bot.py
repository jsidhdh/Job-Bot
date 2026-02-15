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

async def send_email_with_cv(target_email):
    # تنظيف قسري للإيميل من أي رموز ASCII معطوبة
    clean_email = "".join(c for c in target_email if ord(c) < 128).strip()
    if not clean_email or '@' not in clean_email: return False

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"Request for Job Opportunity - High School Graduate - {random.randint(1000, 9999)}"
        
        body = "السلام عليكم ورحمة الله وبركاته،\n\nأرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة (مؤهل ثانوي). أتمنى لي ولكم التوفيق.\n\nشكراً لكم."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if CV_PATH:
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="CV_Professional.pdf"') 
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
        print(f"⚠️ تم حظر إيميل معطوب: {target_email}")
        return False

async def get_fresh_emails(page):
    # قائمة بحث ضخمة لضمان نتائج تتخطى الـ 0
    queries = [
        'site:sa.opensooq.com "إيميل" "ثانوي"',
        'site:mourjan.com "السعودية" "ثانوي" "إيميل"',
        'site:twitter.com "ثانوي" "إيميل" "توظيف"',
        'site:facebook.com "وظائف" "ثانوي" "السعودية" "gmail"',
        'site:instagram.com "ثانوي" "إيميل" "الدمام"',
        '"@gmail.com" وظائف ثانوي الرياض 2026',
        '"@outlook.com" وظائف ثانوي جدة 2026',
        '"@hotmail.com" وظائف ثانوي الشرقية 2026',
        'site:tanqeeb.com "ثانوي" "السعودية" "إيميل"'
    ]
    found_emails = set()
    for query in queries:
        try:
            print(f"🔎 قنص أهداف من: {query[:30]}...")
            await page.goto(f'https://www.google.com/search?q={query}&num=100')
            await asyncio.sleep(random.randint(7, 10))
            content = await page.content()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                e_clean = e.lower().strip()
                if not any(x in e_clean for x in ['google', 'facebook', 'instagram', 'sentry', 'w3.org']):
                    found_emails.add(e_clean)
        except: continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print(f"📁 السيفي المكتشف: {CV_PATH}")
        print("🚀 انطلاق وضع 'الاكتساح الشامل' لعام 2026")
        
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        discovered_emails = await get_fresh_emails(page)
        
        ignore_list = set()
        for f_name in [DATABASE_FILE, BLACKLIST_FILE]:
            if os.path.exists(f_name):
                with open(f_name, "r") as f:
                    ignore_list.update(f.read().splitlines())

        to_apply = [e for e in discovered_emails if e not in ignore_list]
        print(f"🎯 المستهدف اليوم بعد الفلترة: {len(to_apply)} جهة توظيف جديدة.")

        success_count = 0
        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم الإرسال بنجاح إلى: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                await asyncio.sleep(random.randint(20, 45))

        await browser.close()
        print(f"🏁 التقرير النهائي: تم إرسال {success_count} سيرة ذاتية بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
