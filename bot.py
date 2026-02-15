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
        # إضافة إعدادات إضافية لتجنب الكشف
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. تسجيل الدخول
        print("🔑 محاولة تسجيل الدخول إلى LinkedIn...")
        await page.goto('https://www.linkedin.com/login')
        await page.fill('#username', email)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        
        # انتظر شوي للتأكد من الدخول وتجاوز أي رسالة تنبيه
        await asyncio.sleep(10) 

        # 2. الكلمات المفتاحية الجديدة (وظائف مرموقة في الشرقية)
        # جربنا هنا Material Coordinator كبداية قوية
        print("🔎 البحث عن وظائف مرموقة (شركات المقاولات والنفط) في (الشرقية)...")
        
        # الرابط المطور للبحث في الشرقية عن مسميات قوية
        search_query = "Material Coordinator OR Document Controller OR Timekeeper OR Admin"
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location=Eastern%20Province%2C%20Saudi%20Arabia"
        
        await page.goto(search_url)
        await asyncio.sleep(7)

        # 3. فحص النتائج
        # نستخدم selector أدق للبحث عن بطاقات الوظائف
        jobs = await page.query_selector_all('.jobs-search-results-list__item')
        
        if jobs:
            print(f"✅ مبروك! وجدنا {len(jobs)} وظيفة تناسب تخصصات المقاولات والشركات!")
            # البوت هنا يشوف الوظائف، في التحديث الجاي بنخليه يضغط 'التقديم السهل'
        else:
            print("⚠️ لم يتم العثور على وظائف جديدة بهذه المسميات حالياً. جاري المراقبة...")

        await browser.close()
        print("🏁 انتهت المهمة بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
