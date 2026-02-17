import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- الإعدادات ---
MY_EMAIL = "oedn305@gmail.com"
EMAIL_PASSWORD = os.getenv("API_KEY") # الـ 16 حرف حقت قوقل

def get_fresh_jobs():
    """سحب روابط الوظائف اللي نزلت اليوم وتطلب ثانوية"""
    print("🚀 جاري سحب أحدث وظائف الثانوية...")
    url = "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-لحملة-الثانوية"
    headers = {'User-Agent': 'Mozilla/5.0'}
    job_list = []
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # البحث عن الروابط
        for a in soup.find_all('a', href=True):
            title = a.text.strip()
            # تصفية الوظائف عشان نضمن إنها ثانوية
            if any(word in title for word in ["ثانوية", "ثانوي", "أمن", "مشغل", "فني"]):
                href = a['href']
                if not href.startswith('http'):
                    href = f"https://saudi.tanqeeb.com{href}"
                
                entry = f"📍 {title}\n🔗 {href}\n"
                if entry not in job_list:
                    job_list.append(entry)
            
            if len(job_list) >= 15: break # نكتفي بـ 15 رابط فرش
    except Exception as e:
        print(f"❌ خطأ في سحب الوظائف: {e}")
    
    return job_list

def send_links_to_my_email(jobs):
    """إرسال الروابط المجموعة إلى إيميلك الشخصي"""
    if not jobs:
        print("📭 ما لقيت وظائف جديدة حالياً.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = MY_EMAIL
        msg['To'] = MY_EMAIL
        msg['Subject'] = f"🔥 روابط وظائف ثانوية جديدة - بتاريخ اليوم"

        body = "يا بطل، هذي أحدث روابط التوظيف (ثانوية عامة) اللي نزلت اليوم:\n\n"
        body += "\n".join(jobs)
        body += "\n\nبالتوفيق، قدم عليها بسرعة قبل تقفل!"

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ تم إرسال قائمة الروابط إلى إيميلك بنجاح!")
    except Exception as e:
        print(f"❌ فشل إرسال الإيميل: {e}")

if __name__ == "__main__":
    links = get_fresh_jobs()
    send_links_to_my_email(links)
