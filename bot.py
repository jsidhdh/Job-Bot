import os
import re
import requests
from bs4 import BeautifulSoup
import smtplib
import time
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات (تأكد من وجود API_KEY في سيكرتس GitHub) ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY")
DB_FILE = "applied_emails.txt"

def get_cv_file():
    """البحث عن ملف السيرة الذاتية PDF في المجلد"""
    return next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

def send_cv_to_company(company_email):
    """إرسال السيرة الذاتية للشركة المكتشفة"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Job Applicant <{MY_EMAIL}>"
        msg['To'] = company_email
        
        # عناوين احترافية متغيرة لجذب الـ HR
        subjects = [
            f"تقديم على وظيفة (ثانوية عامة) - جاهز للمباشرة - كود {random.randint(100,999)}",
            f"طلب توظيف ميداني/تشغيل - شهادة ثانوي - Ref:{random.randint(1000,5000)}",
            f"High School Graduate - Seeking Job Opportunity - ID:{random.randint(10,99)}"
        ]
        msg['Subject'] = random.choice(subjects)
        
        body = """السلام عليكم ورحمة الله وبركاته،

أتقدم إليكم بطلبي هذا للالتحاق بفريق العمل لديكم، حيث أنني حاصل على شهادة الثانوية العامة ولدي الرغبة والالتزام التام للعمل.

تجدون سيرتي الذاتية مرفقة (PDF). شاكر ومقدر لكم اهتمامكم."""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        cv_path = get_cv_file()
        if cv_path:
            with open(cv_path, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="CV_Candidate.pdf"')
                msg.attach(part)

        # الإرسال الآمن SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except:
        return False

def auto_scout_and_apply():
    """البحث في المواقع وسحب الإيميلات والتقديم فوراً"""
    print("🚀 الروبوت يبحث الآن عن إيميلات شركات حقيقية في (تنقيب، وظيفة.كوم، ونيوم)...")
    
    # روابط بحث عن وظائف الثانوي في السعودية
    urls = [
        "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-لحملة-الثانوية",
        "https://www.wadhefa.com/news/",
        "https://www.ewdifh.com/jobs/1"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    all_found_emails = set()

    # 1. سحب الإيميلات من صفحات الوظائف
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            # استخراج الإيميلات باستخدام Regex (تعبير نمطي)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            for email in emails:
                # تصفية الإيميلات (نستبعد إيميلات المواقع نفسها)
                if not any(domain in email for domain in ["google", "tanqeeb", "wadhefa", "example", "sentry"]):
                    all_found_emails.add(email.lower())
        except:
            continue

    print(f"✅ تم اكتشاف {len(all_found_emails)} إيميل لشركات محتملة.")

    # 2. تحميل قائمة الإيميلات التي تم مراسلتها سابقاً
    applied = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: applied = f.read().splitlines()

    # 3. البدء في التقديم الآلي
    success_count = 0
    for email in all_found_emails:
        if email not in applied:
            print(f"📧 جاري التقديم الآلي على: {email}...")
            if send_cv_to_company(email):
                print(f"✅ تم الإرسال بنجاح!")
                with open(DB_FILE, 'a') as f: f.write(email + "\n")
                success_count += 1
                # انتظار عشوائي بين الإرساليات لتجنب الحظر
                time.sleep(random.randint(15, 30))
            
            if success_count >= 10: # إرسال 10 في كل مرة لتجنب حظر حسابك
                print("✋ تم بلوغ الحد الآمن للإرسال الآلي لهذه الدورة.")
                break

    if success_count == 0:
        print("📭 لم يتم العثور على إيميلات شركات جديدة في إعلانات اليوم.")

if __name__ == "__main__":
    auto_scout_and_apply()
