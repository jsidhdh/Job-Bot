import asyncio
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from playwright.async_api import async_playwright

# --- إعدادات الإيميل والسيفي (تأكد من ضبطها في GitHub Secrets) ---
EMAIL_USER = "oedn305@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") 
CV_PATH = "My_CV.pdf"

async def send_email_with_cv(target_email):
    """دالة لإرسال السيرة الذاتية للإيميلات المكتشفة"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = "تقديم على وظيفة (ثانوية عامة) - 2026"
        
        body = """السلام عليكم ورحمة الله وبركاته،
        
أرغب في التقديم على الوظائف المتاحة لديكم والمناسبة لمؤهلي (الثانوية العامة).
مرفق لكم السيرة الذاتية للاطلاع عليها. شاكر لكم ومقدر جهودكم.

مقدم الطلب: (عبر المساعد الآلي الذكي)"""

        msg.attach(MIMEText(body, 'plain'))

        if os.path.exists(CV_PATH):
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename={CV_PATH}")
                msg.attach(part)
        else:
            print(f"⚠️ تحذير: ملف {CV_PATH} غير موجود!")
            return False

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"✅ تم الإرسال بنجاح إلى: {target_email}")
        return True
    except Exception as e:
        print(f"❌ فشل الإرسال إلى {target_email}: {e}")
        return False

async def run_bot():
    async with async_playwright() as p:
        print("🚀 بدء البحث عن إيميلات التوظيف (وظائف ثانوي)...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # قائمة بالمواقع المستهدفة لسحب الإيميلات منها مباشرة
        target_sites = [
            'https://www.wadhefa.com/news/',
            'https://www.ewadhif.com/',
            'https://www.btalah.com.sa/'
        ]

        found_emails = set()

        for site in target_sites:
            try:
                print(f"🔗 فحص الموقع: {site}")
                await page.goto(site, timeout=60000)
                await asyncio.sleep(5)
                
                # استخراج كافة الإيميلات الموجودة في الصفحة
                content = await page.content()
                emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
                
                for email in emails:
                    # فلترة لتجنب الإيميلات التقنية غير المرغوب فيها
                    if not any(x in email.lower() for x in ['w3.org', 'example', 'sentry', 'schema']):
                        found_emails.add(email)
            except Exception as e:
                print(f"⚠️ تعذر فتح {site}: {e}")

        print(f"🎯 تم العثور على {len(found_emails)} إيميل فريد.")

        # التقديم على الإيميلات التي تم العثور عليها
        success_count = 0
        for target in found_emails:
            if await send_email_with_cv(target):
                success_count += 1
                await asyncio.sleep(3) # تأخير بسيط لتجنب السبام

        await browser.close()
        print(f"🏁 المهمة انتهت. تم التقديم بنجاح على ({success_count}) إيميل.")

if __name__ == "__main__":
    asyncio.run(run_bot())
