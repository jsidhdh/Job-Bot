import os, random, smtplib, asyncio, requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- الإعدادات (تأكد من اسم السيكرت في قيت هب API_KEY) ---
SENDER = "oedn305@gmail.com"
PASS = os.getenv("API_KEY") 
DB = "applied_emails.txt"

def get_cv():
    return next((f for f in os.listdir('.') if f.lower().endswith('.pdf')), None)

def send_cv(target):
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = SENDER, target
        msg['Subject'] = f"High School Graduate - Job Application {random.randint(100, 999)}"
        msg.attach(MIMEText("Greetings,\n\nPlease find my CV attached for job opportunities.\n\nRegards.", 'plain'))
        
        cv = get_cv()
        if cv:
            with open(cv, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="CV.pdf"')
                msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(SENDER, PASS)
            s.send_message(msg)
        return True
    except: return False

def find_jobs():
    print("🔎 جاري سحب روابط التقديم المباشرة (وظائف ثانوية)...")
    try:
        # البحث عن روابط ثانوية في أشهر المواقع
        r = requests.get("https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-لحملة-الثانوية", timeout=10)
        return [f"https://saudi.tanqeeb.com{l['href']}" for l in __import__('bs4').BeautifulSoup(r.text, 'html.parser').find_all('a', href=True) if 'ثانوية' in l.text][:5]
    except: return []

async def run():
    cv = get_cv()
    if not cv or not PASS:
        print(f"❌ خطأ: CV موجود: {bool(cv)} | الباسورد موجود: {bool(PASS)}")
        return

    # 1. إرسال إيميلات لشركات كبرى
    targets = [f"{p}@{d}" for d in ['aramco.com', 'stc.com.sa', 'sabic.com', 'neom.com', 'almarai.com', 'panda.com.sa'] for p in ['hr', 'jobs', 'careers']]
    applied = open(DB, 'r').read().splitlines() if os.path.exists(DB) else []
    
    count = 0
    for email in [e for e in targets if e not in applied]:
        if send_cv(email):
            print(f"✅ تم الإرسال إلى: {email}")
            with open(DB, 'a') as f: f.write(email + "\n")
            count += 1
            if count >= 10: break
            await asyncio.sleep(5)

    # 2. جلب روابط تقديم مباشرة
    links = find_jobs()
    if links:
        print("\n🔗 روابط تقديم مباشرة جديدة:")
        for l in links: print(f"👉 {l}")

if __name__ == "__main__":
    asyncio.run(run())
