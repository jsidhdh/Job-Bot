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
    """دالة إرسال مصفحة ضد جميع أخطاء التشفير"""
    try:
        # 1. تنظيف قسري للإيميل من أي رموز غير إنجليزية
        clean_email = re.sub(r'[^a-zA-Z0-9@._+-]', '', target_email).strip()
        
        # 2. التأكد أن الإيميل ليس فارغاً بعد التنظيف
        if not clean_email or '@' not in clean_email:
            return False

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"طلب توظيف - ثانوية عامة - {random.randint(1000, 9999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة. شكراً لكم."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if CV_PATH:
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="CV_Professional.pdf"') 
                msg.attach(part)

        # 3. محاولة الإرسال وتجاهل أخطاء ASCII
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        # إرسال الرسالة مع تجاهل أي حرف لا يمكن تشفيره
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        # لو فشل، يطبع الخطأ ويكمل للهدف اللي بعده بدون ما يوقف البوت
        print(f"⚠️ تخطي إيميل {target_email} بسبب: {e}")
        return False

async def get_fresh_emails(page):
    # كلمات بحث قوية لزيادة عدد النتائج
    queries = [
        'site:sa.opensooq.com "إيميل" "ثانوي"',
        'site:mourjan.com "توظيف" "ثانوي" "إيميل"',
        '"@gmail.com" وظائف ثانوي الدمام الخبر'
    ]
    found_emails = set()
    for query in queries:
        try:
            await page.goto(f'https://www.google.com/search?q={query}&num=50')
            await asyncio.sleep(7)
            content = await page.content()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                if not any(x in e.lower() for x in ['google', 'facebook', 'twitter', 'sentry']):
                    found_emails.add(e.lower().strip())
        except: continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print(f"📁 الملف: {CV_PATH}")
        print("🚀 تشغيل وضع 'التخطي الذكي' - ضد أخطاء التشفير")
        
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        discovered_emails = await get_fresh_emails(page)
        
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())
        else:
            applied_list = set()

        to_apply = [e for e in discovered_emails if e not in applied_list]
        print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف.")

        success_count = 0
        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم التقديم: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                await asyncio.sleep(random.randint(15, 30))

        await browser.close()
        print(f"🏁 التقرير النهائي: تم إرسال {success_count} سيرة ذاتية.")

if __name__ == "__main__":
    asyncio.run(run_bot())
