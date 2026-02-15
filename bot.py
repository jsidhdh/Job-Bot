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
        msg['Subject'] = f"Request for Job - High School Graduate - {random.randint(100, 999)}"
        body = "السلام عليكم، أرفق لكم سيرتي الذاتية للتقديم على الوظائف المتاحة بمؤهل ثانوي. شكراً لكم."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        if CV_PATH:
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
    except: return False

def generate_smart_emails():
    """توليد إيميلات لشركات ومؤسسات توظيف حقيقية بناءً على النطاقات الشائعة"""
    domains = [
        'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com',
        'moe.gov.sa', 'aramco.com', 'stc.com.sa', 'saudia.com',
        'sabic.com', 'almarai.com', 'panda.com.sa', 'jarir.com'
    ]
    prefixes = ['hr', 'jobs', 'careers', 'recruitment', 'cv', 'employment', 'staff']
    
    generated = []
    # توليد مزيج من الإيميلات العامة والخاصة بالتوظيف
    for d in domains:
        for p in prefixes:
            generated.append(f"{p}@{d}")
    
    # إضافة إيميلات تم قنصها سابقاً لضمان عدم ضياع الفرص
    extra_targets = [
        'recruitment@mcs.gov.sa', 'jobs@neom.com', 'careers@redseaglobal.com',
        'hr@aramco.com', 'cv@alkhofash.com', 'jobs@saudiatransport.com'
    ]
    return list(set(generated + extra_targets))

async def run_bot():
    print(f"📁 السيفي: {CV_PATH}")
    print("🚀 تفعيل وضع 'توليد الأهداف الذكي' لكسر حاجز الصفر")
    
    # 1. توليد الأهداف بدلاً من انتظار محركات البحث
    target_emails = generate_smart_emails()
    
    # 2. فلترة الأهداف المكررة
    applied_list = set()
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            applied_list = set(f.read().splitlines())

    to_apply = [e for e in target_emails if e not in applied_list]
    
    print(f"🎯 المستهدف اليوم: {len(to_apply)} جهة توظيف حقيقية.")

    success_count = 0
    for email in to_apply:
        if await send_email_with_cv(email):
            print(f"✅ تم الإرسال: {email}")
            with open(DATABASE_FILE, "a") as f:
                f.write(email + "\n")
            success_count += 1
            # تأخير بسيط لتجنب حظر Gmail
            await asyncio.sleep(random.randint(10, 20))
            if success_count >= 15: # إرسال 15 سيفي في كل دفعة
                break

    print(f"🏁 التقرير النهائي: تم إرسال {success_count} سيرة ذاتية بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
