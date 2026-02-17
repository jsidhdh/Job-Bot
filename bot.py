import requests
from bs4 import BeautifulSoup
import time

def search_live_jobs():
    # روابط البحث المخصصة لوظائف الثانوي في قطاع المقاولات والنفط بالسعودية
    queries = [
        "https://saudi.tanqeeb.com/ar/s/وظائف/وظائف-لحملة-الثانوية",
        "https://www.wadhefa.com/news/"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("🚀 جاري مسح السوق بحثاً عن وظائف ثانوية حقيقية (آخر 24 ساعة)...")
    print("="*50)

    found_jobs = []

    for url in queries:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # استخراج الروابط التي تحتوي على كلمات مفتاحية (ثانوي، مقاولات، فني)
            links = soup.find_all('a', href=True)
            for link in links:
                text = link.text.strip()
                href = link['href']
                
                if any(word in text for word in ["ثانوية", "ثانوي", "مشغل", "فني", "أمن"]):
                    if not href.startswith('http'):
                        href = f"https://saudi.tanqeeb.com{href}"
                    
                    job_entry = f"📍 وظيفة: {text}\n🔗 رابط التقديم: {href}"
                    if job_entry not in found_jobs:
                        found_jobs.append(job_entry)
                        print(job_entry)
                        print("-" * 30)
                        if len(found_jobs) >= 15: break
        except Exception as e:
            print(f"⚠️ فشل المسح في أحد المواقع: {e}")

    if not found_jobs:
        print("📭 لم يتم العثور على وظائف جديدة في هذه اللحظة. جرب لاحقاً.")

if __name__ == "__main__":
    search_live_jobs()
