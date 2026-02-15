import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_bot():
    email = os.environ.get('USER_EMAIL')
    password = os.environ.get('USER_PASSWORD')

    async with async_playwright() as p:
        # تشغيل المتصفح مع إعدادات تخليه يبان كأنه شخص حقيقي من الدمام
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        print("🔑 جاري اقتحام لينكد إن...")
        try:
            await page.goto('https://www.linkedin.com/login', timeout=60000)
            await page.fill('#username', email)
            await page.fill('#password', password)
            await page.click('button[type="submit"]')
            
            # انتظرنا 20 ثانية كاملة عشان لو فيه تعليق أو حماية تتجاوزها
            await asyncio.sleep(20) 

            # البحث عن كلمات قوية جداً ولها نتائج دايم في الشرقية
            # f_TPR=r7776000 (آخر 3 شهور) | f_AL=true (تقديم سهل فقط لضمان التنفيذ)
            search_url = "https://www.linkedin.com/jobs/search/?keywords=Admin%20OR%20Coordinator%20OR%20Storekeeper&location=Eastern%20Province%2C%20Saudi%20Arabia&f_AL=true&f_TPR=r7776000"
            
            print("🔎 جاري سحب الوظائف فعلياً من المنطقة الشرقية...")
            await page.goto(search_url, timeout=60000)
            await asyncio.sleep(10)

            # محاولة النزول لآخر الصفحة عشان نحمل كل الوظائف (Scroll)
            for _ in range(3):
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(2)

            # استهداف الروابط الفعلية للوظائف
            job_links = await page.query_selector_all('.job-card-container__link, .job-card-list__title')
            
            if not job_links:
                print("⚠️ الصفحة فاضية! جاري محاولة إعادة تحميل ذكية...")
                await page.reload()
                await asyncio.sleep(10)
                job_links = await page.query_selector_all('.job-card-container__link, .job-card-list__title')

            print(f"📦 تم صيد {len(job_links)} وظيفة جاهزة للتقديم!")

            applied_count = 0
            for link in job_links[:15]: # تقديم على 15 وظيفة في كل طلعة
                try:
                    await link.click()
                    await asyncio.sleep(5)

                    # البحث عن زر التقديم السهل بجميع مسمياته البرمجية
                    apply_btn = await page.query_selector('button.jobs-apply-button')
                    if apply_btn:
                        print(f"🎯 لقيت زر التقديم.. جاري الضغط!")
                        await apply_btn.click()
                        await asyncio.sleep(3)

                        # ميزة "اكتساح الفورم": يضغط Next لين يوصل لـ Submit
                        for _ in range(5):
                            next_btn = await page.query_selector('button[aria-label*="Next"], button[aria-label*="Continue"], button[aria-label*="Review"]')
                            if next_btn:
                                await next_btn.click()
                                await asyncio.sleep(2)
                            else:
                                break

                        submit_btn = await page.query_selector('button[aria-label*="Submit"]')
                        if submit_btn:
                            await submit_btn.click()
                            applied_count += 1
                            print(f"✅ مبروك! تم التقديم فعلياً (رقم {applied_count})")
                            await asyncio.sleep(2)
                            # إغلاق نافذة النجاح
                            await page.keyboard.press("Escape")
                except:
                    continue

        except Exception as e:
            print(f"❌ صار خطأ تقني: {e}")

        await browser.close()
        print(f"🏁 المهمة انتهت. إجمالي التقديمات الفعلية: {applied_count}")

if __name__ == "__main__":
    asyncio.run(run_bot())
