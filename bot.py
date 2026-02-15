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

# --- إعدادات الإيميل ---
EMAIL_USER = "oedn305@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") 
DATABASE_FILE = "applied_emails.txt"

# --- دالة ذكية لإيجاد الملف حتى لو فيه تكرار في الصيغة ---
def get_cv_path():
    for file in os.listdir('.'):
        # يبحث عن أي ملف يبدأ بـ My وينتهي بـ pdf
        if file.lower().startswith('my') and file.lower().endswith('.pdf'):
            print(f"📁 تم العثور على الملف: {file}")
            return file
    return None

CV_PATH = get_cv_path()

async def send_email_with_cv(target_email):
    if not CV_PATH:
        print("⚠️ خطأ: لم يتم العثور على ملف السيفي (تأكد من وجود ملف يبدأ بـ My وينتهي بـ .pdf)")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = f"طلب توظيف (ثانوية عامة) - تحديث {random.randint(1000, 9999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة. شكراً لكم."
        msg.attach(MIMEText(body, 'plain'))

        with open(CV_PATH, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            # يرسل للمستلم باسم نظيف واحترافي
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
    # قنص إيميلات من منصات الإعلانات المباشرة
    queries = [
        'site:sa.opensooq.com "إيميل" "ثانوي"',
        'site:mourjan.com "السعودية" "ثانوي" "إيميل"',
        '"@gmail.com" وظائف ثانوي الدمام 2026',
        'site:linkedin.com/jobs "ثانوي" "السعودية"'
    ]
    found_emails = set()
    for query in queries:
        try:
            await page.goto(f'https://www.google.com/search?q={query}&num=20')
            await asyncio.sleep(5)
            content = await page.content()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                if not any(x in e.lower() for x in ['google', 'w3.org', 'schema', 'facebook', 'twitter']):
                    found_emails.add(e.lower())
        except: continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print("🚀 انطلاق البوت اللانهائي - 2026")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        discovered_emails = await get_fresh_emails(page)
        
        # تحميل الذاكرة
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())
        else:
            applied_list = set()

        to_apply = [e for e in discovered_emails if e not in applied_list]
        print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف.")

        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم التقديم بنجاح على: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                # تأخير أطول قليلاً لضمان عدم الحظر
                await asyncio.sleep(random.randint(20, 40))

        await browser.close()
        print("🏁 المهمة اكتملت.")

if __name__ == "__main__":
    asyncio.run(run_bot())
