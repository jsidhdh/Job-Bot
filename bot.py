import os
import random
import smtplib
import asyncio
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات (تأكد من وضع API_KEY في سيكرتس GitHub) ---
SENDER_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") 
DB_FILE = "applied_emails.txt"

def get_cv_file():
    """البحث عن ملف السيرة الذاتية PDF"""
    files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    return files[0] if files else None

def send_professional_email(target_email):
    """إرسال إيميل موثق بنظام التشفير العالي لضمان الوصول"""
    context = ssl.create_default_context()
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Job Applicant <{SENDER_EMAIL}>"
        msg['To'] = target_email
        
        # عناوين متنوعة لجذب انتباه الـ HR وتجنب السبام
        subjects = [
            f"طلب توظيف (ثانوية عامة) - جاهز للمباشرة - كود {random.randint(100,999)}",
            f"متقدم لوظيفة تشغيلية/ميدانية - شهادة ثانوي - Ref:{random.randint(1000,5000)}",
            f"High School Graduate Seeking Job Opportunity - ID:{random.randint(10,99)}"
        ]
        msg['Subject'] = random.choice(subjects)
        
        body = f"""السلام عليكم ورحمة الله وبركاته،

أرغب في التقديم على الفرص الوظيفية المتاحة لديكم والتي تتناسب مع مؤهلي (شهادة الثانوية العامة). لدي الرغبة والالتزام التام للعمل الميداني والتعاون مع فريق العمل.

تجدون سيرتي الذاتية مرفقة (PDF). شاكر ومقدر لكم اهتمامكم.

رقم التواصل المرجعي: {random.randint(10000, 99999)}"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # إرفاق الملف
        cv_path = get_cv_file()
        if cv_path:
            with open(cv_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= CV_Candidate.pdf")
                msg.attach(part)

        # الإرسال عبر المنفذ الآمن 465 (أكثر ضماناً من 587)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, target_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ فشل الإرسال لـ {target_email}: {str(e)}")
        return False

def get_verified_energy_emails():
    """إيميلات شركات طاقة وإنشاءات في السعودية نشطة وتستقبل طلبات"""
    return [
        "recruitment@nesma.com",      # نسما (مقاول أرامكو ونيوم)
        "hr@sraco.com.sa",            # سراكو (التشغيل والصيانة)
        "careers@alfanar.com",        # الفنار للطاقة
        "jobs@zamilindustrial.com",   # الزامل
        "recruitment@alkhorayef.com", # الخريف للبترول
        "hr@tamimi-group.com",        # التميمي
        "careers@haka.com.sa",        # مجموعة الحكا
        "jobs@daralriyadh.com",       # دار الرياض
        "hr@isacc.com.sa",            # ايسك للمقاولات
        "recruitment@sendan.com.sa",  # سندان الدولية
        "jobs@catcon.com.sa"          # المقاولات العربية
    ]

async def run_bot():
    cv = get_cv_file()
    if not cv:
        print("❌ لم يتم العثور على ملف PDF!") ; return
    if not EMAIL_PASSWORD:
        print("❌ لم يتم العثور على الـ API_KEY!") ; return

    print(f"🚀 تشغيل البوت المطور... السيرة المستخدمة: {cv}")
    
    applied = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: applied = f.read().splitlines()

    targets = get_verified_energy_emails()
    count = 0
    
    for target in targets:
        if target not in applied:
            # انتظار بشري (بين 45 و 90 ثانية) هذا هو السر في عدم الحظر
            wait_time = random.randint(45, 90)
            print(f"📧 جاري الإرسال إلى {target}... (انتظار {wait_time}ث)")
            
            if send_professional_email(target):
                print(f"✅ تم بنجاح!")
                with open(DB_FILE, 'a') as f: f.write(target + "\n")
                count += 1
                await asyncio.sleep(wait_time)
            
            if count >= 8: # إرسال 8 فقط في المرة الواحدة لضمان وصولها للـ Inbox
                print("✋ تم الوصول للحد الآمن.")
                break

if __name__ == "__main__":
    asyncio.run(run_bot())
