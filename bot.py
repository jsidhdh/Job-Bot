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

def send_to_active_hr():
    # قائمة الإيميلات "القناصة" - إيميلات حية لمكاتب توظيف نشطة
    active_targets = [
        "hr@sraco.com.sa",           # سراكو (رقم 1 في السعودية للثانوي)
        "recruitment@sendan.com.sa", # سندان الدولية (مقاولات صناعية)
        "jobs@emdad-it.com",         # إمداد الخبرات (توظيف حكومي وشبه حكومي)
        "cv@iscc.com.sa"             # شركة نظم المقاولات
    ]

    cv_file = next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)
    if not cv_file:
        print("❌ لم يتم العثور على ملف السيرة الذاتية PDF")
        return

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            print("🚀 البوت يرسل الآن للقائمة الموثوقة فقط...")

            for target in active_targets:
                msg = MIMEMultipart()
                msg['From'] = f"Job Application <{MY_EMAIL}>"
                msg['To'] = target
                msg['Subject'] = "متقدم لوظيفة (ثانوية عامة) - جاهز للمباشرة فوراً"

                body = "السلام عليكم، أتقدم بطلبي للعمل في شركتكم الموقرة (لحملة الثانوية). السيرة الذاتية مرفقة."
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                with open(cv_file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {cv_file}")
                    msg.attach(part)

                server.send_message(msg)
                print(f"✅ تم الإرسال بنجاح إلى: {target}")
                time.sleep(15)

        print("✨ تم الانتهاء. هذه القائمة هي الأكثر ضماناً حالياً.")

    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    send_to_active_hr()
