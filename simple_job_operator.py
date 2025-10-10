#!/usr/bin/env python3
"""
Simple Job Search Operator - Uses existing Playwright installation
No Phase 1 dependencies required
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class SimpleJobOperator:
    """Simple job search operator using Playwright"""

    def __init__(self, cv_path: str):
        self.cv_path = Path(cv_path)
        self.playwright = None
        self.browser = None
        self.context = None
        self.pages = []
        self.found_jobs = []

    async def initialize(self):
        """Initialize browser"""
        logger.info("=" * 60)
        logger.info("🤖 AUTONOMOUS JOB SEARCH OPERATOR")
        logger.info("=" * 60)

        # Load CV
        logger.info(f"\n📄 Loading CV: {self.cv_path.name}")
        with open(self.cv_path, 'r', encoding='utf-8') as f:
            cv_text = f.read()

        # Extract basic info from CV
        lines = cv_text.split('\n')
        name = lines[0] if lines else "Candidate"
        role = lines[1] if len(lines) > 1 else "Professional"

        logger.info(f"👤 Candidate: {name}")
        logger.info(f"💼 Role: {role}")

        # Start browser
        logger.info(f"\n🌐 Starting browser...")
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

        logger.info("✅ Browser ready")

    async def search_seek(self, keywords: str, location: str):
        """Search Seek.com.au"""
        logger.info("\n" + "=" * 60)
        logger.info(f"🔎 SEARCHING: {keywords}")
        logger.info(f"📍 LOCATION: {location}")
        logger.info("=" * 60)

        # Create search page
        page = await self.context.new_page()
        self.pages.append(page)

        # Build URL
        keywords_clean = keywords.replace(' ', '-').lower()
        location_clean = location.replace(' ', '-').lower().replace(',', '')

        url = f"https://www.seek.com.au/{keywords_clean}-jobs/in-{location_clean}"

        logger.info(f"\n🌐 URL: {url}")
        logger.info("⏳ Loading job listings...")

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)

            logger.info("\n📋 Extracting jobs...")

            # Try to find job cards
            # Seek uses data-testid attributes
            job_cards = await page.query_selector_all('[data-card-type="JobCard"]')

            if not job_cards:
                # Fallback selectors
                job_cards = await page.query_selector_all('article[data-testid*="job"]')

            if not job_cards:
                # Try generic article tags
                job_cards = await page.query_selector_all('article')

            logger.info(f"✅ Found {len(job_cards)} job listings\n")

            # Extract first 5 jobs
            for i, card in enumerate(job_cards[:5], 1):
                try:
                    job = await self._extract_job(card, i)
                    if job:
                        self.found_jobs.append(job)

                except Exception as e:
                    logger.error(f"❌ Error extracting job {i}: {e}")

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")

    async def _extract_job(self, card, index: int) -> Dict[str, Any]:
        """Extract job details from card"""
        try:
            # Title
            title_elem = await card.query_selector('[data-testid*="job-title"], h3 a, a')
            title_text = await title_elem.inner_text() if title_elem else "Unknown"
            title = title_text.strip()

            # Company
            company_elem = await card.query_selector('[data-testid*="company"], span[data-testid*="company"]')
            company_text = await company_elem.inner_text() if company_elem else "Unknown Company"
            company = company_text.strip()

            # Location
            location_elem = await card.query_selector('[data-testid*="location"], span[data-testid*="location"]')
            location_text = await location_elem.inner_text() if location_elem else "Unknown"
            location = location_text.strip()

            # URL
            link = await card.query_selector('a[href]')
            href = await link.get_attribute('href') if link else None
            url = f"https://www.seek.com.au{href}" if href and not href.startswith('http') else href

            # Description snippet
            desc_elem = await card.query_selector('[data-testid*="snippet"], p')
            desc_text = await desc_elem.inner_text() if desc_elem else ""
            description = desc_text.strip()

            # Print job info
            logger.info(f"📌 JOB {index}:")
            logger.info(f"   📋 {title}")
            logger.info(f"   🏢 {company}")
            logger.info(f"   📍 {location}")
            if description:
                preview = description[:80] + "..." if len(description) > 80 else description
                logger.info(f"   💬 {preview}")
            logger.info("")

            return {
                "index": index,
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "description": description
            }

        except Exception as e:
            logger.error(f"Error in _extract_job: {e}")
            return None

    async def open_job_tabs(self):
        """Open each job in a new tab"""
        logger.info("=" * 60)
        logger.info("📑 OPENING JOB TABS")
        logger.info("=" * 60)

        opened = 0
        for job in self.found_jobs:
            if not job.get('url'):
                continue

            try:
                logger.info(f"\n🌐 Opening: {job['title']}")

                # Open in new tab
                new_page = await self.context.new_page()
                self.pages.append(new_page)

                await new_page.goto(job['url'], wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(1.5)

                logger.info(f"   ✅ Opened in tab {opened + 2}")  # +2 because tab 1 is search results
                opened += 1

            except Exception as e:
                logger.error(f"   ❌ Failed: {e}")

        logger.info(f"\n✅ Successfully opened {opened}/{len(self.found_jobs)} job tabs")

    async def run(self, keywords: str = "Full Stack Developer", location: str = "Melbourne VIC"):
        """Run complete workflow"""
        try:
            # Initialize
            await self.initialize()

            # Search
            await self.search_seek(keywords, location)

            # Open tabs
            if self.found_jobs:
                await self.open_job_tabs()
            else:
                logger.warning("\n⚠️  No jobs found to open")

            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("📊 SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Jobs found: {len(self.found_jobs)}")
            logger.info(f"Tabs open: {len(self.pages)}")
            logger.info(f"\n💡 Browser will stay open for review")
            logger.info("   Press Ctrl+C when done")

            # Keep open
            await asyncio.sleep(3600)

        except KeyboardInterrupt:
            logger.info("\n\n👋 Closing browser...")
        except Exception as e:
            logger.error(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()


async def main():
    operator = SimpleJobOperator(cv_path="sample_cv.txt")
    await operator.run(
        keywords="Full Stack Developer",
        location="Melbourne VIC"
    )


if __name__ == "__main__":
    asyncio.run(main())
