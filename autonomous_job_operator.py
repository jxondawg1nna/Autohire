#!/usr/bin/env python3
"""
Autonomous Job Search Operator
Searches for jobs based on CV and keeps relevant matches open in browser
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from app.services.anti_detection.camoufox_browser import (
        CamoufoxBrowserFactory,
        CamoufoxBrowserManager
    )
    from app.services.intelligence.skill_extraction_service import (
        IntelligentSkillMatcher,
        SkillTaxonomy
    )
    PHASE1_AVAILABLE = True
except ImportError:
    print("⚠️  Phase 1 components not installed. Using fallback mode.")
    PHASE1_AVAILABLE = False
    from playwright.async_api import async_playwright

from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutonomousJobOperator:
    """
    Autonomous job search operator with intelligent matching
    """

    def __init__(self, cv_path: str):
        self.cv_path = Path(cv_path)
        self.browser = None
        self.skill_matcher = None
        self.candidate_skills = []
        self.found_jobs = []

    async def initialize(self):
        """Initialize browser and skill matcher"""
        logger.info("🤖 Initializing Autonomous Job Operator...")

        # Load CV
        logger.info(f"📄 Loading CV from: {self.cv_path}")
        with open(self.cv_path, 'r', encoding='utf-8') as f:
            cv_text = f.read()

        if PHASE1_AVAILABLE:
            # Use advanced Camoufox browser
            logger.info("🦊 Starting Camoufox browser (Melbourne, VIC)...")
            self.browser = await CamoufoxBrowserFactory.create_melbourne_browser(
                headless=False  # Keep visible so you can see
            )

            # Initialize skill matcher
            logger.info("🧠 Initializing intelligent skill matcher...")
            self.skill_matcher = IntelligentSkillMatcher(
                taxonomy=SkillTaxonomy.ESCO
            )

            # Extract candidate skills
            logger.info("🔍 Analyzing CV skills...")
            self.candidate_skills = self.skill_matcher.extract_skills_from_cv(
                cv_text,
                experience_years=8  # From CV: 8 years experience
            )

            logger.info(f"✅ Extracted {len(self.candidate_skills)} skills from CV")

            # Show top skills
            top_skills = [s.matched_skill for s in self.candidate_skills[:10] if s.matched_skill]
            logger.info(f"🎯 Top skills: {', '.join(top_skills[:5])}")

        else:
            # Fallback to basic Playwright
            logger.info("🌐 Starting Playwright browser (fallback mode)...")
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            self.page = await context.new_page()

    async def search_jobs(
        self,
        job_board: str = "seek",
        location: str = "Melbourne VIC",
        keywords: str = "Full Stack Developer"
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on specified job board

        Args:
            job_board: "seek", "linkedin", or "indeed"
            location: Job location
            keywords: Search keywords
        """
        logger.info(f"\n🔎 Searching for: {keywords} in {location}")
        logger.info(f"📍 Platform: {job_board.upper()}")

        if job_board == "seek":
            await self._search_seek(keywords, location)
        elif job_board == "linkedin":
            await self._search_linkedin(keywords, location)
        elif job_board == "indeed":
            await self._search_indeed(keywords, location)

        return self.found_jobs

    async def _search_seek(self, keywords: str, location: str):
        """Search on Seek.com.au"""
        if PHASE1_AVAILABLE:
            page = self.browser.get_page()
        else:
            page = self.page

        # Build Seek URL
        keywords_encoded = keywords.replace(' ', '-').lower()
        location_encoded = location.replace(' ', '-').lower()

        url = f"https://www.seek.com.au/{keywords_encoded}-jobs/in-{location_encoded}"

        logger.info(f"🌐 Navigating to Seek: {url}")

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for job cards to load
            await asyncio.sleep(3)

            # Extract job listings
            logger.info("📋 Extracting job listings...")

            # Get job cards (Seek's structure)
            job_cards = await page.query_selector_all('[data-card-type="JobCard"]')

            if not job_cards:
                # Try alternative selectors
                job_cards = await page.query_selector_all('article[data-testid="job-card"]')

            if not job_cards:
                logger.warning("⚠️  No job cards found. Page structure may have changed.")
                # Take screenshot for debugging
                await page.screenshot(path="seek_debug.png")
                logger.info("📸 Screenshot saved to seek_debug.png")

                # Try generic job listing selectors
                job_cards = await page.query_selector_all('a[data-job-id], .job-card, article')

            logger.info(f"Found {len(job_cards)} job listings")

            # Process first 5 jobs
            for i, card in enumerate(job_cards[:5], 1):
                try:
                    job_data = await self._extract_job_from_card(page, card, i)
                    if job_data:
                        self.found_jobs.append(job_data)

                        # Analyze relevance if Phase 1 available
                        if PHASE1_AVAILABLE and self.skill_matcher:
                            await self._analyze_job_relevance(job_data)

                except Exception as e:
                    logger.error(f"❌ Error extracting job {i}: {e}")

        except Exception as e:
            logger.error(f"❌ Error searching Seek: {e}")

    async def _extract_job_from_card(self, page, card, index: int) -> Dict[str, Any]:
        """Extract job details from a job card"""
        try:
            # Extract title
            title_elem = await card.query_selector('a[data-testid="job-title"], h3 a, a.job-title')
            title = await title_elem.inner_text() if title_elem else "Unknown Title"

            # Extract company
            company_elem = await card.query_selector('[data-testid="job-company"], .company-name, span.company')
            company = await company_elem.inner_text() if company_elem else "Unknown Company"

            # Extract location
            location_elem = await card.query_selector('[data-testid="job-location"], .location, span.location')
            location = await location_elem.inner_text() if location_elem else "Unknown Location"

            # Get job URL
            link_elem = await card.query_selector('a')
            job_url = await link_elem.get_attribute('href') if link_elem else None

            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.seek.com.au{job_url}"

            # Extract description preview
            desc_elem = await card.query_selector('[data-testid="job-snippet"], .job-snippet, p')
            description = await desc_elem.inner_text() if desc_elem else ""

            job_data = {
                "index": index,
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "url": job_url,
                "description": description.strip(),
                "relevance_score": None,
                "matched_skills": []
            }

            logger.info(f"\n📌 Job {index}: {title}")
            logger.info(f"   🏢 {company}")
            logger.info(f"   📍 {location}")

            return job_data

        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return None

    async def _analyze_job_relevance(self, job_data: Dict[str, Any]):
        """Analyze job relevance using skill matching"""
        if not self.skill_matcher or not job_data.get('description'):
            return

        try:
            # Extract skills from job description
            job_skills = self.skill_matcher.extract_skills_from_job_description(
                job_data['description'],
                job_title=job_data['title']
            )

            if job_skills:
                # Calculate relevance
                relevance = self.skill_matcher.calculate_relevance_score(
                    self.candidate_skills,
                    job_skills
                )

                job_data['relevance_score'] = relevance.overall_score
                job_data['matched_skills'] = relevance.matched_skills[:5]  # Top 5

                # Log results
                score_pct = relevance.overall_score * 100
                emoji = "🟢" if relevance.overall_score >= 0.7 else "🟡" if relevance.overall_score >= 0.5 else "🔴"

                logger.info(f"   {emoji} Relevance: {score_pct:.0f}% ({relevance.recommendation})")

                if relevance.matched_skills:
                    logger.info(f"   ✅ Matched skills: {', '.join(relevance.matched_skills[:3])}")

        except Exception as e:
            logger.error(f"Error analyzing relevance: {e}")

    async def open_top_jobs_in_tabs(self, min_relevance: float = 0.5):
        """Open the most relevant jobs in separate browser tabs"""
        if not self.found_jobs:
            logger.warning("⚠️  No jobs found to open")
            return

        # Sort by relevance score (if available)
        sorted_jobs = sorted(
            self.found_jobs,
            key=lambda x: x.get('relevance_score') or 0,
            reverse=True
        )

        logger.info(f"\n📑 Opening top jobs in browser tabs...")

        if PHASE1_AVAILABLE:
            context = self.browser.get_context()
        else:
            # For fallback mode, we already have page context
            logger.info("Opening jobs in current browser...")

        opened = 0
        for job in sorted_jobs:
            # Skip jobs below minimum relevance
            if job.get('relevance_score') and job['relevance_score'] < min_relevance:
                logger.info(f"⏭️  Skipping '{job['title']}' - relevance too low ({job['relevance_score']:.1%})")
                continue

            if not job.get('url'):
                logger.warning(f"⚠️  No URL for '{job['title']}'")
                continue

            try:
                logger.info(f"🌐 Opening: {job['title']} ({job.get('relevance_score', 0):.1%} match)")

                if PHASE1_AVAILABLE:
                    # Open in new tab
                    new_page = await context.new_page()
                    await new_page.goto(job['url'], wait_until="domcontentloaded")
                    await asyncio.sleep(2)  # Let page load
                else:
                    # For fallback, open in current page
                    await self.page.goto(job['url'], wait_until="domcontentloaded")
                    await asyncio.sleep(2)

                opened += 1

            except Exception as e:
                logger.error(f"❌ Failed to open '{job['title']}': {e}")

        logger.info(f"\n✅ Opened {opened} job tabs")
        logger.info(f"👀 Browser will stay open for your review")

    async def run(
        self,
        job_board: str = "seek",
        keywords: str = "Full Stack Developer",
        location: str = "Melbourne VIC",
        min_relevance: float = 0.5
    ):
        """
        Run complete autonomous job search workflow

        Args:
            job_board: Job platform to search
            keywords: Search keywords
            location: Job location
            min_relevance: Minimum relevance score to open (0.0-1.0)
        """
        try:
            # Initialize
            await self.initialize()

            # Search for jobs
            jobs = await self.search_jobs(
                job_board=job_board,
                location=location,
                keywords=keywords
            )

            # Open relevant jobs in tabs
            await self.open_top_jobs_in_tabs(min_relevance=min_relevance)

            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("📊 SEARCH SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total jobs found: {len(self.found_jobs)}")

            if PHASE1_AVAILABLE:
                avg_relevance = sum(j.get('relevance_score', 0) for j in self.found_jobs) / len(self.found_jobs) if self.found_jobs else 0
                logger.info(f"Average relevance: {avg_relevance:.1%}")

                high_match = sum(1 for j in self.found_jobs if j.get('relevance_score', 0) >= 0.7)
                logger.info(f"High matches (≥70%): {high_match}")

            logger.info("\n💡 Browser will remain open for your review")
            logger.info("   Press Ctrl+C to close")

            # Keep browser open
            await asyncio.sleep(3600)  # Keep open for 1 hour

        except KeyboardInterrupt:
            logger.info("\n👋 Closing browser...")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if PHASE1_AVAILABLE and self.browser:
                await self.browser.stop()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Autonomous Job Search Operator")
    parser.add_argument(
        "--cv",
        default="sample_cv.txt",
        help="Path to CV file"
    )
    parser.add_argument(
        "--keywords",
        default="Full Stack Developer",
        help="Job search keywords"
    )
    parser.add_argument(
        "--location",
        default="Melbourne VIC",
        help="Job location"
    )
    parser.add_argument(
        "--platform",
        default="seek",
        choices=["seek", "linkedin", "indeed"],
        help="Job board platform"
    )
    parser.add_argument(
        "--min-relevance",
        type=float,
        default=0.5,
        help="Minimum relevance score (0.0-1.0)"
    )

    args = parser.parse_args()

    # Create operator
    operator = AutonomousJobOperator(cv_path=args.cv)

    # Run search
    await operator.run(
        job_board=args.platform,
        keywords=args.keywords,
        location=args.location,
        min_relevance=args.min_relevance
    )


if __name__ == "__main__":
    asyncio.run(main())
