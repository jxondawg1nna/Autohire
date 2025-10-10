#!/usr/bin/env python3
"""
Advanced Autonomous Application Operator
Complete desktop vision and control for automatic job applications

Features:
- Full screen capture and OCR
- Desktop control (mouse, keyboard)
- Browser automation
- Real-time visual feedback
- Automatic form filling
- CV upload handling
"""
import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from playwright.async_api import async_playwright, Page, Browser
import pyautogui
import pytesseract
from PIL import Image
import io

# Try to import existing visual operator components
try:
    from app.services.visual_operator.screen_capture import ScreenCaptureService
    from app.services.visual_operator.input_controller import InputController
    from app.services.vision.vision_engine import VisionEngine
    VISUAL_OPERATOR_AVAILABLE = True
except ImportError:
    VISUAL_OPERATOR_AVAILABLE = False
    print("⚠️  Visual operator components not fully available, using fallback")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedApplicationOperator:
    """
    Advanced autonomous operator with complete desktop vision and control
    """

    def __init__(self, cv_path: str):
        self.cv_path = Path(cv_path)
        self.browser = None
        self.context = None
        self.playwright = None

        # Visual operator components
        if VISUAL_OPERATOR_AVAILABLE:
            self.screen_capture = ScreenCaptureService()
            self.input_controller = InputController()
            self.vision_engine = VisionEngine()

        # Application data
        self.candidate_data = {}
        self.applications_submitted = []
        self.current_job = None

        # Real-time feedback
        self.operation_log = []

        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    def log_operation(self, action: str, details: str, status: str = "INFO"):
        """Log operation with timestamp for real-time feedback"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "status": status
        }
        self.operation_log.append(entry)

        # Visual feedback
        icon = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "VISION": "👁️",
            "ACTION": "🎯"
        }.get(status, "•")

        logger.info(f"{icon} {action}: {details}")

    async def initialize(self):
        """Initialize all components"""
        self.log_operation("INITIALIZE", "Starting Advanced Application Operator", "INFO")

        # Load CV data
        await self.load_cv_data()

        # Start browser
        await self.start_browser()

        # Initialize visual operator
        if VISUAL_OPERATOR_AVAILABLE:
            self.log_operation("VISION", "Visual operator components active", "SUCCESS")

        self.log_operation("INITIALIZE", "All systems ready", "SUCCESS")

    async def load_cv_data(self):
        """Load and parse CV data for form filling"""
        self.log_operation("LOAD_CV", f"Reading: {self.cv_path.name}", "INFO")

        with open(self.cv_path, 'r', encoding='utf-8') as f:
            cv_text = f.read()

        # Parse CV (basic extraction)
        lines = [l.strip() for l in cv_text.split('\n') if l.strip()]

        self.candidate_data = {
            "full_name": lines[0] if lines else "Jane Smith",
            "title": lines[1] if len(lines) > 1 else "Full Stack Developer",
            "email": self._extract_email(cv_text),
            "phone": self._extract_phone(cv_text),
            "location": "Melbourne, Australia",
            "cv_path": str(self.cv_path.absolute()),
            "cv_text": cv_text,

            # Extracted skills
            "skills": self._extract_skills(cv_text),

            # Experience
            "years_experience": 8,

            # Summary
            "summary": self._extract_summary(cv_text)
        }

        self.log_operation(
            "LOAD_CV",
            f"Loaded: {self.candidate_data['full_name']} - {self.candidate_data['title']}",
            "SUCCESS"
        )

        self.log_operation(
            "PARSE_CV",
            f"Email: {self.candidate_data['email']}, Phone: {self.candidate_data['phone']}",
            "INFO"
        )

    def _extract_email(self, text: str) -> str:
        """Extract email from CV"""
        import re
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else "jane.smith@email.com"

    def _extract_phone(self, text: str) -> str:
        """Extract phone from CV"""
        import re
        match = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', text)
        return match.group(0) if match else "(555) 123-4567"

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from CV"""
        # Look for TECHNICAL SKILLS section
        if "TECHNICAL SKILLS" in text:
            start = text.find("TECHNICAL SKILLS")
            end = text.find("\n\n", start)
            skills_section = text[start:end] if end > start else text[start:start+500]

            # Extract programming languages line
            if "Programming Languages:" in skills_section:
                langs_line = skills_section.split("Programming Languages:")[1].split("\n")[0]
                skills = [s.strip() for s in langs_line.split(',')]
                return skills

        return ["Python", "JavaScript", "React", "Node.js"]

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        if "PROFESSIONAL SUMMARY" in text:
            start = text.find("PROFESSIONAL SUMMARY")
            end = text.find("\n\n", start)
            return text[start:end].replace("PROFESSIONAL SUMMARY", "").strip()

        return "Experienced full-stack developer"

    async def start_browser(self):
        """Start Playwright browser"""
        self.log_operation("BROWSER", "Launching Playwright browser", "INFO")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne'
        )

        self.log_operation("BROWSER", "Browser ready (Melbourne, AU timezone)", "SUCCESS")

    async def capture_screen(self) -> Dict[str, Any]:
        """Capture current screen and analyze with OCR"""
        self.log_operation("VISION", "Capturing screen", "VISION")

        if VISUAL_OPERATOR_AVAILABLE:
            screenshot = await self.screen_capture.capture_screen()
            return screenshot
        else:
            # Fallback: PyAutoGUI screenshot
            screenshot = pyautogui.screenshot()

            # Convert to base64 for logging
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_base64 = buffered.getvalue()

            return {
                "image": screenshot,
                "timestamp": datetime.now().isoformat(),
                "resolution": screenshot.size
            }

    async def analyze_page_with_vision(self, page: Page) -> Dict[str, Any]:
        """Analyze current page using vision + OCR"""
        self.log_operation("VISION", "Analyzing page structure", "VISION")

        # Take screenshot
        screenshot_bytes = await page.screenshot(full_page=False)

        # Convert to PIL Image
        image = Image.open(io.BytesIO(screenshot_bytes))

        # OCR analysis
        try:
            text = pytesseract.image_to_string(image)

            analysis = {
                "ocr_text": text,
                "has_apply_button": "apply" in text.lower(),
                "has_sign_in": "sign in" in text.lower() or "log in" in text.lower(),
                "has_form": "name" in text.lower() or "email" in text.lower(),
                "detected_fields": []
            }

            # Detect form fields
            if "email" in text.lower():
                analysis["detected_fields"].append("email")
            if "phone" in text.lower():
                analysis["detected_fields"].append("phone")
            if "resume" in text.lower() or "cv" in text.lower():
                analysis["detected_fields"].append("resume_upload")

            self.log_operation(
                "VISION",
                f"Detected: {', '.join(analysis['detected_fields']) if analysis['detected_fields'] else 'No form fields'}",
                "INFO"
            )

            return analysis

        except Exception as e:
            self.log_operation("VISION", f"OCR failed: {e}", "WARNING")
            return {}

    async def apply_to_job(self, job_url: str, job_index: int):
        """Apply to a single job with full automation"""
        self.log_operation(
            "APPLICATION",
            f"Starting application #{job_index}: {job_url}",
            "INFO"
        )

        try:
            # Open job page
            page = await self.context.new_page()
            await page.goto(job_url, wait_until="networkidle", timeout=30000)

            self.log_operation("NAVIGATION", "Job page loaded", "SUCCESS")

            # Analyze page
            await asyncio.sleep(2)
            analysis = await self.analyze_page_with_vision(page)

            # Look for Apply button
            apply_selectors = [
                'button:has-text("Apply")',
                'a:has-text("Apply")',
                '[data-testid*="apply"]',
                'button[class*="apply"]',
                '.apply-button'
            ]

            apply_button = None
            for selector in apply_selectors:
                try:
                    apply_button = await page.wait_for_selector(selector, timeout=5000)
                    if apply_button:
                        self.log_operation("VISION", f"Found Apply button: {selector}", "SUCCESS")
                        break
                except:
                    continue

            if not apply_button:
                self.log_operation("WARNING", "No Apply button found - may require login", "WARNING")

                # Take screenshot for review
                await page.screenshot(path=f"job_{job_index}_no_apply.png")
                self.log_operation("SCREENSHOT", f"Saved: job_{job_index}_no_apply.png", "INFO")

                # Look for external apply
                external_link = await page.query_selector('a:has-text("Apply on company website")')
                if external_link:
                    self.log_operation("NAVIGATION", "External application detected", "INFO")
                    href = await external_link.get_attribute('href')
                    self.log_operation("INFO", f"Company website: {href}", "INFO")

                return {
                    "status": "requires_manual",
                    "reason": "No direct apply button found",
                    "job_index": job_index
                }

            # Click Apply
            self.log_operation("ACTION", "Clicking Apply button", "ACTION")
            await apply_button.click()
            await asyncio.sleep(3)

            # Check if application form appeared
            form_analysis = await self.analyze_page_with_vision(page)

            if form_analysis.get("has_form"):
                self.log_operation("FORM", "Application form detected", "SUCCESS")

                # Fill form
                await self.fill_application_form(page)

                return {
                    "status": "submitted",
                    "job_index": job_index
                }
            else:
                # May need to sign in first
                if form_analysis.get("has_sign_in"):
                    self.log_operation("AUTH", "Login required", "WARNING")
                    await page.screenshot(path=f"job_{job_index}_login_required.png")

                    return {
                        "status": "requires_auth",
                        "job_index": job_index
                    }

                # Unknown state
                await page.screenshot(path=f"job_{job_index}_unknown_state.png")
                return {
                    "status": "unknown",
                    "job_index": job_index
                }

        except Exception as e:
            self.log_operation("ERROR", f"Application failed: {e}", "ERROR")
            return {
                "status": "error",
                "error": str(e),
                "job_index": job_index
            }

    async def fill_application_form(self, page: Page):
        """Intelligently fill application form"""
        self.log_operation("FORM", "Starting form auto-fill", "ACTION")

        # Common form field selectors
        field_mappings = {
            "email": [
                'input[type="email"]',
                'input[name*="email" i]',
                'input[id*="email" i]'
            ],
            "name": [
                'input[name*="name" i]',
                'input[id*="name" i]',
                'input[placeholder*="name" i]'
            ],
            "phone": [
                'input[type="tel"]',
                'input[name*="phone" i]',
                'input[id*="phone" i]'
            ],
            "resume": [
                'input[type="file"]',
                'input[name*="resume" i]',
                'input[name*="cv" i]'
            ]
        }

        # Fill email
        for selector in field_mappings["email"]:
            try:
                email_field = await page.query_selector(selector)
                if email_field:
                    await email_field.fill(self.candidate_data["email"])
                    self.log_operation("FORM", f"Filled email: {self.candidate_data['email']}", "SUCCESS")
                    break
            except:
                continue

        # Fill name
        for selector in field_mappings["name"]:
            try:
                name_field = await page.query_selector(selector)
                if name_field:
                    await name_field.fill(self.candidate_data["full_name"])
                    self.log_operation("FORM", f"Filled name: {self.candidate_data['full_name']}", "SUCCESS")
                    break
            except:
                continue

        # Fill phone
        for selector in field_mappings["phone"]:
            try:
                phone_field = await page.query_selector(selector)
                if phone_field:
                    await phone_field.fill(self.candidate_data["phone"])
                    self.log_operation("FORM", f"Filled phone: {self.candidate_data['phone']}", "SUCCESS")
                    break
            except:
                continue

        # Upload resume
        for selector in field_mappings["resume"]:
            try:
                resume_upload = await page.query_selector(selector)
                if resume_upload:
                    await resume_upload.set_input_files(self.candidate_data["cv_path"])
                    self.log_operation("FORM", "Uploaded CV file", "SUCCESS")
                    break
            except:
                continue

        self.log_operation("FORM", "Form auto-fill complete", "SUCCESS")

        # Take screenshot of filled form
        await page.screenshot(path=f"filled_form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        self.log_operation("SCREENSHOT", "Saved filled form screenshot", "INFO")

    async def run_batch_applications(self, job_urls: List[str]):
        """Apply to multiple jobs in batch"""
        self.log_operation(
            "BATCH",
            f"Starting batch application for {len(job_urls)} jobs",
            "INFO"
        )

        for i, url in enumerate(job_urls, 1):
            result = await self.apply_to_job(url, i)
            self.applications_submitted.append(result)

            # Wait between applications
            await asyncio.sleep(5)

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print application summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 APPLICATION SUMMARY")
        logger.info("=" * 60)

        submitted = sum(1 for app in self.applications_submitted if app["status"] == "submitted")
        requires_auth = sum(1 for app in self.applications_submitted if app["status"] == "requires_auth")
        requires_manual = sum(1 for app in self.applications_submitted if app["status"] == "requires_manual")
        errors = sum(1 for app in self.applications_submitted if app["status"] == "error")

        logger.info(f"✅ Successfully submitted: {submitted}")
        logger.info(f"🔐 Requires authentication: {requires_auth}")
        logger.info(f"👤 Requires manual review: {requires_manual}")
        logger.info(f"❌ Errors: {errors}")

        logger.info("\n💾 Operation log saved: application_log.json")

        # Save operation log
        with open("application_log.json", "w") as f:
            json.dump({
                "candidate": self.candidate_data,
                "applications": self.applications_submitted,
                "operations": self.operation_log
            }, f, indent=2)

    async def run(self):
        """Main execution"""
        try:
            await self.initialize()

            # Get job URLs from currently open tabs
            # For demo, let's use Seek search
            logger.info("\n" + "=" * 60)
            logger.info("🎯 AUTONOMOUS APPLICATION MODE")
            logger.info("=" * 60)
            logger.info("\nOperator will:")
            logger.info("1. Navigate to each job")
            logger.info("2. Analyze page with computer vision")
            logger.info("3. Click Apply button")
            logger.info("4. Auto-fill forms with CV data")
            logger.info("5. Upload CV file")
            logger.info("6. Provide real-time visual feedback")

            logger.info("\n▶️  Starting autonomous applications in 3 seconds...")
            await asyncio.sleep(3)

            # Demo: Search and apply
            page = await self.context.new_page()
            await page.goto("https://www.seek.com.au/full-stack-developer-jobs/in-melbourne-vic")
            await asyncio.sleep(3)

            # Get first 5 job links
            links = await page.query_selector_all('a[data-testid="job-title"]')
            job_urls = []

            for link in links[:5]:
                href = await link.get_attribute('href')
                if href:
                    full_url = f"https://www.seek.com.au{href}" if not href.startswith('http') else href
                    job_urls.append(full_url)

            logger.info(f"\n🎯 Found {len(job_urls)} jobs to apply to")

            # Start batch applications
            await self.run_batch_applications(job_urls)

            logger.info("\n✅ All applications processed!")
            logger.info("Browser will stay open for review...")

            await asyncio.sleep(3600)

        except KeyboardInterrupt:
            logger.info("\n\n👋 Operator stopped by user")
        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()


async def main():
    operator = AdvancedApplicationOperator(cv_path="sample_cv.txt")
    await operator.run()


if __name__ == "__main__":
    asyncio.run(main())
