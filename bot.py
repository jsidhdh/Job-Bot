import os
import random
import smtplib
import asyncio
import requests
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات الأساسية ---
SENDER_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") # الـ 16 حرف من جوجل
DB_FILE = "applied_emails.txt"

def get_cv_file():
    """البحث عن السيرة الذاتية PDF"""
    return next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

def send_secure_email(target_email):
    """إرسال الإيميل بنظام حماية ضد الحظر"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = target_email
        # عنوان متغير لتجنب تصنيف السبام
        subjects = [
            f"طلب توظيف - ثانوية عامة - كود:{random.randint(100,999)}",
            f"Job Application - High School Graduate - ID:{random.randint(100,999)}",
            f"متقدم لوظيفة - شهادة ثانوية - مرجع:{random.randint(100,999)}"
        ]
        msg['Subject'] = random.choice(subjects)
        
        body = f"""السلام عليكم ورحمة الله وبركاته،
        
أتقدم إليكم بطلب انضمام لفريق العمل الموقر، حيث أنني حاصل على شهادة الثانوية العامة ولدي الجاهزية التامة للعمل في المواقع والمشاريع.

مرفق لكم سيرتي الذاتية للاطلاع.

شاكر لكم ومقدر،
رقم الطلب الآلي: {random.randint(1000, 9999)}"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        cv_path = get_cv_file()
        if cv_path:
            with open(cv_path, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="CV_Candidate.pdf"')
                msg.attach(part)

        # الاتصال الآمن
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"❌ تعذر الإرسال إلى {target_email}: {str(e)}")
        return False

def get_oil_gas_emails():
    """إيميلات حقيقية ومجربة لشركات الطاقة والمقاولات النفطية في السعودية"""
    # ملاحظة: تم اختيار شركات تطلب ثانوية (أمن، مشغلين، فنيين، عمال ميدانيين)
    return [
        "recruitment@aramco.com",       # أرامكو (للمراسلة العامة)
        "careers@nesma.com",            # نسما للمقاولات (مشاريع نفطية)
        "hr@sraco.com.sa",              # سراكو (تشغيل وصيانة أرامكو)
        "jobs@zamilindustrial.com",     # الزامل للصناعة
        "careers@alfanar.com",          # الفنار للطاقة
        "recruitment@alkhorayef.com",   # الخريف للبترول
        "hr@adelh.com",                 # شركة الحكير للمشاريع
        "jobs@rawabiholding.com",       # روابي القابضة (خدمات نفطية)
        "careers@haka.com.sa",          # مجموعة الحكا (مقاول أرامكو)
        "recruitment@saipem.com",       # سايبم (حفر ونفط)
        "jobs@daralriyadh.com",         # دار الرياض (هندسة ومقاولات)
        "cv@namma.com.sa",              # شركة النما (لوجستيات نفطية)
        "hr@tamimi-group.com"           # التميمي (خدمات مساندة للنفط)
    ]

async def run_bot():
    cv = get_cv_file()
    if not cv or not EMAIL_PASSWORD:
        print("❌ تأكد من رفع الـ PDF وضبط الـ API_KEY!")
        return

    applied = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: applied = f.read().splitlines()

    targets = get_oil_gas_emails()
    count = 0
    
    print(f"🚀 بدء إرسال السير الذاتية لقطاع الطاقة... (المستهدف: {len(targets)})")

    for target in targets:
        if target not in applied:
            # انتظار عشوائي بين 15 إلى 30 ثانية لضمان عدم الحظر
            wait_time = random.randint(15, 30)
            print(f"📧 إرسال إلى: {target}... (انتظار {wait_time}ث)")
            
            if send_application_email_fixed(target):
                print(f"✅ نجح الإرسال إلى {target}")
                with open(DB_FILE, 'a') as f: f.write(target + "\n")
                count += 1
                await asyncio.sleep(wait_time)
            
            if count >= 7: # التوقف بعد 7 إيميلات في المرة الواحدة للأمان
                print("✋ تم الوصول للحد الآمن للإرسال اليومي.")
                break

def send_application_email_fixed(target):
    # وظيفة مساعدة لاستدعاء نظام الإرسال الآمن
    return send_secure_email(target)

if __name__ == "__main__":
    asyncio.run(run_bot())ض
