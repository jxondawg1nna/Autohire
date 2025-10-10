#!/usr/bin/env python3
"""
Intelligent Job Application Operator
- Reads and analyzes CV
- Searches jobs based on CV skills/experience
- Picks top 5 most relevant jobs
- Generates tailored CV for each job (2+ pages)
- Demonstrates thought process at every step
"""
import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any
import json

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from playwright.async_api import async_playwright, Page
from backend.app.services.cv_analysis_service import CVAnalysisService
from backend.app.services.cv_generator_service import CVGeneratorService

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class JobPlatform:
    """Platform configurations"""
    SEEK = {
        "name": "Seek",
        "search_url": "https://www.seek.com.au/{keywords}-jobs/in-{location}",
        "job_card_selector": '[data-card-type="JobCard"]',
        "job_link_selector": 'a[data-testid="job-title"]',
        "job_desc_selector": '[data-automation="jobAdDetails"]',
    }

    LINKEDIN = {
        "name": "LinkedIn",
        "search_url": "https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}",
        "job_card_selector": '.job-card-container',
        "job_link_selector": '.job-card-list__title',
        "job_desc_selector": '.show-more-less-html__markup',
    }

    INDEED = {
        "name": "Indeed",
        "search_url": "https://au.indeed.com/jobs?q={keywords}&l={location}",
        "job_card_selector": '.job_seen_beacon',
        "job_link_selector": 'h2.jobTitle a',
        "job_desc_selector": '#jobDescriptionText',
    }


class IntelligentJobOperator:
    """
    Intelligent operator that:
    1. Analyzes CV to understand skills/experience
    2. Searches for relevant jobs
    3. Ranks jobs by relevance
    4. Picks top 5
    5. Creates tailored CV for each
    6. Demonstrates reasoning throughout
    """

    def __init__(self, cv_path: str):
        self.cv_path = Path(cv_path).absolute()
        self.cv_analysis_service = CVAnalysisService()
        self.cv_generator_service = CVGeneratorService()

        self.cv_analysis = None
        self.playwright = None
        self.browser = None
        self.context = None

        self.thought_log = []
        self.results = []

    async def initialize(self):
        """Initialize operator and analyze CV"""
        logger.info("\n" + "=" * 80)
        logger.info("🤖 INTELLIGENT JOB APPLICATION OPERATOR")
        logger.info("=" * 80)

        # Step 1: Analyze CV
        self._log_thought("STEP 1", "Analyzing CV to understand candidate profile")
        self.cv_analysis = self.cv_analysis_service.analyze_cv(str(self.cv_path))

        personal = self.cv_analysis['personal_info']
        logger.info(f"\n👤 Candidate Profile:")
        logger.info(f"   Name: {personal['name']}")
        logger.info(f"   Title: {personal['title']}")
        logger.info(f"   Location: {personal['location']}")
        logger.info(f"   Skills: {', '.join(self.cv_analysis['skills'][:10])}")
        logger.info(f"   Search Keywords: {', '.join(self.cv_analysis['keywords'][:5])}")

        self._log_thought(
            "ANALYSIS",
            f"Identified {len(self.cv_analysis['skills'])} technical skills and "
            f"{len(self.cv_analysis['experience'])} work experiences. "
            f"Will search for: {', '.join(self.cv_analysis['keywords'][:3])}"
        )

        # Step 2: Initialize browser
        self._log_thought("STEP 2", "Initializing browser automation")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
        )

        logger.info("✅ Browser ready for job search")

    def _log_thought(self, phase: str, thought: str):
        """Log operator's thought process"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{phase}] {thought}"
        self.thought_log.append(entry)
        logger.info(f"\n💭 {entry}")

    async def search_jobs(self, platform_config: Dict, keywords: List[str]) -> List[Dict]:
        """
        Search for jobs on a platform

        Returns:
            List of job dictionaries with title, company, url, description
        """
        platform_name = platform_config['name']
        logger.info("\n" + "=" * 80)
        logger.info(f"🔍 SEARCHING {platform_name.upper()}")
        logger.info("=" * 80)

        # Use top keywords for search
        search_term = " ".join(keywords[:3])  # Top 3 keywords
        self._log_thought(
            f"SEARCH-{platform_name}",
            f"Searching {platform_name} for: '{search_term}'"
        )

        page = await self.context.new_page()

        # Build search URL
        search_url = platform_config["search_url"].format(
            keywords=search_term.replace(' ', '-'),
            location="Melbourne"
        )

        logger.info(f"📍 URL: {search_url}")

        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            # Handle popups
            await self._dismiss_popups(page)

            # Extract job listings
            self._log_thought(
                f"EXTRACT-{platform_name}",
                "Extracting job listings from search results"
            )

            jobs = []
            try:
                job_elements = await page.query_selector_all(platform_config["job_link_selector"])
                logger.info(f"   Found {len(job_elements)} job listings")

                for i, element in enumerate(job_elements[:10], 1):  # Get up to 10
                    try:
                        href = await element.get_attribute('href')
                        title = await element.inner_text()

                        if href:
                            # Make absolute URL
                            if href.startswith('/'):
                                base_url = f"https://{page.url.split('/')[2]}"
                                href = base_url + href

                            jobs.append({
                                'title': title.strip(),
                                'url': href,
                                'platform': platform_name,
                                'company': 'Unknown',  # Will extract on detail page
                                'description': ''  # Will extract on detail page
                            })

                            logger.info(f"   {i}. {title.strip()}")

                    except Exception as e:
                        logger.debug(f"Error extracting job {i}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error extracting jobs: {e}")

            await page.close()
            return jobs

        except Exception as e:
            logger.error(f"Search failed: {e}")
            await page.close()
            return []

    async def get_job_details(self, job: Dict) -> Dict:
        """
        Get detailed information about a job

        Returns:
            Updated job dict with description
        """
        page = await self.context.new_page()

        try:
            await page.goto(job['url'], wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)

            await self._dismiss_popups(page)

            # Extract job description
            description = ""
            desc_selectors = [
                '[data-automation="jobAdDetails"]',  # Seek
                '.show-more-less-html__markup',  # LinkedIn
                '#jobDescriptionText',  # Indeed
                '.jobsearch-jobDescriptionText',  # Indeed alt
                '[class*="description"]',  # Generic
            ]

            for selector in desc_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        description = await element.inner_text()
                        break
                except:
                    continue

            job['description'] = description[:1000]  # First 1000 chars

            # Extract company if available
            company_selectors = [
                '[data-automation="advertiser-name"]',  # Seek
                '.jobs-unified-top-card__company-name',  # LinkedIn
                '[data-testid="company-name"]',  # Indeed
                '[class*="company"]',  # Generic
            ]

            for selector in company_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        job['company'] = (await element.inner_text()).strip()
                        break
                except:
                    continue

        except Exception as e:
            logger.debug(f"Error getting job details: {e}")

        await page.close()
        return job

    async def _dismiss_popups(self, page: Page):
        """Dismiss any popups or cookie banners"""
        popup_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Got it")',
            'button:has-text("Close")',
            'button[aria-label="Close"]',
            '#onetrust-accept-btn-handler'
        ]

        for selector in popup_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    await element.click()
                    await asyncio.sleep(0.5)
            except:
                continue

    def rank_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Rank jobs by relevance to CV

        Returns:
            Sorted list of jobs with relevance scores
        """
        logger.info("\n" + "=" * 80)
        logger.info("📊 RANKING JOBS BY RELEVANCE")
        logger.info("=" * 80)

        self._log_thought(
            "RANKING",
            f"Calculating relevance scores for {len(jobs)} jobs based on CV skills and keywords"
        )

        for job in jobs:
            job_text = f"{job['title']} {job['description']}".lower()
            score = self.cv_analysis_service.calculate_job_relevance(
                job_text,
                self.cv_analysis
            )
            job['relevance_score'] = score

            logger.info(f"   {job['title'][:50]:50} | Relevance: {score:.1f}%")

        # Sort by relevance
        ranked_jobs = sorted(jobs, key=lambda x: x['relevance_score'], reverse=True)

        self._log_thought(
            "DECISION",
            f"Selected top 5 jobs with relevance scores: "
            f"{', '.join([f'{j[\"relevance_score\"]:.0f}%' for j in ranked_jobs[:5]])}"
        )

        return ranked_jobs

    async def apply_to_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Create tailored CVs and apply to jobs

        Returns:
            List of application results
        """
        logger.info("\n" + "=" * 80)
        logger.info("📝 CREATING TAILORED CVS AND APPLYING")
        logger.info("=" * 80)

        results = []

        for i, job in enumerate(jobs[:5], 1):  # Top 5 jobs
            logger.info(f"\n{'=' * 80}")
            logger.info(f"JOB {i}/5: {job['title']}")
            logger.info(f"Company: {job['company']}")
            logger.info(f"Relevance: {job['relevance_score']:.1f}%")
            logger.info(f"{'=' * 80}")

            self._log_thought(
                f"JOB-{i}",
                f"Starting application for '{job['title']}' at {job['company']}"
            )

            # Generate tailored CV
            self._log_thought(
                f"CV-GEN-{i}",
                f"Generating tailored CV emphasizing relevant skills: "
                f"{', '.join([s for s in self.cv_analysis['skills'] if s.lower() in job['description'].lower()][:3])}"
            )

            cv_filename = f"cv_tailored_{job['platform']}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            cv_output_path = Path("generated_cvs") / cv_filename

            try:
                cv_result = self.cv_generator_service.generate_tailored_cv(
                    self.cv_analysis,
                    job,
                    str(cv_output_path)
                )

                self._log_thought(
                    f"CV-COMPLETE-{i}",
                    f"Generated {cv_result['word_count']}-word CV (~{cv_result['word_count'] // 400 + 1} pages) "
                    f"with {cv_result['relevant_skills']} relevant skills highlighted"
                )

                # Simulate application (would actually apply here)
                self._log_thought(
                    f"APPLY-{i}",
                    f"Would now navigate to application page and fill form with tailored CV"
                )

                results.append({
                    'job': job,
                    'cv_path': str(cv_output_path),
                    'cv_details': cv_result,
                    'status': 'cv_generated',
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Error generating CV: {e}")
                results.append({
                    'job': job,
                    'status': 'error',
                    'error': str(e)
                })

        return results

    def save_results(self):
        """Save application results and thought log"""
        output_file = f"application_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        results_data = {
            'candidate': self.cv_analysis['personal_info'],
            'cv_skills': self.cv_analysis['skills'],
            'search_keywords': self.cv_analysis['keywords'],
            'thought_process': self.thought_log,
            'applications': self.results,
            'timestamp': datetime.now().isoformat()
        }

        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)

        logger.info(f"\n💾 Results saved to: {output_file}")

        # Print thought log summary
        logger.info("\n" + "=" * 80)
        logger.info("🧠 THOUGHT PROCESS SUMMARY")
        logger.info("=" * 80)
        for thought in self.thought_log:
            logger.info(thought)

    async def run(self):
        """Run the complete intelligent job application workflow"""
        try:
            # Initialize
            await self.initialize()

            # Step 3: Search jobs
            self._log_thought("STEP 3", "Searching job platforms for relevant positions")
            all_jobs = []

            for platform_config in [JobPlatform.SEEK, JobPlatform.INDEED]:
                jobs = await self.search_jobs(platform_config, self.cv_analysis['keywords'])
                all_jobs.extend(jobs)

            logger.info(f"\n✅ Found {len(all_jobs)} total jobs across platforms")

            # Step 4: Get job details
            self._log_thought("STEP 4", f"Fetching detailed descriptions for {len(all_jobs)} jobs")
            detailed_jobs = []
            for job in all_jobs[:15]:  # Limit to 15 for performance
                detailed_job = await self.get_job_details(job)
                if detailed_job['description']:
                    detailed_jobs.append(detailed_job)

            # Step 5: Rank jobs
            self._log_thought("STEP 5", "Ranking jobs by relevance to candidate profile")
            ranked_jobs = self.rank_jobs(detailed_jobs)

            # Step 6: Apply to top 5
            self._log_thought("STEP 6", "Creating tailored CVs and applying to top 5 jobs")
            self.results = await self.apply_to_jobs(ranked_jobs)

            # Step 7: Save results
            self._log_thought("STEP 7", "Saving application results and thought log")
            self.save_results()

            logger.info("\n" + "=" * 80)
            logger.info("✅ WORKFLOW COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   • Analyzed CV with {len(self.cv_analysis['skills'])} skills")
            logger.info(f"   • Searched {len(all_jobs)} jobs across platforms")
            logger.info(f"   • Ranked {len(detailed_jobs)} jobs by relevance")
            logger.info(f"   • Generated {len([r for r in self.results if r['status'] == 'cv_generated'])} tailored CVs")
            logger.info(f"   • Logged {len(self.thought_log)} thought process steps")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"\n❌ Error in workflow: {e}")
            raise

        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()


async def main():
    """Entry point"""
    cv_path = "test_cv.txt"  # Default CV path

    logger.info("=" * 80)
    logger.info("🤖 INTELLIGENT JOB APPLICATION OPERATOR")
    logger.info("=" * 80)
    logger.info("\nThis operator will:")
    logger.info("  1. 📄 Analyze your CV to understand skills and experience")
    logger.info("  2. 🔍 Search job platforms for relevant positions")
    logger.info("  3. 📊 Rank jobs by relevance to your profile")
    logger.info("  4. 🎯 Pick top 5 most relevant jobs")
    logger.info("  5. ✍️  Create tailored CV for each job (2+ pages)")
    logger.info("  6. 💭 Demonstrate thought process at every step")
    logger.info("=" * 80)

    operator = IntelligentJobOperator(cv_path=cv_path)

    try:
        await operator.run()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Operator stopped by user")


if __name__ == "__main__":
    asyncio.run(main())
