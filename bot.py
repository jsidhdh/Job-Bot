import asyncio
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from playwright.async_api import async_playwright

# --- إعدادات الإيميل والسيفي ---
EMAIL_USER = "oedn305@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") 
CV_PATH = "My_CV.pdf"

async def send_email_with_cv(target_email, job_title):
    """دالة لإرسال السيفي بمجرد العثور على إيميل في صفحة الوظيفة"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = f"تقديم على وظيفة {job_title} - ثانوي"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة لديكم لحملة الثانوية. شكراً لكم."
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
        print(f"📧 تم إرسال السيفي بنجاح إلى: {target_email}")
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

async def run_bot():
    async with async_playwright() as p:
        print("🚀 انطلاق (قناص الروابط والتقديم الآلي) - 2026")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        search_query = 'site:wadhefa.com OR site:ewadhif.com "ثانوي" "إيميل"'
        await page.goto(f'https://www.google.com/search?q={search_query}')
        await asyncio.sleep(5)

        # رصد الروابط
        links = await page.query_selector_all('h3')
        print(f"📦 تم رصد {len(links)} إعلان وظيفي.")

        for i, link in enumerate(links[:10]):
            try:
                await link.click()
                await asyncio.sleep(5)
                
                # استخراج الإيميلات من داخل صفحة الوظيفة
                content = await page.content()
                emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
                
                if emails:
                    print(f"🎯 وجدنا إيميل تقديم في الرابط {i+1}: {emails[0]}")
                    await send_email_with_cv(emails[0], "ثانوية عامة")
                
                await page.go_back()
                await asyncio.sleep(3)
            except:
                continue

        await browser.close()
        print("🏁 انتهت المهمة. البوت قدم لك على الوظائف المتاحة.")

if __name__ == "__main__":
    asyncio.run(run_bot())
