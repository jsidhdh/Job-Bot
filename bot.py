import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_bot():
    email = os.environ.get('USER_EMAIL')
    password = os.environ.get('USER_PASSWORD')

    async with async_playwright() as p:
        print("🚀 تشغيل نسخة (الاكتساح الشامل) لآخر 3 شهور...")
        browser = await p.chromium.launch(headless=True)
        # ميزة: التخفي التام عشان ما ينكشف البوت
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. تسجيل الدخول
        await page.goto('https://www.linkedin.com/login')
        await page.fill('#username', email)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        await asyncio.sleep(7)

        # 2. فلتر الاكتساح: مسميات مرموقة + المنطقة الشرقية + آخر 3 شهور (7776000 ثانية)
        # أضفت كل المسميات اللي طلبناها
        search_query = "Material Coordinator OR Document Controller OR Timekeeper OR Admin OR Safety Officer OR Warehouse"
        # الرابط المطور للبحث الشامل (عادي + سهل)
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location=Eastern%20Province%2C%20Saudi%20Arabia&f_TPR=r7776000"
        
        print(f"🔎 جاري مسح كافة الوظائف منذ 3 شهور في المنطقة الشرقية...")
        await page.goto(search_url)
        await asyncio.sleep(5)

        # 3. استخراج قائمة الوظائف
        job_cards = await page.query_selector_all('.jobs-search-results-list__item')
        print(f"📦 تم العثور على {len(job_cards)} وظيفة محتملة. بدأ الهجوم...")

        applied_count = 0
        for job in job_cards[:25]: # زيادة الحد لـ 25 وظيفة في المرة الواحدة
            try:
                await job.click()
                await asyncio.sleep(3)
                
                # البحث عن زر التقديم (سواء كان Easy Apply أو Apply العادي)
                # ميزة: يدعم كل أنواع أزرار التقديم
                apply_button = await page.query_selector('button.jobs-apply-button, .jobs-apply-button--top-card button')
                
                if apply_button:
                    button_text = await apply_button.inner_text()
                    print(f"🎯 محاولة التقديم على: {button_text}")
                    await apply_button.click()
                    await asyncio.sleep(4)

                    # إذا كان تقديم سهل، سيحاول إكمال الخطوات
                    # ميزة: الضغط المتكرر على Next حتى النهاية
                    for _ in range(6):
                        next_btn = await page.query_selector('button[aria-label*="Next"], button[aria-label*="Continue"], button[aria-label*="Review"]')
                        if next_btn:
                            await next_btn.click()
                            await asyncio.sleep(2)
                        else:
                            break
                    
                    # ميزة: التأكد من إرفاق السيفي وإرسال الطلب النهائي
                    submit_btn = await page.query_selector('button[aria-label*="Submit"]')
                    if submit_btn:
                        await submit_btn.click()
                        applied_count += 1
                        print(f"✅ تم تقديم الطلب بنجاح! (العدد الحالي: {applied_count})")
                        await asyncio.sleep(2)
                        # إغلاق أي نافذة شكر تظهر
                        close_btn = await page.query_selector('button[aria-label="Dismiss"]')
                        if close_btn: await close_btn.click()
                
            except Exception as e:
                continue

        await browser.close()
        print(f"🏁 انتهت العملية. تم التقديم على {applied_count} وظيفة بنجاح.")

if __name__ == "__main__":
    asyncio.run(run_bot())
