import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_bot():
    async with async_playwright() as p:
        print("🚀 انطلاق بوت (قناص وظائف قوقل) - نسخة الثانوية العامة السعودية")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. الذهاب لقوقل والبحث عن وظائف
        # كلمات البحث: وظائف ثانوي، وظائف الثانوية، وظائف ثانوي في السعودية
        search_query = "وظائف ثانوي السعودية 2026"
        print(f"🔎 جاري البحث في قوقل عن: {search_query}")
        
        await page.goto(f'https://www.google.com/search?q={search_query}&ibp=htl;jobs')
        await asyncio.sleep(7)

        # 2. رصد روابط الوظائف
        # في قوقل للوظائف، النتائج تظهر في قائمة
        job_listings = await page.query_selector_all('[role="listitem"]')
        print(f"📦 تم العثور على {len(job_listings)} وظيفة في قوقل.")

        applied_count = 0
        for i, job in enumerate(job_listings[:15]): # نفتح أول 15 وظيفة
            try:
                await job.click()
                await asyncio.sleep(3)
                
                # البحث عن زر التقديم (عادة يكون رابط لموقع التوظيف الأصلي)
                # قوقل يعطيك زر "Apply on [Site Name]"
                apply_links = await page.query_selector_all('a[aria-label*="التقديم"], a[aria-label*="Apply"]')
                
                if apply_links:
                    print(f"🎯 جاري فتح رابط الوظيفة رقم {i+1}...")
                    # ميزة: الدخول على الرابط لإنعاشه وتنشيطه
                    url = await apply_links[0].get_attribute('href')
                    
                    # نفتح صفحة جديدة لكل وظيفة عشان ما نضيع البحث الأصلي
                    new_page = await context.new_page()
                    await new_page.goto(url, timeout=60000)
                    print(f"🔗 دخلنا على موقع التوظيف: {new_page.url}")
                    
                    # هنا البوت يسوي "تنشيط" للرابط (Refresh/Scroll)
                    await new_page.mouse.wheel(0, 500)
                    await asyncio.sleep(5)
                    
                    applied_count += 1
                    await new_page.close()
                    print(f"✅ تم إنعاش وتنشيط الوظيفة بنجاح.")
                
                await asyncio.sleep(random.randint(2, 5))
            except Exception as e:
                print(f"⚠️ تخطي وظيفة بسبب: {e}")
                continue

        await browser.close()
        print(f"🏁 المهمة انتهت. تم الدفع بـ {applied_count} رابط وظيفة للتنشيط!")

if __name__ == "__main__":
    asyncio.run(run_bot())
