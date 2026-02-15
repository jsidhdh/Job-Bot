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
    # تنظيف فائق للإيميل
    clean_email = "".join(c for c in target_email if ord(c) < 128).strip()
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"Job Application - High School Graduate - {random.randint(100, 999)}"
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة. شكراً لكم."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        if CV_PATH:
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="Resume.pdf"') 
                msg.attach(part)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

async def get_fresh_emails(page):
    # كلمات بحث "قناصة" لاصطياد إيميلات الشركات الحقيقية
    queries = [
        '"hr@" شركة السعودية gmail.com',
        '"jobs@" الدمام الخبر gmail.com',
        '"careers@" الرياض وظائف outlook.com',
        'site:sa.opensooq.com "إيميل" "توظيف"',
        '"لإرسال السيرة الذاتية" @gmail.com',
        'site:facebook.com "السعودية" "وظائف" "gmail.com"'
    ]
    found_emails = set()
    for query in queries:
        try:
            # البحث عبر DuckDuckGo (لأنه لا يحجب النتائج مثل قوقل)
            print(f"🔎 قنص داتا من: {query[:30]}")
            await page.goto(f'https://duckduckgo.com/html/?q={query}')
            await asyncio.sleep(5)
            content = await page.content()
            # استخراج أي إيميل يظهر في الصفحة
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)
            for e in emails:
                e_c = e.lower().strip()
                # السماح بكل الإيميلات باستثناء المعطوبة تقنياً
                if not e_c.startswith('22@') and not any(x in e_c for x in ['google', 'sentry', 'w3.org', 'example']):
                    found_emails.add(e_c)
        except: continue
    return list(found_emails)

async def run_bot():
    async with async_playwright() as p:
        print(f"📁 السيفي: {CV_PATH}")
        browser = await p.chromium.launch(headless=True)
        # تمويه المتصفح كأنه جهاز ماك
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        page = await context.new_page()
        
        discovered_emails = await get_fresh_emails(page)
        
        # أهم خطوة: تصفير الذاكرة (افعلها يدوياً في جيت هاب أيضاً)
        applied_list = set()
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                applied_list = set(f.read().splitlines())

        to_apply = [e for e in discovered_emails if e not in applied_list]
        print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف جديدة.")

        success_count = 0
        for email in to_apply:
            if await send_email_with_cv(email):
                print(f"✅ تم الإرسال: {email}")
                with open(DATABASE_FILE, "a") as f:
                    f.write(email + "\n")
                success_count += 1
                await asyncio.sleep(random.randint(5, 10))

        await browser.close()
        print(f"🏁 التقرير النهائي: تم إرسال {success_count} سيرة ذاتية.")

if __name__ == "__main__":
    asyncio.run(run_bot())
