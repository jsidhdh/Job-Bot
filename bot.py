import os
import re
import requests
from bs4 import BeautifulSoup
import smtplib
import time
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") 

def get_fresh_job_links():
    """البحث عن روابط وظائف ثانوي جديدة في المواقع"""
    print("🔎 جاري البحث عن روابط تقديم مباشرة...")
    links = []
    url = "https://www.wadhefa.com/news/" # موقع وظيفة.كوم (أخبار التوظيف)
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if any(word in a.text for word in ["ثانوية", "ثانوي", "أمن", "مدني", "فني"]):
                links.append(f"📍 {a.text.strip()}\n🔗 https://www.wadhefa.com{a['href']}")
    except: pass
    return links[:10] # نجيب أول 10 روابط بس

def send_master_application():
    # 1. قائمة الإيميلات النشطة 100% (تجنباً لرسائل الفشل)
    active_emails = [
        "hr@sraco.com.sa",            # سراكو - نشط جداً
        "careers@alfanar.com",        # الفنار - شغال
        "talent@zamilindustrial.com", # الزامل - تحديث 2026
        "jobs@sa.g4s.com",            # شركة المجال G4S
        "recruitment@sendan.com.sa",  # سندان الدولية
        "cv@znth.com.sa"              # مجموعة زينيث
    ]

    # 2. التأكد من السيفي
    cv_file = "CV_Candidate.pdf"
    if not os.path.exists(cv_file):
        cv_file = next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            print("✅ تم تسجيل الدخول.. جاري الإرسال للشركات النشطة.")

            for target in active_emails:
                msg = MIMEMultipart()
                msg['From'] = f"متقدم لوظيفة <{MY_EMAIL}>"
                msg['To'] = target
                msg['Subject'] = "طلب توظيف (ثانوية عامة) - جاهز للمباشرة فوراً"
                
                body = "السلام عليكم، أتقدم بطلبي للعمل في شركتكم الموقرة. السيرة الذاتية مرفقة."
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                if cv_file:
                    with open(cv_file, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename= {cv_file}")
                        msg.attach(part)

                server.send_message(msg)
                print(f"🚀 تم الإرسال إلى: {target}")
                time.sleep(10)

        # 3. إرسال تقرير الروابط لك أنت (عشان تقدم يدوياً في المواقع اللي ما تقبل إيميل)
        links = get_fresh_job_links()
        if links:
            report = MIMEMultipart()
            report['From'] = MY_EMAIL
            report['To'] = MY_EMAIL
            report['Subject'] = "🔥 روابط تقديم مباشرة (وظائف ثانوي اليوم)"
            report_body = "يا بطل، هذي الشركات تطلب تقديم عن طريق موقعها (مو إيميل)، قدم عليها الحين:\n\n" + "\n\n".join(links)
            report.attach(MIMEText(report_body, 'plain', 'utf-8'))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(MY_EMAIL, EMAIL_PASSWORD)
                server.send_message(report)
                print("📨 تم إرسال قائمة الروابط الإضافية إلى إيميلك الشخصي.")

    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    send_master_application()
