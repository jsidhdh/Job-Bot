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

# --- الإعدادات (تأكد من ضبط Secret في GitHub باسم EMAIL_PASSWORD) ---
EMAIL_USER = "oedn305@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") 
CV_PATH = "My_CV.pdf"
DATABASE_FILE = "applied_emails.txt"

async def send_email_with_cv(target_email):
    """دالة إرسال الإيميل مع مرفق السيرة الذاتية"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = f"طلب توظيف (ثانوية عامة) - تحديث {random.randint(1000, 9999)}"
        
        body = """السلام عليكم ورحمة الله وبركاته،
        
أتقدم لسيادتكم بطلب التوظيف لمؤهل (الثانوية العامة). أنا شاب سعودي لدي الطموح والجدية للعمل ضمن فريقكم.
مرفق لكم السيرة الذاتية (CV) للاطلاع عليها.

شاكر ومقدر لكم وقتكم."""

        msg.attach(MIMEText(body, 'plain'))

        if os.path.exists(CV_PATH):
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename={CV_PATH}")
                msg.attach(part)
        else:
            print(f"⚠️ ملف {CV_PATH} غير موجود!")
            return False

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
    """دالة البحث عن إيميلات جديدة في منصات متعددة"""
    queries = [
        'site:sa.opensooq.com "إيميل" "ثانوي"',
        'site:mourjan.com "السعودية" "ثانوي" "إيميل"',
        'site:bebee.com "السعودية" "ثانوي" "وظائف"',
        '"@gmail.com" وظائف ثانوي الدمام 2026',
        '"@outlook.com" توظيف ثانوي الخبر 2026',
        'site:linkedin.com/jobs "ثانوي" "السعودية"'
    ]
    
    found_emails = set()
    for query in queries:
        try:
            print(f"🔎 جاري القنص في: {query}")
            await page.goto(f'https://www.google.com/search?q={query}&num=30')
            await asyncio.sleep(random.randint(5, 10)) # تأخير لتجنب الحظر
            
            content = await page.content()
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            
            for e in emails:
                e_low = e.lower()
                if not any(x in e_low for x in ['google', 'w3.org', 'schema', 'sentry', 'facebook', 'twitter', 'png', 'jpg']):
                    found_emails.add(e_low)
        except:
            continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print("🚀 انطلاق البوت اللانهائي - نسخة 2026")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. جلب الإيميلات الجديدة من الإنترنت
        discovered_emails = await get_fresh_emails(page)
        
        # 2. تحميل الذاكرة (الإيميلات التي تم التقديم عليها سابقاً)
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())
        else:
            applied_list = set()

        # 3. تصفية القائمة لإرسال الجديد فقط
        to_apply = [e for e in discovered_emails if e not in applied_list]
        
        print(f"🎯 وجدنا {len(discovered_emails)} إيميل إجمالي.")
        print(f"🆕 سيتم التقديم على {len(to_apply)} جهة جديدة الآن.")

        success_count = 0
        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم التقديم بنجاح على: {email}")
                # حفظ الإيميل في الذاكرة لعدم تكرار الإرسال
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                # تأخير بين كل إرسال وإرسال لسلامة حسابك
                await asyncio.sleep(random.randint(15, 30))

        await browser.close()
        print(f"🏁 المهمة انتهت. إجمالي التقديمات الجديدة: {success_count}")

if __name__ == "__main__":
    asyncio.run(run_bot())
