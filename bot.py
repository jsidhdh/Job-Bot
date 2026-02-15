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
    """البحث عن ملف السيفي مهما كان اسمه"""
    for file in os.listdir('.'):
        if file.lower().endswith('.pdf'):
            return file
    return None

CV_PATH = get_cv_path()

def hardcore_clean_email(email_str):
    """تنظيف الإيميل من أي رموز مخفية أو عربية نهائياً"""
    # يمسح أي حرف ليس (أرقام، حروف إنجليزية، نقطة، آت، شرطة)
    return re.sub(r'[^a-zA-Z0-9@._+-]', '', email_str).strip()

async def send_email_with_cv(target_email):
    if not CV_PATH:
        print("⚠️ ملف السيفي غير موجود!")
        return False
    
    try:
        # تنظيف قسري للإيميل قبل الإرسال
        clean_email = hardcore_clean_email(target_email)
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"طلب توظيف - ثانوية عامة - {random.randint(1000, 9999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة. شكراً لكم."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with open(CV_PATH, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="CV_Professional.pdf"') 
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        # إرسال بنظام ASCII الإجباري بعد التنظيف
        server.sendmail(EMAIL_USER, clean_email, msg.as_string().encode('ascii', errors='ignore').decode('ascii'))
        server.quit()
        return True
    except Exception as e:
        print(f"❌ فشل الإرسال إلى {target_email}: {e}")
        return False

async def get_fresh_emails(page):
    """قنص إيميلات جديدة من محركات البحث"""
    queries = [
        'site:sa.opensooq.com "إيميل" "ثانوي"',
        'site:mourjan.com "توظيف" "ثانوي" "إيميل"',
        '"@gmail.com" وظائف ثانوي الدمام الخبر 2026'
    ]
    found_emails = set()
    for query in queries:
        try:
            await page.goto(f'https://www.google.com/search?q={query}&num=30')
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
        print(f"📁 الملف المستخدم: {CV_PATH}")
        print("🚀 انطلاق النسخة النهائية - معالجة قوية للأخطاء")
        
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
                print(f"✅ تم الإرسال بنجاح إلى: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                await asyncio.sleep(random.randint(15, 30))

        await browser.close()
        print(f"🏁 التقرير: تم إرسال {success_count} سيرة ذاتية.")

if __name__ == "__main__":
    asyncio.run(run_bot())
