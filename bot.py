import asyncio
import os
from playwright.async_api import async_playwright

async def run_bot():
    async with async_playwright() as p:
        print("🚀 انطلاق (قناص الروابط المباشرة) - وظائف ثانوي السعودية")
        browser = await p.chromium.launch(headless=True)
        # استخدام هوية متصفح حقيقي 100%
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # كلمات البحث الأكثر انتشاراً لوظائف الثانوي
        search_query = 'site:wadhefa.com OR site:ewadhif.com "ثانوي"'
        
        print(f"🔎 جاري سحب أحدث الروابط لـ: {search_query}")
        # الذهاب لنتائج بحث قوقل العادية (أصعب في الحظر)
        await page.goto(f'https://www.google.com/search?q={search_query}')
        await asyncio.sleep(5)

        # رصد الروابط التي تظهر في نتائج البحث
        # في قوقل، روابط المواقع تكون داخل وسم h3
        links = await page.query_selector_all('h3')
        print(f"📦 تم رصد {len(links)} رابط موقع توظيف.")

        active_links = 0
        for i, link in enumerate(links[:10]): # نفتح أول 10 نتائج
            try:
                # الضغط على الرابط لفتحه
                await link.click()
                await asyncio.sleep(5)
                
                print(f"✅ دخلنا الرابط رقم {i+1}: {page.url[:50]}...")
                
                # حركة (Scroll) لإنعاش الصفحة وتنشيط الرابط
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(3)
                
                active_links += 1
                # العودة لنتائج البحث لفتح الرابط التالي
                await page.go_back()
                await asyncio.sleep(3)
                
            except:
                continue

        await browser.close()
        print(f"🏁 المهمة انتهت. تم تنشيط {active_links} موقع توظيف بنجاح!")

if __name__ == "__main__":
    asyncio.run(run_bot())
