import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_bot():
    email = os.environ.get('USER_EMAIL')
    password = os.environ.get('USER_PASSWORD')

    async with async_playwright() as p:
        print("🚀 تشغيل نسخة كسر الجمود - الاكتساح الشامل")
        # تشغيل المتصفح مع إظهار الهوية كإنسان
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. تسجيل الدخول
        print("🔑 محاولة الدخول...")
        await page.goto('https://www.linkedin.com/login', wait_until="networkidle")
        await page.fill('#username', email)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        
        # انتظار طويل (30 ثانية) عشان لو طلع لك "تأكيد" في الجوال تلحق توافق
        print("⏳ انتظار المصادقة (شيك جوالك إذا جاء تنبيه)...")
        await asyncio.sleep(30) 

        # 2. رابط بحث مباشر وبسيط جداً (ثانوي - السعودية)
        search_url = "https://www.linkedin.com/jobs/search/?f_AL=true&keywords=%D8%AB%D8%A7%D9%86%D9%88%D9%8A&location=Saudi%20Arabia"
        
        print("🔎 جاري اقتحام صفحة الوظائف...")
        await page.goto(search_url, wait_until="networkidle")
        await asyncio.sleep(15)

        # محاولة عمل سكرول عشان تظهر الوظائف في القائمة اليمين
        await page.mouse.wheel(0, 1000)
        await asyncio.sleep(5)

        # 3. رصد الوظائف (استخدام أكثر من كود للرصد لضمان النتيجة)
        job_cards = await page.query_selector_all('.job-card-container, [data-job-id]')
        
        if len(job_cards) == 0:
            print("⚠️ لم تظهر نتائج. جاري أخذ لقطة للشاشة للتشخيص...")
            await page.screenshot(path="error.png") # بيحفظ صورة لو فشل عشان نعرف السبب
        
        print(f"📦 تم رصد {len(job_cards)} وظيفة.")

        applied_count = 0
        for job in job_cards[:10]:
            try:
                await job.click()
                await asyncio.sleep(5)
                
                # البحث عن زر التقديم السهل
                apply_btn = await page.query_selector('button.jobs-apply-button')
                if apply_btn:
                    print("🎯 لقيت زر التقديم! جاري التنفيذ...")
                    await apply_btn.click()
                    await asyncio.sleep(3)

                    # الضغط على Next/Submit
                    for _ in range(5):
                        btn = await page.query_selector('button[aria-label*="Next"], button[aria-label*="Submit"], button[aria-label*="Review"]')
                        if btn:
                            await btn.click()
                            await asyncio.sleep(2)
                        else:
                            break
                    applied_count += 1
                    print(f"✅ تم التقديم بنجاح!")
                    await page.keyboard.press("Escape")
            except:
                continue

        await browser.close()
        print(f"🏁 الجولة انتهت. الإجمالي الفعلي: {applied_count}")

if __name__ == "__main__":
    asyncio.run(run_bot())
