import os
import asyncio  # <-- 1. เพิ่มเข้ามาเพื่อจัดการ Event Loop
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("TRUE_USER")
PASSWORD = os.getenv("TRUE_PASS")

LOGIN_URL = "https://gateway.truecorp.co.th/install/"
EXPORT_URL = "https://gateway.truecorp.co.th/install/exportTextSOUnInstall.do?action=load"

def download_report(download_folder="downloads"):
    # --- 2. ป้องกันปัญหา Event Loop ชนกันเมื่อรันใน Thread ---
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.set_event_loop(asyncio.new_event_loop())
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    # ----------------------------------------------------

    os.makedirs(download_folder, exist_ok=True)
    
    today = datetime.now()
    from_date = today.strftime("%d/%m/%Y")
    to_date = (today + timedelta(days=7)).strftime("%d/%m/%Y")

    print(f"ช่วงเวลาที่เลือก: From Date = {from_date} ถึง To Date = {to_date}")

    with sync_playwright() as p:
        print("กำลังเปิดเบราว์เซอร์...")
        launch_args = [
            "--disable-web-security",
            "--ignore-certificate-errors",
            "--no-sandbox",
            "--disable-setuid-sandbox"
        ]
        
        try:
            # บังคับใช้ headless=True สำหรับรันบน Server / Docker
            print("กำลังเปิด Browser ด้วย Chrome...", flush=True)

            try:
                browser = p.chromium.launch(
                    headless=True,
                    channel="chrome",
                    args=launch_args
                )

                print(
                    f"✅ เปิด Chrome สำเร็จ | Version: {browser.version}",
                    flush=True
                )

            except Exception as e:

                print(
                    f"⚠️ Chrome เปิดไม่ได้: {type(e).__name__}: {e}",
                    flush=True
                )

                try:
                    print("กำลังลอง Chromium ของ Playwright...", flush=True)

                    browser = p.chromium.launch(
                        headless=True,
                        args=launch_args
                    )

                    print(
                        f"✅ เปิด Chromium สำเร็จ | Version: {browser.version}",
                        flush=True
                    )

                except Exception as e2:

                    print(
                        f"❌ Chromium เปิดไม่ได้: {type(e2).__name__}: {e2}",
                        flush=True
                    )

                    raise
        except Exception:
            try:
                browser = p.chromium.launch(headless=True, channel="msedge", args=launch_args)
            except Exception:
                browser = p.chromium.launch(headless=True, args=launch_args)

        context = browser.new_context(accept_downloads=True, ignore_https_errors=True)
        page = context.new_page()

        page.set_default_navigation_timeout(120000)
        page.set_default_timeout(120000)

        
        # =========================================================
        # 1. เปิดหน้าเข้าสู่ระบบ + Diagnostic
        # =========================================================

        print("=" * 70, flush=True)
        print("STEP 1 : เปิดหน้าเข้าสู่ระบบ", flush=True)
        print(f"LOGIN_URL = {LOGIN_URL}", flush=True)
        print(f"Browser URL ก่อนเปิด = {page.url}", flush=True)

        # ตรวจสอบ Browser ที่กำลังใช้งาน
        try:
            print(
                f"Browser Version = {browser.version}",
                flush=True
            )
        except Exception as e:
            print(
                f"ไม่สามารถอ่าน Browser Version ได้: {e}",
                flush=True
            )

        print("กำลังเรียก page.goto()...", flush=True)

        login_ok = False

        try:
            start_time = datetime.now()

            response = page.goto(
                LOGIN_URL,
                wait_until="commit",
                timeout=30000
            )

            elapsed = (datetime.now() - start_time).total_seconds()

            print(
                f"page.goto() จบการทำงาน ใช้เวลา {elapsed:.2f} วินาที",
                flush=True
            )

            if response:
                print(
                    f"Login HTTP Status = {response.status}",
                    flush=True
                )
                print(
                    f"Login Response URL = {response.url}",
                    flush=True
                )
            else:
                print(
                    "Login HTTP Status = ไม่มี Response",
                    flush=True
                )

            print(
                f"Browser URL หลัง goto = {page.url}",
                flush=True
            )

            try:
                print(
                    f"Page Title = {page.title()}",
                    flush=True
                )
            except Exception as e:
                print(
                    f"อ่าน Page Title ไม่ได้: {e}",
                    flush=True
                )

            login_ok = True

        except Exception as e:

            elapsed = (datetime.now() - start_time).total_seconds()

            print("=" * 70, flush=True)
            print("❌ LOGIN PAGE เปิดไม่สำเร็จ", flush=True)
            print(
                f"Error Type = {type(e).__name__}",
                flush=True
            )
            print(
                f"Error = {e}",
                flush=True
            )
            print(
                f"ใช้เวลา = {elapsed:.2f} วินาที",
                flush=True
            )
            print(
                f"URL ปัจจุบัน = {page.url}",
                flush=True
            )
            print(
                f"Frame จำนวน = {len(page.frames)}",
                flush=True
            )
            print("=" * 70, flush=True)


            # =========================================================
            # ถ้า Login เปิดไม่ได้ → หยุดทันที
            # =========================================================

            if not login_ok:

                print(
                    "❌ ยกเลิกการทำงาน เนื่องจากเปิด True Gateway ไม่สำเร็จ",
                    flush=True
                )

                try:
                    browser.close()
                except Exception:
                    pass

                raise RuntimeError(
                    "ไม่สามารถเปิด True Gateway Login ได้ "
                    f"(URL: {LOGIN_URL}, Browser URL: {page.url})"
                )


            # =========================================================
            # Login เปิดสำเร็จ
            # =========================================================

            print("✅ Login Page เปิดสำเร็จ", flush=True)
            print("กำลังรอหน้า Login โหลด...", flush=True)

            page.wait_for_timeout(3000)

            print(
                f"URL หลังรอ = {page.url}",
                flush=True
            )

            print(
                f"จำนวน Frame = {len(page.frames)}",
                flush=True
            )

        page.wait_for_timeout(5000)

        # ค้นหา Frame ล็อกอิน
        target_page = page
        for frame in page.frames:
            try:
                if frame.locator("input[type='password']").count() > 0:
                    target_page = frame
                    break
            except Exception:
                continue

        print("กำลังกรอก Username และ Password...")
        inputs = target_page.locator("input[type='text'], input[type='password']")
        if inputs.count() >= 2:
            inputs.nth(0).fill(USERNAME)
            inputs.nth(1).fill(PASSWORD)

        print("กำลังกดปุ่มเข้าสู่ระบบ...")
        if target_page.locator("input[type='submit']").count() > 0:
            target_page.locator("input[type='submit']").click()
        elif target_page.locator("input[type='image']").count() > 0:
            target_page.locator("input[type='image']").click()
        else:
            inputs.nth(1).press("Enter")

        page.wait_for_timeout(3000)

        # 2. ยิงตรงไปหน้า Export
        print("กำลังไปยังหน้า Export...")
        try:
            page.goto(EXPORT_URL, wait_until="commit", timeout=120000)
        except Exception as e:
            print(f"กำลังโหลดหน้า Export... ({e})")

        # รอให้หน้าเว็บและ Network โหลดนิ่งสนิทเพื่อป้องกัน Context ถูกทำลายระหว่างทาง
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass

        page.wait_for_timeout(3000)

        # 3. จัดการ Frame หน้า Export (ใส่ try-catch ป้องกันเฟรมที่หลุดไปแล้ว)
        export_page = page
        for frame in page.frames:
            try:
                if frame.locator("input[value='Export']").count() > 0 or frame.locator("#fromDate").count() > 0:
                    export_page = frame
                    break
            except Exception:
                continue

        # 4. เลือก Due Date + ปรับวันที่ +7 วัน
        print("กำลังเลือก Date Type : Due Date และตั้งวันที่...")
        try:
            radios = export_page.locator("input[type='radio']")
            if radios.count() > 0:
                radios.first.check(force=True)
            
            export_page.evaluate(f'''() => {{
                let radioList = document.querySelectorAll("input[type='radio']");
                if (radioList.length > 0) {{
                    radioList[0].checked = true;
                }}
                let fromElem = document.getElementById("fromDate") || document.querySelector("input[name='fromDate']");
                let toElem = document.getElementById("toDate") || document.querySelector("input[name='toDate']");
                if (fromElem) {{
                    fromElem.removeAttribute("readonly");
                    fromElem.value = "{from_date}";
                }}
                if (toElem) {{
                    toElem.removeAttribute("readonly");
                    toElem.value = "{to_date}";
                }}
            }}''')
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตั้งค่าฟอร์ม: {e}")

        page.wait_for_timeout(1500)

        # 5. กด Export ดาวน์โหลด
        print("กำลังกด Export เพื่อดาวน์โหลดไฟล์...")
        with page.expect_download(timeout=90000) as download_info:
            if export_page.locator("input[value='Export']").count() > 0:
                export_page.locator("input[value='Export']").click()
            elif export_page.locator("input[type='button'][value='Export']").count() > 0:
                export_page.locator("input[type='button'][value='Export']").click()
            else:
                export_page.locator("input[name='Export']").click()

        download = download_info.value
        file_path = os.path.join(download_folder, download.suggested_filename)
        download.save_as(file_path)
        print(f"ดาวน์โหลดสำเร็จ! บันทึกไฟล์ไว้ที่: {file_path}")

        browser.close()
        return file_path

if __name__ == "__main__":
    download_report()