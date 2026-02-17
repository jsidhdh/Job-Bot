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

def send_to_active_only():
    # قائمة الإيميلات (المفحوصة والنشطة حالياً)
    # ملاحظة: تم حذف znth و tamimi و catcon لأن نطاقاتها معطلة
    active_targets = [
        "hr@sraco.com.sa",           # سراكو (شغال 100%)
        "careers@alfanar.com",       # الفنار (شغال 100%)
        "talent@zamilindustrial.com",# الزامل (شغال 100%)
        "jobs@sa.g4s.com",           # شركة المجال/G4S (شغال 100%)
        "recruitment@sendan.com.sa", # سندان الدولية (شغال 100%)
        "jobs@emdad-it.com"          # إمداد الخبرات (شغال 100%)
    ]

    cv_file = next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)
    if not cv_file:
        print("❌ لم يتم العثور على ملف السيفي PDF")
        return

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            print("🚀 البوت بدأ الإرسال للأهداف النشطة فقط...")

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
                print(f"✅ تم الإرسال بنجاح إلى: {target}")
                time.sleep(12) # وقت انتظار لتجنب السبام

        print("✨ تم الانتهاء! كل الشركات أعلاه استلمت طلبك الآن.")

    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    send_to_active_only()
