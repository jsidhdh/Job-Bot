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

# --- الإعدادات الأساسية ---
EMAIL_USER = "oedn305@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") 
DATABASE_FILE = "applied_emails.txt"

def get_cv_path():
    """يبحث عن أي ملف PDF في المجلد ويرسله"""
    for file in os.listdir('.'):
        if file.lower().endswith('.pdf'):
            return file
    return None

CV_PATH = get_cv_path()

def clean_text(text):
    """دالة لتنظيف الإيميلات والنصوص من أي رموز غير مرئية تسبب أخطاء"""
    return "".join(i for i in text if ord(i) < 128).strip()

async def send_email_with_cv(target_email):
    if not CV_PATH:
        print("⚠️ خطأ: لا يوجد ملف PDF!")
        return False
    
    try:
        # تنظيف الإيميل تماماً من أي رموز ASCII غريبة
        target_email = clean_text(target_email)
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = f"طلب توظيف (ثانوية عامة) - {random.randint(1000, 9999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة. شكراً لكم."
        # استخدام UTF-8 صراحة
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
    """يبحث في قوقل ويجلب إيميلات الشركات المباشرة"""
    queries = [
        'site:sa.opensooq.com "إيميل" "ثانوي"',
        '"@gmail.com" وظائف ثانوي الدمام الخبر 2026',
        'site:mourjan.com "توظيف" "ثانوي" "إيميل"',
        'site:twitter.com "ثانوي" "إيميل" السعودية'
    ]
    found_emails = set()
    for query in queries:
        try:
            # طلب عدد نتائج أكبر لزيادة الفرص
            await page.goto(f'https://www.google.com/search?q={query}&num=40')
            await asyncio.sleep(random.randint(5, 8))
            content = await page.content()
            # استخراج الإيميلات
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                e_clean = e.lower().strip()
                # تجنب الإيميلات التقنية غير المفيدة
                if not any(x in e_clean for x in ['google', 'w3.org', 'schema', 'sentry', 'facebook', 'twitter']):
                    found_emails.add(e_clean)
        except: continue
    return list(found_emails)

async def run_bot():
    if not CV_PATH:
        print("❌ توقف: لم يتم العثور على أي ملف PDF في المستودع.")
        return

    async with async_playwright() as p:
        print(f"📁 الملف المستخدم حالياً: {CV_PATH}")
        print("🚀 انطلاق البوت المطور - إصلاح شامل للأخطاء 2026")
        
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()

        discovered_emails = await get_fresh_emails(page)
        
        # تحميل سجل الإرسال السابق
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())
        else:
            applied_list = set()

        to_apply = [e for e in discovered_emails if e not in applied_list]
        print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف جديدة.")

        success_count = 0
        for email in to_apply:
            # محاولة الإرسال مع تنظيف الإيميل
            if await send_email_with_cv(email):
                print(f"✅ تم الإرسال بنجاح إلى: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                # تأخير عشوائي لحماية الإيميل من الحظر
                await asyncio.sleep(random.randint(15, 30))
            else:
                continue # لو فشل واحد يكمل الباقي

        await browser.close()
        print(f"🏁 انتهت المهمة. تم إرسال {success_count} سيرة ذاتية بنجاح!")

if __name__ == "__main__":
    asyncio.run(run_bot())
