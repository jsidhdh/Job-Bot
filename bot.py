import asyncio
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from playwright.async_api import async_playwright

EMAIL_USER = "oedn305@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") 
CV_PATH = "My_CV.pdf"

async def send_email_with_cv(target_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = "طلب توظيف (ثانوية عامة) - 2026"
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف الشاغرة لديكم. شكراً لكم."
        msg.attach(MIMEText(body, 'plain'))

        with open(CV_PATH, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={CV_PATH}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

async def run_bot():
    async with async_playwright() as p:
        print("🔍 بدء البحث المتقدم عن إيميلات التوظيف...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # البحث في قوقل عن نصوص تحتوي على إيميلات توظيف مباشرة للسعودية
        search_url = 'https://www.google.com/search?q=site:twitter.com "ثانوي" "gmail.com" "السعودية" "وظائف"'
        
        try:
            await page.goto(search_url, timeout=60000)
            await asyncio.sleep(7) # انتظار إضافي لتحميل النتائج

            # سحب كل النص الموجود في الصفحة للبحث عن إيميلات
            content = await page.content()
            # استخراج الإيميلات (البحث عن نمط الإيميل المعتاد)
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            
            # تنظيف القائمة من الإيميلات غير المفيدة
            clean_emails = set()
            for e in emails:
                if not any(x in e.lower() for x in ['google', 'w3.org', 'png', 'jpg', 'git']):
                    clean_emails.add(e)

            print(f"🎯 تم العثور على {len(clean_emails)} إيميل.")

            count = 0
            for target in clean_emails:
                if await send_email_with_cv(target):
                    print(f"✅ تم الإرسال إلى: {target}")
                    count += 1
            
            print(f"🏁 المهمة انتهت. تم التقديم بنجاح على {count} جهة.")

        except Exception as e:
            print(f"❌ حدث خطأ: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())
