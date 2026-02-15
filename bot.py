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

async def send_email_with_cv(target_email):
    clean_email = "".join(c for c in target_email if ord(c) < 128).strip()
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"طلب توظيف - ثانوية عامة - {random.randint(100, 999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة. شكراً لكم."
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
        return False

async def get_fresh_emails(page):
    # كلمات بحث لمناطق جديدة لضمان نتائج غير مكررة
    queries = [
        '"@gmail.com" وظائف ثانوي جدة مكة 2026',
        '"@outlook.com" ثانوي توظيف الرياض القصيم',
        '"@hotmail.com" وظائف ثانوي أبها جازان تبوك',
        'site:sa.opensooq.com "السيرة الذاتية" "ثانوي"',
        'site:mourjan.com "مطلوب موظفين" "ثانوي"',
        '"hr@" شركة توظيف ثانوي 2026'
    ]
    found_emails = set()
    for query in queries:
        try:
            print(f"🔎 قنص من: {query}")
            await page.goto(f'https://www.google.com/search?q={query}&num=100')
            await asyncio.sleep(5)
            content = await page.content()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                # فلترة الإيميلات الوهمية والمكررة
                e_clean = e.lower().strip()
                if not e_clean.startswith('22@') and not any(x in e_clean for x in ['google', 'facebook', 'w3.org']):
                    found_emails.add(e_clean)
        except: continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print(f"📁 الملف المستخدم: {CV_PATH}")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        discovered_emails = await get_fresh_emails(page)
        
        applied_list = set()
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())

        to_apply = [e for e in discovered_emails if e not in applied_list]
        print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف جديدة.")

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
