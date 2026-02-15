import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_bot():
    email = os.environ.get('USER_EMAIL')
    password = os.environ.get('USER_PASSWORD')

    async with async_playwright() as p:
        print("🚀 انطلاق بوت الاكتساح الشامل - نسخة الثانوية")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("🔑 تسجيل دخول...")
        await page.goto('https://www.linkedin.com/login')
        await page.fill('#username', email)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        await asyncio.sleep(random.randint(10, 15))

        # البحث بكلمة ثانوي في كامل السعودية - تقديم سهل - آخر أسبوع لضمان أن الوظيفة نشطة
        search_query = 'ثانوي OR "High School" OR "الثانوية"'
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location=Saudi%20Arabia&f_AL=true&f_TPR=r604800"
        
        await page.goto(search_url)
        print("🔎 جاري مسح الوظائف في المملكة...")
        await asyncio.sleep(10)

        # تحميل الوظائف بسكرول ذكي
        for _ in range(5): 
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)

        job_cards = await page.query_selector_all('.job-card-container, .jobs-search-results-list__item')
        print(f"📦 رصد {len(job_cards)} وظيفة. بدأ التقديم...")

        applied_count = 0
        for job in job_cards[:50]: # حد أمان 50 وظيفة لكل جولة
            try:
                await job.click()
                await asyncio.sleep(random.randint(4, 7)) 
                
                apply_btn = await page.query_selector('button.jobs-apply-button')
                if apply_btn:
                    await apply_btn.click()
                    await asyncio.sleep(3)

                    for _ in range(6):
                        next_btn = await page.query_selector('button[aria-label*="Next"], button[aria-label*="Continue"], button[aria-label*="Review"], button[aria-label*="Submit"]')
                        if next_btn:
                            txt = await next_btn.inner_text()
                            await next_btn.click()
                            if "Submit" in txt or "إرسال" in txt:
                                applied_count += 1
                                print(f"✅ تم التقديم ({applied_count})")
                                break
                            await asyncio.sleep(random.randint(2, 4))
                        else:
                            break
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(random.randint(3, 6)) 
            except:
                continue

        await browser.close()
        print(f"🏁 الجولة انتهت. الإجمالي: {applied_count}")

if __name__ == "__main__":
    asyncio.run(run_bot())
