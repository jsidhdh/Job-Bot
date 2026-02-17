import os
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") 

def send_to_agencies():
    # قائمة مكاتب توظيف (Agencies) - هذه الإيميلات حية ولا تغلق
    # توظف لشركات المقاولات والطاقة والكهروميكانيك
    active_targets = [
        "hr@sraco.com.sa",            # سراكو (الأقوى للثانوي)
        "careers@alfanar.com",        # الفنار (مشاريع الطاقة)
        "jobs@sa.g4s.com",            # شركة المجال (أمن وتفتيش)
        "recruitment@sendan.com.sa",  # سندان الدولية (مقاولات نفط)
        "cv@iscc.com.sa",             # شركة نظم المقاولات (الخبر)
        "jobs@fawaz-alhokair.com"     # فواز الحكير (قطاع التجزئة والتشغيل)
    ]

    cv_file = next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)
    if not cv_file:
        print("❌ ارفع ملف السيرة الذاتية PDF أولاً")
        return

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            print("🚀 بدأ الهجوم على مكاتب التوظيف النشطة...")

            for target in active_targets:
                msg = MIMEMultipart()
                msg['From'] = f"Job Application <{MY_EMAIL}>"
                msg['To'] = target
                msg['Subject'] = "طلب توظيف (ثانوية عامة) - جاهز للمباشرة"

                body = "السلام عليكم، أتقدم بطلبي للعمل في شركتكم الموقرة. السيرة الذاتية مرفقة."
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                with open(cv_file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {cv_file}")
                    msg.attach(part)

                server.send_message(msg)
                print(f"✅ تم الإرسال بنجاح إلى المكتب: {target}")
                time.sleep(15)

        print("✨ المهمة تمت! هذه المكاتب هي بوابتك للشركات الكبرى.")

    except Exception as e:
        print(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    send_to_agencies()
