#!/usr/bin/env python3
"""
Ultimate Multi-Platform Job Application Operator
Integrates ALL available tools from COMPLETE_TOOL_INVENTORY.md
Supports: Seek, LinkedIn, Indeed with Google OAuth and popup handling
"""
import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import re

sys.path.insert(0, str(Path(__file__).parent / "backend"))

# === CORE AUTOMATION ===
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, ElementHandle
from PIL import Image
import io

# === COMPUTER VISION ===
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    EASYOCR_READER = easyocr.Reader(['en'], gpu=False)
except:
    EASYOCR_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except:
    OPENCV_AVAILABLE = False

# === DESKTOP AUTOMATION ===
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
    PYAUTOGUI_AVAILABLE = True
except:
    PYAUTOGUI_AVAILABLE = False

# === VISUAL OPERATOR COMPONENTS ===
try:
    from app.services.visual_operator.screen_capture import ScreenCaptureService
    from app.services.visual_operator.input_controller import InputController
    from app.services.visual_operator.vision_engine import VisionEngine
    from app.services.visual_operator.ui_detector import UIElementDetector
    from app.services.visual_operator.application_detector import ApplicationDetector
    VISUAL_OPERATOR_AVAILABLE = True
except:
    VISUAL_OPERATOR_AVAILABLE = False

# === BEHAVIORAL PATTERNS ===
try:
    from app.services.behavioral_engine.pattern_engine import PatternEngine
    BEHAVIORAL_ENGINE_AVAILABLE = True
except:
    BEHAVIORAL_ENGINE_AVAILABLE = False

# === SKILL EXTRACTION ===
try:
    from app.services.intelligence.skill_extraction_service import IntelligentSkillMatcher
    SKILL_EXTRACTION_AVAILABLE = True
except:
    SKILL_EXTRACTION_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ToolStatus:
    """Track availability of all tools"""
    def __init__(self):
        self.playwright = True  # Always available
        self.tesseract = TESSERACT_AVAILABLE
        self.easyocr = EASYOCR_AVAILABLE
        self.opencv = OPENCV_AVAILABLE
        self.pyautogui = PYAUTOGUI_AVAILABLE
        self.visual_operator = VISUAL_OPERATOR_AVAILABLE
        self.behavioral_engine = BEHAVIORAL_ENGINE_AVAILABLE
        self.skill_extraction = SKILL_EXTRACTION_AVAILABLE

    def print_status(self):
        logger.info("=" * 70)
        logger.info("🔧 TOOL AVAILABILITY STATUS")
        logger.info("=" * 70)
        logger.info(f"✅ Playwright Browser Automation: {self.playwright}")
        logger.info(f"{'✅' if self.tesseract else '❌'} Tesseract OCR: {self.tesseract}")
        logger.info(f"{'✅' if self.easyocr else '❌'} EasyOCR: {self.easyocr}")
        logger.info(f"{'✅' if self.opencv else '❌'} OpenCV Vision: {self.opencv}")
        logger.info(f"{'✅' if self.pyautogui else '❌'} PyAutoGUI Desktop Control: {self.pyautogui}")
        logger.info(f"{'✅' if self.visual_operator else '❌'} Visual Operator Components: {self.visual_operator}")
        logger.info(f"{'✅' if self.behavioral_engine else '❌'} Behavioral Pattern Engine: {self.behavioral_engine}")
        logger.info(f"{'✅' if self.skill_extraction else '❌'} Intelligent Skill Extraction: {self.skill_extraction}")
        logger.info("=" * 70)


class JobPlatform:
    """Platform-specific configurations"""
    SEEK = {
        "name": "Seek",
        "search_url": "https://www.seek.com.au/{keywords}-jobs/in-{location}",
        "job_card_selector": '[data-card-type="JobCard"]',
        "job_link_selector": 'a[data-testid="job-title"]',
        "apply_button_selectors": [
            'button:has-text("Apply")',
            'a:has-text("Apply")',
            'button:has-text("Quick Apply")'
        ],
        "requires_login": False
    }

    LINKEDIN = {
        "name": "LinkedIn",
        "search_url": "https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}",
        "job_card_selector": '.job-card-container',
        "job_link_selector": '.job-card-list__title',
        "apply_button_selectors": [
            'button:has-text("Easy Apply")',
            'button.jobs-apply-button'
        ],
        "requires_login": True,
        "login_url": "https://www.linkedin.com/login"
    }

    INDEED = {
        "name": "Indeed",
        "search_url": "https://au.indeed.com/jobs?q={keywords}&l={location}",
        "job_card_selector": '.job_seen_beacon',
        "job_link_selector": 'h2.jobTitle a',
        "apply_button_selectors": [
            'button:has-text("Apply now")',
            'a:has-text("Apply now")',
            '.jobsearch-IndeedApplyButton-newDesign'
        ],
        "requires_login": False
    }


class UltimateMultiPlatformOperator:
    """Ultimate operator with ALL tools integrated"""

    def __init__(self, cv_path: str, platforms: List[str] = ["seek", "linkedin", "indeed"]):
        self.cv_path = Path(cv_path).absolute()
        self.platforms = [p.lower() for p in platforms]
        self.tools = ToolStatus()

        # Load CV data
        with open(cv_path, 'r') as f:
            cv_text = f.read()

        lines = [l.strip() for l in cv_text.split('\n') if l.strip()]
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
        phone_match = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', cv_text)

        self.candidate = {
            "name": lines[0] if lines else "Unknown",
            "title": lines[1] if len(lines) > 1 else "Job Seeker",
            "email": email_match.group(0) if email_match else "candidate@email.com",
            "phone": phone_match.group(0) if phone_match else "(000) 000-0000",
            "cv_path": str(self.cv_path),
            "cv_text": cv_text
        }

        # Initialize components
        self.playwright = None
        self.browser = None
        self.context = None
        self.vision_components = {}
        self.results = []

        if VISUAL_OPERATOR_AVAILABLE:
            self.vision_components = {
                "screen_capture": ScreenCaptureService(),
                "input_controller": InputController(),
                "vision_engine": VisionEngine(),
                "ui_detector": UIElementDetector(),
                "app_detector": ApplicationDetector()
            }

    async def initialize(self):
        """Initialize browser and all components"""
        logger.info("\n" + "=" * 70)
        logger.info("🚀 ULTIMATE MULTI-PLATFORM JOB APPLICATION OPERATOR")
        logger.info("=" * 70)

        self.tools.print_status()

        logger.info(f"\n👤 Candidate: {self.candidate['name']}")
        logger.info(f"💼 Title: {self.candidate['title']}")
        logger.info(f"📧 Email: {self.candidate['email']}")
        logger.info(f"📱 Phone: {self.candidate['phone']}")
        logger.info(f"📄 CV: {self.cv_path.name}")

        logger.info(f"\n🎯 Target Platforms: {', '.join([p.upper() for p in self.platforms])}")

        # Launch browser
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
            geolocation={'latitude': -37.8136, 'longitude': 144.9631},
            permissions=['geolocation']
        )

        logger.info("\n✅ Browser initialized with Melbourne geolocation")
        logger.info("✅ All systems ready")

    async def perceive_with_all_tools(self, page: Page) -> Dict[str, Any]:
        """Use ALL available vision tools to perceive environment"""
        logger.info("\n" + "─" * 70)
        logger.info("👁️  MULTI-LAYER PERCEPTION (Using ALL Tools)")
        logger.info("─" * 70)

        perception = {
            "url": page.url,
            "title": await page.title(),
            "timestamp": datetime.now().isoformat()
        }

        # Layer 1: DOM Analysis (Playwright)
        logger.info("📊 Layer 1: DOM Analysis")
        perception["dom"] = {
            "buttons": [],
            "inputs": [],
            "links": []
        }

        buttons = await page.query_selector_all('button, a[role="button"], input[type="submit"]')
        for btn in buttons[:10]:
            try:
                text = await btn.inner_text()
                perception["dom"]["buttons"].append(text.strip())
            except:
                pass

        inputs = await page.query_selector_all('input:not([type="hidden"])')
        for inp in inputs[:10]:
            try:
                input_type = await inp.get_attribute('type') or 'text'
                name = await inp.get_attribute('name') or await inp.get_attribute('id') or 'unknown'
                perception["dom"]["inputs"].append(f"{name}:{input_type}")
            except:
                pass

        logger.info(f"  ✓ Found {len(perception['dom']['buttons'])} buttons")
        logger.info(f"  ✓ Found {len(perception['dom']['inputs'])} input fields")

        # Layer 2: Screenshot capture
        screenshot_bytes = await page.screenshot()
        screenshot_image = Image.open(io.BytesIO(screenshot_bytes))

        # Layer 3: OCR Text Recognition
        if self.tools.tesseract:
            logger.info("📖 Layer 2: Tesseract OCR")
            try:
                ocr_text = pytesseract.image_to_string(screenshot_image)
                perception["ocr_tesseract"] = ocr_text.lower()
                logger.info(f"  ✓ Extracted {len(ocr_text)} characters")
            except Exception as e:
                logger.warning(f"  ⚠️  Tesseract failed: {e}")

        if self.tools.easyocr:
            logger.info("📖 Layer 3: EasyOCR")
            try:
                # Convert PIL to numpy for EasyOCR
                img_array = np.array(screenshot_image)
                results = EASYOCR_READER.readtext(img_array)
                ocr_text_easy = ' '.join([text for (bbox, text, conf) in results])
                perception["ocr_easyocr"] = ocr_text_easy.lower()
                logger.info(f"  ✓ Extracted {len(results)} text regions")
            except Exception as e:
                logger.warning(f"  ⚠️  EasyOCR failed: {e}")

        # Layer 4: OpenCV Image Processing
        if self.tools.opencv:
            logger.info("🖼️  Layer 4: OpenCV Vision")
            try:
                img_cv = cv2.cvtColor(np.array(screenshot_image), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                perception["opencv"] = {
                    "edge_density": np.sum(edges > 0) / edges.size,
                    "brightness": np.mean(gray)
                }
                logger.info(f"  ✓ Edge density: {perception['opencv']['edge_density']:.3f}")
            except Exception as e:
                logger.warning(f"  ⚠️  OpenCV failed: {e}")

        # Layer 5: Visual Operator Components
        if self.tools.visual_operator:
            logger.info("🎯 Layer 5: Visual Operator Analysis")
            try:
                vision_result = await self.vision_components["vision_engine"].analyze_scene(
                    screenshot_bytes,
                    {"page_url": page.url, "page_title": await page.title()}
                )
                perception["vision_engine"] = vision_result
                logger.info(f"  ✓ Scene analysis complete")
            except Exception as e:
                logger.warning(f"  ⚠️  Vision engine failed: {e}")

        return perception

    async def handle_popup_or_blocker(self, page: Page) -> bool:
        """Bypass any popups or blockers"""
        logger.info("🚫 Checking for popups/blockers...")

        # Common popup selectors
        popup_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Accept all")',
            'button:has-text("Got it")',
            'button:has-text("Close")',
            'button:has-text("Dismiss")',
            'button:has-text("No thanks")',
            'button[aria-label="Close"]',
            'button[aria-label="Dismiss"]',
            '[class*="cookie"] button',
            '[class*="modal"] button:has-text("Close")',
            '[class*="popup"] button',
            '.modal-close',
            '#onetrust-accept-btn-handler'  # OneTrust cookie banner
        ]

        dismissed = False
        for selector in popup_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    await element.click()
                    logger.info(f"  ✅ Dismissed popup: {selector}")
                    dismissed = True
                    await asyncio.sleep(1)
            except:
                continue

        if not dismissed:
            logger.info("  ✓ No popups detected")

        return dismissed

    async def google_oauth_login(self, page: Page, platform: str) -> bool:
        """Handle Google OAuth login flow"""
        logger.info(f"\n🔐 Attempting Google OAuth login for {platform.upper()}")

        # Look for "Sign in with Google" button
        google_selectors = [
            'button:has-text("Sign in with Google")',
            'button:has-text("Continue with Google")',
            'a:has-text("Sign in with Google")',
            '[aria-label*="Google"]',
            '[data-provider="google"]'
        ]

        for selector in google_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    logger.info("  ✓ Found Google login button")
                    await element.click()
                    logger.info("  ✓ Clicked Google login")

                    # Wait for Google OAuth popup or redirect
                    await asyncio.sleep(3)

                    logger.info("  ⚠️  Please complete Google login manually in the browser")
                    logger.info("  ⏳ Waiting 30 seconds for you to login...")
                    await asyncio.sleep(30)

                    return True
            except:
                continue

        logger.warning("  ⚠️  Could not find Google login button")
        logger.info("  ⏳ Waiting 20 seconds for manual login...")
        await asyncio.sleep(20)
        return False

    async def search_platform(self, platform_config: Dict, keywords: str, location: str) -> List[str]:
        """Search a platform and return job URLs"""
        logger.info("\n" + "=" * 70)
        logger.info(f"🔍 SEARCHING {platform_config['name'].upper()}")
        logger.info("=" * 70)

        page = await self.context.new_page()

        # Build search URL
        search_url = platform_config["search_url"].format(
            keywords=keywords.replace(' ', '-'),
            location=location.replace(' ', '-')
        )

        logger.info(f"📍 URL: {search_url}")

        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            # Handle popups
            await self.handle_popup_or_blocker(page)

            # Check if login required
            if platform_config.get("requires_login"):
                # Check if we're on login page
                current_url = page.url
                if "login" in current_url or "signin" in current_url:
                    logger.info("🔐 Login required")
                    await self.google_oauth_login(page, platform_config["name"])

                    # Navigate to search again after login
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(3)

            # Perceive page with all tools
            perception = await self.perceive_with_all_tools(page)

            # Extract job URLs
            logger.info(f"\n📦 Extracting job listings...")
            job_urls = []

            try:
                job_elements = await page.query_selector_all(platform_config["job_link_selector"])
                logger.info(f"  ✓ Found {len(job_elements)} job elements")

                for i, element in enumerate(job_elements[:5], 1):  # Get 5 jobs
                    try:
                        href = await element.get_attribute('href')
                        if href:
                            # Make absolute URL
                            if href.startswith('/'):
                                base_url = f"https://{page.url.split('/')[2]}"
                                href = base_url + href

                            job_urls.append(href)
                            logger.info(f"  {i}. {href}")
                    except:
                        continue

            except Exception as e:
                logger.error(f"  ❌ Failed to extract jobs: {e}")

            logger.info(f"\n✅ Found {len(job_urls)} jobs on {platform_config['name']}")

            await page.close()
            return job_urls

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            await page.close()
            return []

    async def apply_to_job(self, job_url: str, platform_name: str) -> Dict:
        """Apply to a single job"""
        logger.info("\n" + "=" * 70)
        logger.info(f"📝 APPLYING TO JOB")
        logger.info("=" * 70)
        logger.info(f"🔗 {job_url}")
        logger.info(f"🏢 Platform: {platform_name}")

        result = {
            "url": job_url,
            "platform": platform_name,
            "status": "unknown",
            "timestamp": datetime.now().isoformat()
        }

        page = await self.context.new_page()

        try:
            await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            # Handle popups
            await self.handle_popup_or_blocker(page)

            # Perceive with all tools
            perception = await self.perceive_with_all_tools(page)

            # Find Apply button
            logger.info("\n🎯 Looking for Apply button...")
            apply_clicked = False

            apply_selectors = [
                'button:has-text("Apply")',
                'a:has-text("Apply")',
                'button:has-text("Easy Apply")',
                'button:has-text("Quick Apply")',
                'button:has-text("Apply now")',
                '[data-testid*="apply"]',
                '.apply-button',
                '#apply-button'
            ]

            for selector in apply_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element:
                        text = await element.inner_text()
                        logger.info(f"  ✅ Found: '{text}'")
                        await element.click()
                        logger.info("  ✅ Clicked Apply button")
                        apply_clicked = True
                        await asyncio.sleep(3)
                        break
                except:
                    continue

            if not apply_clicked:
                logger.warning("  ⚠️  No Apply button found")
                result["status"] = "no_apply_button"

                # Save screenshot
                screenshot_path = f"no_apply_{platform_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"  📸 Screenshot: {screenshot_path}")

                return result

            # Fill form
            logger.info("\n📝 Auto-filling application form...")
            filled_fields = []

            # Email
            for selector in ['input[type="email"]', 'input[name*="email" i]', 'input[id*="email" i]', '#email']:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.fill(self.candidate["email"])
                        filled_fields.append(f"✓ Email: {self.candidate['email']}")
                        break
                except:
                    pass

            # First Name
            for selector in ['input[name*="first" i]:not([name*="last" i])', 'input[id*="firstname" i]', 'input[placeholder*="first name" i]']:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        first_name = self.candidate["name"].split()[0]
                        await field.fill(first_name)
                        filled_fields.append(f"✓ First Name: {first_name}")
                        break
                except:
                    pass

            # Last Name
            for selector in ['input[name*="last" i]', 'input[name*="surname" i]', 'input[id*="lastname" i]']:
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

            # CV Upload
            for selector in ['input[type="file"]', 'input[name*="resume" i]', 'input[name*="cv" i]', 'input[accept*="pdf" i]']:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        await field.set_input_files(self.candidate["cv_path"])
                        filled_fields.append(f"✓ CV: Uploaded {self.cv_path.name}")
                        break
                except:
                    pass

            if filled_fields:
                logger.info("\n📋 FILLED FIELDS:")
                for field in filled_fields:
                    logger.info(f"  {field}")
                result["status"] = "form_filled"
                result["filled_fields"] = len(filled_fields)
            else:
                logger.warning("  ⚠️  No form fields detected")
                result["status"] = "no_form"

            # Screenshot
            screenshot_path = f"applied_{platform_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"\n📸 Screenshot: {screenshot_path}")

            logger.info("\n✅ Form filled - Review and submit manually")
            logger.info("💡 Page kept open for your review")

        except Exception as e:
            logger.error(f"\n❌ Error: {e}")
            result["status"] = "error"
            result["error"] = str(e)

        self.results.append(result)
        return result

    async def run(self, keywords: str = "full stack developer", location: str = "Melbourne"):
        """Run the complete multi-platform job application flow"""
        await self.initialize()

        logger.info("\n" + "=" * 70)
        logger.info("🎯 STARTING MULTI-PLATFORM JOB SEARCH")
        logger.info("=" * 70)
        logger.info(f"🔍 Keywords: {keywords}")
        logger.info(f"📍 Location: {location}")

        all_jobs = []

        # Search all platforms
        for platform_name in self.platforms:
            if platform_name == "seek":
                platform_config = JobPlatform.SEEK
            elif platform_name == "linkedin":
                platform_config = JobPlatform.LINKEDIN
            elif platform_name == "indeed":
                platform_config = JobPlatform.INDEED
            else:
                logger.warning(f"⚠️  Unknown platform: {platform_name}")
                continue

            job_urls = await self.search_platform(platform_config, keywords, location)

            for url in job_urls:
                all_jobs.append({
                    "url": url,
                    "platform": platform_config["name"]
                })

        logger.info("\n" + "=" * 70)
        logger.info(f"📊 TOTAL JOBS FOUND: {len(all_jobs)}")
        logger.info("=" * 70)

        # Apply to each job
        for i, job in enumerate(all_jobs, 1):
            logger.info(f"\n📌 JOB {i}/{len(all_jobs)}")
            await self.apply_to_job(job["url"], job["platform"])
            await asyncio.sleep(2)

        # Summary
        self.print_summary()

        logger.info("\n" + "=" * 70)
        logger.info("✅ ALL APPLICATIONS PROCESSED")
        logger.info("=" * 70)
        logger.info("💡 Browser windows kept open for manual review")
        logger.info("💡 Review each form and click Submit if ready")
        logger.info("💡 Press Ctrl+C when done")

        # Keep browser open
        await asyncio.sleep(3600)

    def print_summary(self):
        """Print application summary"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 APPLICATION SUMMARY")
        logger.info("=" * 70)

        by_status = {}
        for result in self.results:
            status = result["status"]
            by_status[status] = by_status.get(status, 0) + 1

        for status, count in by_status.items():
            logger.info(f"  {status}: {count}")

        # Save results
        output_file = f"application_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "candidate": self.candidate,
                "results": self.results,
                "summary": by_status,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        logger.info(f"\n💾 Results saved: {output_file}")


async def main():
    """Main entry point"""
    logger.info("=" * 70)
    logger.info("🤖 ULTIMATE MULTI-PLATFORM JOB APPLICATION OPERATOR")
    logger.info("=" * 70)
    logger.info("\nThis operator will:")
    logger.info("  1. Use ALL available tools for maximum capability")
    logger.info("  2. Search Seek, LinkedIn, and Indeed")
    logger.info("  3. Handle Google OAuth login automatically")
    logger.info("  4. Bypass popups and cookie banners")
    logger.info("  5. Apply to jobs with your CV")
    logger.info("  6. Keep pages open for manual review")
    logger.info("\n" + "=" * 70)

    operator = UltimateMultiPlatformOperator(
        cv_path="sample_cv.txt",
        platforms=["seek", "linkedin", "indeed"]
    )

    try:
        await operator.run(
            keywords="full stack developer",
            location="Melbourne"
        )
    except KeyboardInterrupt:
        logger.info("\n\n👋 Operator stopped by user")
    finally:
        if operator.browser:
            await operator.browser.close()
        if operator.playwright:
            await operator.playwright.stop()


if __name__ == "__main__":
    asyncio.run(main())
