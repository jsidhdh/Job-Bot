import asyncio
import os
from playwright.async_api import async_playwright

async def run_bot():
    # سحب البيانات من الـ Secrets اللي أنت حطيتها في الإعدادات
    email = os.environ.get('USER_EMAIL')
    password = os.environ.get('USER_PASSWORD')

    if not email or not password:
        print("❌ خطأ: لم يتم العثور على الإيميل أو الباسورد في الـ Secrets!")
        return

    async with async_playwright() as p:
        print("🚀 جاري تشغيل المتصفح...")
        browser = await p.chromium.launch(headless=True) # تشغيل مخفي
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()

        # 1. تسجيل الدخول
        print("🔑 محاولة تسجيل الدخول إلى LinkedIn...")
        await page.goto('https://www.linkedin.com/login')
        await page.fill('#username', email)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        
        # ننتظر شوي للتأكد من الدخول
        await asyncio.sleep(7) 

        # 2. البحث عن وظائف ثانوي في الشرقية
        print("🔎 البحث عن وظائف (ثانوي) في (الشرقية)...")
        search_url = "https://www.linkedin.com/jobs/search/?keywords=ثانوي&location=Eastern%20Province"
        await page.goto(search_url)
        await asyncio.sleep(5)

        # 3. فحص النتائج
        jobs = await page.query_selector_all('.job-card-container')
        if jobs:
            print(f"✅ وجدنا {len(jobs)} وظائف محتملة!")
            # هنا نقدر نضيف كود الضغط على التقديم السهل
        else:
            print("⚠️ لم يتم العثور على وظائف جديدة حالياً.")

        await browser.close()
        print("🏁 انتهت المهمة بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
