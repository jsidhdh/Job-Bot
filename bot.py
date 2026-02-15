import asyncio
import os
from playwright.async_api import async_playwright

async def run_bot():
    email = os.environ.get('USER_EMAIL')
    password = os.environ.get('USER_PASSWORD')

    if not email or not password:
        print("❌ خطأ: لم يتم العثور على الإيميل أو الباسورد في الـ Secrets!")
        return

    async with async_playwright() as p:
        print("🚀 جاري تشغيل المتصفح (النسخة المرموقة)...")
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()

        # 1. تسجيل الدخول
        print("🔑 محاولة تسجيل الدخول...")
        await page.goto('https://www.linkedin.com/login')
        await page.fill('#username', email)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        await asyncio.sleep(10) 

        # 2. البحث عن وظائف شركات المقاولات والنفط (المسميات القوية)
        print("🔎 البحث عن وظائف مرموقة (Material/Document Controller/Timekeeper) في الشرقية...")
        
        # كلمات البحث الجديدة
        search_query = "Material Coordinator OR Document Controller OR Timekeeper"
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location=Eastern%20Province%2C%20Saudi%20Arabia"
        
        await page.goto(search_url)
        await asyncio.sleep(7)

        # 3. فحص النتائج
        jobs = await page.query_selector_all('.jobs-search-results-list__item')
        
        if jobs:
            print(f"✅ كفو! وجدنا {len(jobs)} وظائف مرموقة جديدة بالشرقية!")
        else:
            print("⚠️ لا توجد وظائف جديدة بهذه المسميات حالياً. جاري المراقبة...")

        await browser.close()
        print("🏁 انتهت المهمة بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
