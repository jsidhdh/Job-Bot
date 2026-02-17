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

def auto_apply_now():
    # قائمة الإيميلات "الصحيحة" لشركات التوظيف المباشر للثانوي
    target_emails = [
        "hr@sraco.com.sa",           # سراكو (رقم 1 في توظيف الثانوي)
        "careers@alfanar.com",       # الفنار (مشاريع الكهرباء)
        "jobs@zamilindustrial.com",  # الزامل (صناعات ثقيلة)
        "recruitment@sendan.com.sa", # سندان الدولية (مقاولات نفط)
        "cv@znth.com.sa",            # مجموعة زينيث (حراسات وأمن)
        "jobs@catcon.com.sa",        # المقاولات العربية (مشاريع كبرى)
        "careers@rezayat.com"        # مجموعة رضايات
    ]

    cv_file = "CV_Candidate.pdf"
    if not os.path.exists(cv_file):
        cv_file = next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

    if not cv_file:
        print("❌ ارفع ملف السيرة الذاتية أولاً باسم CV_Candidate.pdf")
        return

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            print("✅ البوت متصل وجاهز للهجوم..")

            for target in target_emails:
                msg = MIMEMultipart()
                msg['From'] = f"Job Applicant <{MY_EMAIL}>"
                msg['To'] = target
                msg['Subject'] = "طلب توظيف (ثانوية عامة) - جاهز للمباشرة فوراً"

                body = "السلام عليكم، أتقدم بطلبي للعمل في شركتكم الموقرة (لحملة الثانوية العامة). السيرة الذاتية مرفقة."
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                with open(cv_file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {cv_file}")
                    msg.attach(part)

                server.send_message(msg)
                print(f"🚀 تم التقديم على شركة: {target}")
                time.sleep(15) # انتظار عشان ما يتقفل إيميلك

        print("✨ المهمة تمت! البوت قدم لك على أقوى الشركات المتوفرة.")

    except Exception as e:
        print(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    auto_apply_now()
