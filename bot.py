import os
import random
import smtplib
import asyncio
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from bs4 import BeautifulSoup

# --- الإعدادات (تأكد من وجود السيكرت باسم API_KEY في قيت هب) ---
SENDER_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") 
DB_FILE = "applied_emails.txt"

def get_cv_file():
    """البحث عن ملف السيرة الذاتية PDF في المجلد"""
    return next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

def send_application_email(target_email):
    """إرسال الإيميل مع المرفق"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = target_email
        msg['Subject'] = f"Job Application - High School Graduate - Ref:{random.randint(1000, 9999)}"
        
        body = """Greetings,

I am writing to express my interest in potential job opportunities at your esteemed organization. 
I am a High School Graduate, highly motivated, and ready to contribute to your team.

Please find my CV attached for your review.

Best Regards,"""
        
        msg.attach(MIMEText(body, 'plain'))

        cv_path = get_cv_file()
        if cv_path:
            with open(cv_path, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="CV_Saudi_Candidate.pdf"')
                msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"❌ تعذر الإرسال إلى {target_email}: {str(e)}")
        return False

def get_real_emails():
    """قائمة إيميلات حقيقية ومحدثة لجهات تطلب ثانوي"""
    return [
        "recruitment@panda.com.sa",      # بنده
        "careers@jarir.com",             # جرير
        "jobs@almarai.com",              # المراعي
        "recruitment@nwc.com.sa",        # شركة المياه
        "hr@saudicatering.com",          # التموين
        "careers@nesma.com",             # نسما
        "jobs@kfb.com.sa",               # مخابز الفيصل
        "recruitment@alkhorayef.com",    # الخريف
        "jobs@daralarkan.com",           # دار الأركان
        "careers@alfanar.com",           # الفنار
        "jobs@shaker.com.sa",            # مجموعة شاكر
        "hr@sraco.com.sa",               # سراكو (صيانة وتشغيل)
        "jobs@zamilindustrial.com",      # الزامل
        "recruitment@fawazalhokair.com", # الحكير (تجزئة)
        "careers@appareluae.com",        # أباريل (ملابس وماركات)
        "jobs@binzagr.com.sa"            # بن زقر (توزيع)
    ]

def scrape_direct_links():
    """سحب أحدث روابط التوظيف المباشرة لحملة الثانوية"""
    print("\n🔎 جاري البحث عن روابط تقديم مباشرة (أحدث الوظائف)...")
    url = "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-لحملة-الثانوية"
    links = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if 'ثانوية' in a.text:
                full_url = a['href'] if a['href'].startswith('http') else f"https://saudi.tanqeeb.com{a['href']}"
                links.append(f"{a.text.strip()[:50]}... -> {full_url}")
                if len(links) >= 5: break
    except: pass
    return links

async def run_bot():
    cv = get_cv_file()
    if not cv:
        print("❌ خطأ: لم يتم العثور على ملف PDF (السيرة الذاتية)!")
        return
    if not EMAIL_PASSWORD:
        print("❌ خطأ: لم يتم العثور على الباسورد (API_KEY) في السيكرتس!")
        return

    print(f"🚀 بدء العمل... السيرة الذاتية المستخدمة: {cv}")
    
    # تحميل القائمة السوداء (الجهات التي تم مراسلتها سابقاً)
    applied = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: applied = f.read().splitlines()

    emails = get_real_emails()
    count = 0
    
    for target in emails:
        if target not in applied:
            print(f"📧 جاري الإرسال إلى: {target}...")
            if send_application_email(target):
                print(f"✅ نجح الإرسال!")
                with open(DB_FILE, 'a') as f: f.write(target + "\n")
                count += 1
                await asyncio.sleep(10) # فترات راحة لتجنب الحظر
            if count >= 10: break # إرسال 10 إيميلات في المرة الواحدة

    # جلب روابط التقديم اليدوي
    direct_links = scrape_direct_links()
    if direct_links:
        print("\n🔥 وظائف جديدة (قدم عليها يدوياً بالروابط):")
        for link in direct_links: print(f"👉 {link}")

if __name__ == "__main__":
    asyncio.run(run_bot())
