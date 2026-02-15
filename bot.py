import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_bot():
    email = os.environ.get('USER_EMAIL')
    password = os.environ.get('USER_PASSWORD')

    async with async_playwright() as p:
        print("🚀 انطلاق نسخة (التسلل الهادئ) - اكتساح السعودية")
        # تشغيل المتصفح بمواصفات تخفي عالية
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edge/121.0.0.0",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        # 1. الدخول لصفحة تسجيل الدخول مباشرة
        print("🔑 جاري تسجيل الدخول...")
        try:
            await page.goto('https://www.linkedin.com/login', wait_until="networkidle")
            await page.type('#username', email, delay=100) # محاكاة كتابة بشرية
            await page.type('#password', password, delay=100)
            await page.click('button[type="submit"]')
            
            print("⏳ انتظار المصادقة.. وافق من جوالك الآن (معك 40 ثانية)!")
            await asyncio.sleep(40) 

            # 2. البحث عن وظائف الثانوي في السعودية برابط جديد ومبسط
            # استخدمنا كلمات بحث (ثانوي، الثانوية، High School) لضمان النتائج
            search_url = "https://www.linkedin.com/jobs/search/?f_AL=true&keywords=%D8%AB%D8%A7%D9%86%D9%88%D9%8A%20OR%20High%20School&location=Saudi%20Arabia&refresh=true"
            
            print("🔎 جاري البحث عن وظائف الثانوي...")
            await page.goto(search_url, wait_until="networkidle")
            await asyncio.sleep(15)

            # رصد الوظائف بطريقة "صياد الفرص"
            job_cards = await page.query_selector_all('.job-card-list__title, .job-card-container__link')
            
            if len(job_cards) == 0:
                print("⚠️ لم تظهر نتائج.. جاري محاولة أخيرة بفلتر مختلف...")
                await page.goto("https://www.linkedin.com/jobs/search/?f_AL=true&keywords=High%20School&location=Saudi%20Arabia")
                await asyncio.sleep(10)
                job_cards = await page.query_selector_all('.job-card-list__title')

            print(f"📦 تم رصد {len(job_cards)} وظيفة.")

            applied_count = 0
            for job in job_cards[:10]:
                try:
                    await job.click()
                    await asyncio.sleep(5)
                    
                    apply_btn = await page.query_selector('button.jobs-apply-button')
                    if apply_btn:
                        print("🎯 لقيت تقديم سهل! جاري التنفيذ...")
                        await apply_btn.click()
                        await asyncio.sleep(4)

                        # الضغط على أزرار التقديم حتى النهاية
                        for _ in range(5):
                            next_btn = await page.query_selector('button[aria-label*="Next"], button[aria-label*="Submit"], button[aria-label*="Review"]')
                            if next_btn:
                                await next_btn.click()
                                await asyncio.sleep(3)
                            else:
                                break
                        applied_count += 1
                        print(f"✅ تم التقديم بنجاح!")
                        await page.keyboard.press("Escape")
                except:
                    continue

            print(f"🏁 المهمة تمت. التقديمات: {applied_count}")
        except Exception as e:
            print(f"❌ خطأ تقني: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())
