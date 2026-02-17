import os
import smtplib
import ssl
import time
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") 

def send_to_active_companies():
    # 1. قائمة إيميلات "محدثة" (تم استبدال الإيميلات المعطلة)
    # هذه الشركات تعمل في المقاولات، التشغيل، والطاقة
    target_emails = [
        "hr@sraco.com.sa",           # سراكو (نشط جداً للثانوي)
        "careers@alfanar.com",       # الفنار
        "jobs@zamilindustrial.com",  # الزامل
        "hr@tamimi-group.com",       # التميمي
        "recruitment@sendan.com.sa", # سندان الدولية
        "cv@znth.com.sa",            # مجموعة زينيث
        "jobs@catcon.com.sa",        # المقاولات العربية
        "careers@rezayat.com",       # مجموعة رضايات (الخبر)
        "jobs@nasspa.com"            # شركة ناصر سعيد الهاجري
    ]

    # البحث عن ملف السيفي
    cv_file = "CV_Candidate.pdf"
    if not os.path.exists(cv_file):
        cv_file = next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

    if not cv_file:
        print("❌ لم يتم العثور على ملف السيرة الذاتية")
        return

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            print("✅ تم تسجيل الدخول بنجاح!")

            for target in target_emails:
                msg = MIMEMultipart()
                msg['From'] = f"متقدم لوظيفة <{MY_EMAIL}>"
                msg['To'] = target
                msg['Subject'] = "طلب توظيف (ثانوية عامة) - جاهز للمباشرة فوراً"

                body = "السلام عليكم، أتقدم بطلبي للعمل في شركتكم الموقرة (لحملة الثانوية). السيرة الذاتية مرفقة."
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                with open(cv_file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {cv_file}")
                    msg.attach(part)

                server.send_message(msg)
                print(f"🚀 تم الإرسال بنجاح إلى: {target}")
                time.sleep(random.randint(10, 15))

    except Exception as e:
        print(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    send_to_active_companies()
