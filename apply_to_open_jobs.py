#!/usr/bin/env python3
"""
Apply to Currently Open Job Tabs
Works with browser tabs already open from previous search
"""
import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any
import json

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from playwright.async_api import async_playwright
from PIL import Image
import pytesseract
import io
import pyautogui

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class JobApplicationBot:
    """Autonomous bot to apply to open job tabs"""

    def __init__(self, cv_path: str):
        self.cv_path = Path(cv_path).absolute()
        self.playwright = None
        self.browser = None
        self.context = None

        # Load candidate data
        with open(cv_path, 'r') as f:
            cv_text = f.read()

        lines = [l.strip() for l in cv_text.split('\n') if l.strip()]

        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
        phone_match = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', cv_text)

        self.candidate = {
            "name": lines[0],
            "title": lines[1],
            "email": email_match.group(0) if email_match else "jane.smith@email.com",
            "phone": phone_match.group(0) if phone_match else "(555) 123-4567",
            "cv_path": str(self.cv_path)
        }

        self.results = []

    async def connect_to_running_browser(self):
        """Connect to already-running browser"""
        logger.info("=" * 70)
        logger.info("🤖 AUTONOMOUS JOB APPLICATION BOT")
        logger.info("=" * 70)
        logger.info(f"\n👤 Candidate: {self.candidate['name']}")
        logger.info(f"📧 Email: {self.candidate['email']}")
        logger.info(f"📄 CV: {self.candidate['cv_path']}")

        # Start new browser instance
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )

        logger.info("\n✅ Browser ready")

    async def analyze_page(self, page) -> Dict:
        """Analyze current page"""
        logger.info("\n" + "-" * 70)
        logger.info("👁️  ANALYZING PAGE WITH COMPUTER VISION")
        logger.info("-" * 70)

        # Get URL and title
        url = page.url
        title = await page.title()

        logger.info(f"📄 Page: {title}")
        logger.info(f"🔗 URL: {url}")

        # Take screenshot
        screenshot_bytes = await page.screenshot()
        image = Image.open(io.BytesIO(screenshot_bytes))

        # OCR
        try:
            ocr_text = pytesseract.image_to_string(image).lower()

            analysis = {
                "url": url,
                "title": title,
                "has_apply_button": "apply" in ocr_text or "submit" in ocr_text,
                "has_form": any(word in ocr_text for word in ["email", "name", "phone", "resume", "cv"]),
                "requires_login": any(word in ocr_text for word in ["sign in", "log in", "login"]),
                "is_application_page": "application" in ocr_text or "apply" in ocr_text
            }

            logger.info(f"✓ Apply button detected: {analysis['has_apply_button']}")
            logger.info(f"✓ Form fields detected: {analysis['has_form']}")
            logger.info(f"✓ Requires login: {analysis['requires_login']}")

            return analysis

        except Exception as e:
            logger.warning(f"⚠️  OCR failed: {e}")
            return {"url": url, "title": title}

    async def find_and_click_apply(self, page) -> bool:
        """Find and click Apply button"""
        logger.info("\n🎯 SEARCHING FOR APPLY BUTTON...")

        selectors = [
            'button:has-text("Apply")',
            'a:has-text("Apply")',
            'button:has-text("Submit Application")',
            'a:has-text("Submit Application")',
            '[data-testid*="apply"]',
            'button[class*="apply" i]',
            'a[class*="apply" i]',
            'button:has-text("Quick Apply")',
            'a:has-text("Quick Apply")'
        ]

        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    text = await element.inner_text()
                    logger.info(f"✅ Found: '{text}' button")

                    # Click it
                    await element.click()
                    logger.info("✅ Clicked Apply button")
                    await asyncio.sleep(3)
                    return True

            except:
                continue

        logger.warning("⚠️  No Apply button found")
        return False

    async def fill_form(self, page):
        """Auto-fill application form"""
        logger.info("\n📝 AUTO-FILLING APPLICATION FORM")
        logger.info("-" * 70)

        filled_fields = []

        # Email
        for selector in ['input[type="email"]', 'input[name*="email" i]', 'input[id*="email" i]']:
            try:
                field = await page.query_selector(selector)
                if field:
                    await field.fill(self.candidate["email"])
                    filled_fields.append(f"✓ Email: {self.candidate['email']}")
                    break
            except:
                pass

        # Name
        for selector in ['input[name*="name" i]:not([name*="last" i]):not([name*="sur" i])',
                        'input[id*="firstname" i]',
                        'input[placeholder*="first name" i]']:
            try:
                field = await page.query_selector(selector)
                if field:
                    first_name = self.candidate["name"].split()[0]
                    await field.fill(first_name)
                    filled_fields.append(f"✓ First Name: {first_name}")
                    break
            except:
                pass

        # Last name
        for selector in ['input[name*="lastname" i]', 'input[name*="surname" i]',
                        'input[id*="lastname" i]', 'input[placeholder*="last name" i]']:
            try:
                field = await page.query_selector(selector)
                if field:
                    last_name = ' '.join(self.candidate["name"].split()[1:])
                    await field.fill(last_name)
                    filled_fields.append(f"✓ Last Name: {last_name}")
                    break
            except:
                pass

        # Phone
        for selector in ['input[type="tel"]', 'input[name*="phone" i]', 'input[id*="phone" i]']:
            try:
                field = await page.query_selector(selector)
                if field:
                    await field.fill(self.candidate["phone"])
                    filled_fields.append(f"✓ Phone: {self.candidate['phone']}")
                    break
            except:
                pass

        # Resume upload
        for selector in ['input[type="file"]', 'input[name*="resume" i]', 'input[name*="cv" i]']:
            try:
                field = await page.query_selector(selector)
                if field:
                    await field.set_input_files(self.candidate["cv_path"])
                    filled_fields.append(f"✓ CV: Uploaded {self.cv_path.name}")
                    break
            except:
                pass

        # Log results
        if filled_fields:
            logger.info("\n📋 FILLED FIELDS:")
            for field in filled_fields:
                logger.info(f"  {field}")
        else:
            logger.warning("⚠️  No form fields detected")

        # Screenshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"form_filled_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"\n📸 Screenshot saved: {screenshot_path}")

        return len(filled_fields) > 0

    async def process_job(self, job_url: str, job_num: int) -> Dict:
        """Process single job application"""
        logger.info("\n" + "=" * 70)
        logger.info(f"📌 JOB #{job_num}")
        logger.info("=" * 70)

        result = {
            "job_number": job_num,
            "url": job_url,
            "status": "unknown",
            "details": []
        }

        try:
            # Open page
            page = await self.context.new_page()
            await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            # Analyze
            analysis = await self.analyze_page(page)

            # Try to apply
            if analysis.get("requires_login"):
                result["status"] = "requires_login"
                result["details"].append("Page requires authentication")
                logger.warning("⚠️  SKIP: Login required")

            elif await self.find_and_click_apply(page):
                await asyncio.sleep(3)

                # Try to fill form
                if await self.fill_form(page):
                    result["status"] = "form_filled"
                    result["details"].append("Form auto-filled successfully")
                    logger.info("\n✅ SUCCESS: Form filled (review and submit manually)")
                else:
                    result["status"] = "no_form_detected"
                    result["details"].append("Apply button clicked but no form found")

            else:
                result["status"] = "no_apply_button"
                result["details"].append("Could not find Apply button")
                logger.warning("⚠️  SKIP: No Apply button")

            # Keep page open
            logger.info(f"\n💡 Page kept open for review")

        except Exception as e:
            result["status"] = "error"
            result["details"].append(str(e))
            logger.error(f"❌ ERROR: {e}")

        self.results.append(result)
        return result

    async def run(self, job_urls: List[str]):
        """Run batch application"""
        await self.connect_to_running_browser()

        logger.info(f"\n🎯 PROCESSING {len(job_urls)} JOB APPLICATIONS")
        logger.info("=" * 70)

        for i, url in enumerate(job_urls, 1):
            await self.process_job(url, i)
            await asyncio.sleep(2)

        # Summary
        self.print_summary()

        logger.info("\n💡 Browser will stay open. Review and submit applications manually.")
        logger.info("   Press Ctrl+C when done.")

        await asyncio.sleep(3600)

    def print_summary(self):
        """Print summary"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 APPLICATION SUMMARY")
        logger.info("=" * 70)

        form_filled = sum(1 for r in self.results if r["status"] == "form_filled")
        requires_login = sum(1 for r in self.results if r["status"] == "requires_login")
        no_button = sum(1 for r in self.results if r["status"] == "no_apply_button")
        errors = sum(1 for r in self.results if r["status"] == "error")

        logger.info(f"\n✅ Forms auto-filled: {form_filled}")
        logger.info(f"🔐 Requires login: {requires_login}")
        logger.info(f"❌ No apply button: {no_button}")
        logger.info(f"⚠️  Errors: {errors}")

        # Save log
        with open("application_results.json", "w") as f:
            json.dump({
                "candidate": self.candidate,
                "results": self.results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        logger.info(f"\n💾 Results saved: application_results.json")


async def main():
    # Example URLs - replace with your actual job URLs
    job_urls = [
        # Add your 5 job URLs here from the open tabs
        "https://www.seek.com.au/job/80813359",  # Example
    ]

    if len(job_urls) == 1 and "example" in job_urls[0].lower():
        logger.error("\n❌ ERROR: Please add actual job URLs to the script")
        logger.info("\nTo use this bot:")
        logger.info("1. Open apply_to_open_jobs.py")
        logger.info("2. Replace the job_urls list with your actual URLs")
        logger.info("3. Run: python apply_to_open_jobs.py")
        return

    bot = JobApplicationBot(cv_path="sample_cv.txt")

    try:
        await bot.run(job_urls)
    except KeyboardInterrupt:
        logger.info("\n\n👋 Bot stopped by user")
    finally:
        if bot.browser:
            await bot.browser.close()
        if bot.playwright:
            await bot.playwright.stop()


if __name__ == "__main__":
    # For testing with live Seek jobs
    logger.info("🤖 Job Application Bot")
    logger.info("=" * 70)
    logger.info("\nThis bot will:")
    logger.info("  1. Open each job URL")
    logger.info("  2. Analyze page with OCR vision")
    logger.info("  3. Find and click Apply button")
    logger.info("  4. Auto-fill forms with your CV data")
    logger.info("  5. Upload your CV file")
    logger.info("  6. Keep pages open for manual review/submit")
    logger.info("\n" + "=" * 70)

    asyncio.run(main())
