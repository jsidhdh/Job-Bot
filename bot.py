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

def clean_text(text):
    """تنظيف النص من أي رموز غير مرئية أو عربية تسبب فشل الإرسال"""
    if not text: return ""
    return "".join(c for c in text if ord(c) < 128).strip()

async def send_email_with_cv(target_email):
    # تنظيف الإيميل قسرياً من أي رموز ASCII معطوبة
    target_email = clean_text(target_email)
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = target_email
        msg['Subject'] = f"Job Application - High School - {random.randint(100, 999)}"
        
        # كتابة الرسالة بتنسيق يضمن عدم تداخل اللغات
        body = "Greetings,\n\nPlease find my CV attached for potential job opportunities (High School Graduate).\n\nRegards."
        msg.attach(MIMEText(body, 'plain'))

        if CV_PATH and os.path.exists(CV_PATH):
            with open(CV_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="CV.pdf"') 
                msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Error sending to {target_email}: {str(e)}")
        return False

def generate_smart_emails():
    # قائمة الإيميلات التي نجحت في الاختبار السابق
    domains = ['gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'moe.gov.sa', 'aramco.com', 'stc.com.sa', 'saudia.com', 'sabic.com', 'almarai.com', 'panda.com.sa', 'jarir.com']
    prefixes = ['hr', 'jobs', 'careers', 'recruitment', 'cv', 'employment']
    generated = [f"{p}@{d}" for d in domains for p in prefixes]
    extra = ['recruitment@mcs.gov.sa', 'jobs@neom.com', 'careers@redseaglobal.com']
    # تنظيف كل إيميل يتم توليده فوراً
    return list(set(clean_text(e) for e in generated + extra))

async def run_bot():
    print(f"📁 CV Found: {CV_PATH}")
    if not CV_PATH:
        print("⚠️ No PDF file found!")
        return

    target_emails = generate_smart_emails()
    
    applied_list = set()
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            applied_list = set(clean_text(line) for line in f.read().splitlines())

    to_apply = [e for e in target_emails if e and e not in applied_list]
    print(f"🎯 Targets today: {len(to_apply)}")

    success_count = 0
    for email in to_apply:
        if await send_email_with_cv(email):
            print(f"✅ Success: {email}")
            with open(DATABASE_FILE, "a") as f:
                f.write(email + "\n")
            success_count += 1
            await asyncio.sleep(10) # انتظار 10 ثواني بين كل إرسال
            if success_count >= 15: break 

    print(f"🏁 Final Report: Sent {success_count} emails successfully.")

if __name__ == "__main__":
    asyncio.run(run_bot())ص
