import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- الإعدادات ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") 

def get_fresh_jobs():
    """سحب روابط الوظائف من عدة مصادر وبكلمات بحث قوية"""
    print("🚀 جاري المسح الشامل للوظائف الجديدة...")
    
    # كلمات البحث اللي تهمك
    keywords = ["ثانوية", "ثانوي", "أمن", "مشغل", "فني", "تدريب", "ميداني"]
    
    # روابط بحث مباشرة في أشهر المواقع
    search_queries = [
        "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-لحملة-الثانوية",
        "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-حراسات-أمنية",
        "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-فنيين"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    job_list = []
    
    for url in search_queries:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                title = a.text.strip()
                # إذا العنوان فيه وحدة من الكلمات اللي نبيها
                if any(word in title for word in keywords):
                    href = a['href']
                    if not href.startswith('http'):
                        href = f"https://saudi.tanqeeb.com{href}"
                    
                    entry = f"📍 {title}\n🔗 {href}\n"
                    if entry not in job_list:
                        job_list.append(entry)
            
        except Exception as e:
            print(f"⚠️ فشل المسح في: {url}")
            
    return job_list

def send_links_to_my_email(jobs):
    if not jobs:
        print("📭 لم يتم العثور على روابط جديدة حالياً. جرب تشغيل البوت في وقت لاحق (مثلاً صباحاً).")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = MY_EMAIL
        msg['To'] = MY_EMAIL
        msg['Subject'] = f"🔥 {len(jobs)} رابط وظيفة ثانوية جديدة لليوم"

        body = f"يا وحش، الرادار لقى لك {len(jobs)} وظيفة تناسبك ونزلت مؤخراً:\n\n"
        body += "\n".join(jobs)
        body += "\n\nافتح الروابط وقدم سيرتك الذاتية فوراً. بالتوفيق!"

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ مبروك! أرسلت لك {len(jobs)} رابط على إيميلك الشخصي.")
    except Exception as e:
        print(f"❌ فشل إرسال الإيميل: {e}")

if __name__ == "__main__":
    links = get_fresh_jobs()
    send_links_to_my_email(links)
