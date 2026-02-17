import os
import smtplib
import ssl
import time
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات (تأكد من وجود API_KEY في سيكرتس GitHub) ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") 

def send_professional_job_mail():
    # 1. قائمة شركات "مضمونة" تستقبل إيميلات وتوظف ثانوي
    # تشمل شركات مقاولات أرامكو وسراكو والتميمي وغيرهم
    target_emails = [
        "recruitment@nesma.com",      # نسما للمقاولات
        "hr@sraco.com.sa",            # سراكو للتشغيل والصيانة
        "careers@alfanar.com",        # الفنار
        "jobs@zamilindustrial.com",   # الزامل
        "hr@tamimi-group.com",        # التميمي
        "recruitment@sendan.com.sa",  # سندان الدولية
        "jobs@catcon.com.sa",         # المقاولات العربية
        "cv@znth.com.sa",             # مجموعة زينيث
        "jobs@daralriyadh.com"        # دار الرياض
    ]

    # 2. البحث عن ملف السيفي (تأكد أن اسمه CV_Candidate.pdf)
    cv_file = "CV_Candidate.pdf"
    if not os.path.exists(cv_file):
        # إذا ما لقي الاسم بالضبط، يبحث عن أي ملف PDF آخر
        cv_file = next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

    if not cv_file:
        print("❌ خطأ: لم يتم العثور على ملف السيرة الذاتية PDF!")
        return

    print(f"📦 الملف المكتشف: {cv_file} | الحجم: {os.path.getsize(cv_file)/1024:.2f} KB")

    context = ssl.create_default_context()
    
    try:
        # الاتصال بالسيرفر مرة واحدة لإرسال الجميع (أسرع وأضمن)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            print("✅ تم تسجيل الدخول إلى Gmail بنجاح!")

            for target in target_emails:
                msg = MIMEMultipart()
                msg['From'] = f"متقدم لوظيفة <{MY_EMAIL}>"
                msg['To'] = target
                
                # عناوين متنوعة لجذب الانتباه
                subjects = [
                    "طلب توظيف (ثانوية عامة) - جاهز للمباشرة فوراً",
                    "متقدم لوظيفة ميدانية/فنية - شهادة ثانوي",
                    "Job Application - High School Graduate - Ready to Join"
                ]
                msg['Subject'] = random.choice(subjects)

                body = """السلام عليكم ورحمة الله وبركاته،

أرغب في التقديم على الفرص الوظيفية المتاحة لديكم والتي تتناسب مع مؤهلي (شهادة الثانوية العامة). لدي الرغبة الكاملة والالتزام للعمل الميداني والتعاون مع فريق العمل.

تجدون سيرتي الذاتية مرفقة (PDF). شاكر ومقدر لكم اهتمامكم وتعاونكم.

رقم التواصل: موجود داخل السيرة الذاتية."""
                
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                # إرفاق الملف
                with open(cv_file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {cv_file}")
                    msg.attach(part)

                server.send_message(msg)
                print(f"🚀 تم الإرسال بنجاح إلى: {target}")
                
                # انتظار عشوائي بين 10 إلى 20 ثانية عشان جيميل ما يحظر الإرسال
                time.sleep(random.randint(10, 20))

        print("✨ انتهت المهمة بنجاح! راجع مجلد 'المرسل' في إيميلك.")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء التشغيل: {str(e)}")

if __name__ == "__main__":
    send_professional_job_mail()
