import asyncio
import os
import re
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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
    clean_email = "".join(c for c in target_email if ord(c) < 128).strip()
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = clean_email
        msg['Subject'] = f"Request for Job Opportunity - {random.randint(100, 999)}"
        
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة بمؤهل ثانوي. شكراً لكم."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if CV_PATH and os.path.exists(CV_PATH):
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="CV.pdf"') 
                msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ خطأ في الإرسال لـ {target_email}: {e}")
        return False

def generate_smart_emails():
    domains = ['gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'moe.gov.sa', 'aramco.com', 'stc.com.sa', 'saudia.com', 'sabic.com', 'almarai.com', 'panda.com.sa', 'jarir.com']
    prefixes = ['hr', 'jobs', 'careers', 'recruitment', 'cv', 'employment']
    generated = [f"{p}@{d}" for d in domains for p in prefixes]
    extra = ['recruitment@mcs.gov.sa', 'jobs@neom.com', 'careers@redseaglobal.com']
    return list(set(generated + extra))

async def run_bot():
    print(f"📁 السيفي المكتشف: {CV_PATH}")
    if not CV_PATH:
        print("⚠️ تنبيه: لم يتم العثور على ملف PDF في المجلد!")
        return

    target_emails = generate_smart_emails()
    
    applied_list = set()
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            applied_list = set(f.read().splitlines())

    to_apply = [e for e in target_emails if e not in applied_list]
    print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف.")

    success_count = 0
    for email in to_apply:
        if await send_email_with_cv(email):
            print(f"✅ تم الإرسال بنجاح إلى: {email}")
            with open(DATABASE_FILE, "a") as f:
                f.write(email + "\n")
            success_count += 1
            await asyncio.sleep(12) 
            if success_count >= 10: break 

    print(f"🏁 التقرير النهائي: تم إرسال {success_count} سيرة ذاتية بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
