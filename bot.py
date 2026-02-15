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
        if file.lower().startswith('my') and file.lower().endswith('.pdf'):
            return file
    return None

CV_PATH = get_cv_path()

async def send_email_with_cv(target_email):
    if not CV_PATH:
        print("⚠️ ملف السيفي غير موجود!")
        return False
    
    try:
        # تنظيف الإيميل من أي رموز مخفية قد تسبب خطأ ASCII
        clean_email = target_email.encode('ascii', 'ignore').decode('ascii').strip()
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"طلب توظيف (ثانوية عامة) - تحديث {random.randint(1000, 9999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة. شكراً لكم."
        # استخدام UTF-8 صراحة لحل مشكلة الترميز
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with open(CV_PATH, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="My_CV.pdf"') 
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ فشل الإرسال إلى {target_email}: {e}")
        return False

async def get_fresh_emails(page):
    # توسيع نطاق البحث ليشمل نتائج أكثر لعام 2026
    queries = [
        'site:sa.opensooq.com "إيميل" "ثانوي"',
        '"@gmail.com" وظائف ثانوي الدمام الخبر 2026',
        'site:twitter.com "ثانوي" "توظيف" "إيميل"',
        'site:mourjan.com "ثانوي" "إيميل"'
    ]
    found_emails = set()
    for query in queries:
        try:
            # طلب 50 نتيجة لزيادة عدد الإيميلات
            await page.goto(f'https://www.google.com/search?q={query}&num=50')
            await asyncio.sleep(6)
            content = await page.content()
            # استخراج الإيميلات
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                e_clean = e.lower().strip()
                if not any(x in e_clean for x in ['google', 'w3.org', 'schema', 'facebook', 'sentry']):
                    found_emails.add(e_clean)
        except: continue
    return list(found_emails)

async def run_bot():
    if not CV_PATH:
        print("❌ توقف: لم يتم العثور على ملف السيفي.")
        return

    async with async_playwright() as p:
        print(f"📁 الملف المستخدم: {CV_PATH}")
        print("🚀 انطلاق البوت اللانهائي - نسخة 2026 المحدثة")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        discovered_emails = await get_fresh_emails(page)
        
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())
        else:
            applied_list = set()

        to_apply = [e for e in discovered_emails if e not in applied_list]
        print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف جديدة.")

        success_count = 0
        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم التقديم بنجاح على: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                await asyncio.sleep(random.randint(15, 30))

        await browser.close()
        print(f"🏁 انتهت المهمة. تم إرسال {success_count} سيرة ذاتية بنجاح!")

if __name__ == "__main__":
    asyncio.run(run_bot())
