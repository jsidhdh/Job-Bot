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
CV_PATH = "My_CV.pdf"

# دالة لإرسال السيفي
async def send_email_with_cv(target_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = f"تقديم على وظيفة شاغرة (ثانوية عامة) - تحديث {random.randint(100, 999)}"
        
        body = "السلام عليكم، أتقدم بطلب توظيف لمؤهل الثانوية العامة. مرفق السيرة الذاتية. شكراً لكم."
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

# دالة البحث عن إيميلات جديدة "لانهائية"
async def get_fresh_emails(page):
    # كلمات بحث تتغير عشوائياً كل مرة يشتغل فيها البوت لضمان نتائج جديدة
    keywords = [
        'وظائف "الدمام" ثانوي إيميل',
        'تعلن شركة "الخبر" توظيف ثانوي إيميل',
        'hr email saudi "high school"',
        'إيميل التوظيف شركة "الظهران"',
        'وظائف حراس أمن إيميل السعودية'
    ]
    query = random.choice(keywords)
    print(f"🔎 جاري البحث عن: {query}")
    
    await page.goto(f'https://www.google.com/search?q={query}')
    await asyncio.sleep(5)
    
    content = await page.content()
    # استخراج الإيميلات من نتائج البحث
    found = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
    
    # تنظيف القائمة
    clean = {e for e in found if not any(x in e.lower() for x in ['google', 'w3.org', 'png', 'jpg'])}
    return list(clean)

async def run_bot():
    async with async_playwright() as p:
        print("🚀 انطلاق البوت اللانهائي...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1. التقديم على القائمة الثابتة (للتأكيد)
        fixed_emails = ["hr@tamimi-group.com", "jobs@kudu.com.sa", "recruitment@almarai.com"] # أضف ما تشاء
        
        # 2. البحث عن إيميلات جديدة
        new_emails = await get_fresh_emails(page)
        
        all_targets = list(set(fixed_emails + new_emails))
        print(f"🎯 سيتم التقديم على {len(all_targets)} جهة اليوم.")

        for email in all_targets:
            if await send_email_with_cv(email):
                print(f"✅ تم الإرسال إلى: {email}")
                await asyncio.sleep(random.randint(5, 15)) # تأخير عشوائي عشان ما ننكشف

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())
