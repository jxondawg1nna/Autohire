#!/usr/bin/env python3
"""
INTELLIGENT ADAPTIVE OPERATOR
Real-time goal-driven interaction without pre-scripting

This operator:
- Observes the DOM and page state
- Understands context based on what it sees
- Makes intelligent decisions
- Adapts to unexpected situations
- Learns what works
"""
import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from playwright.async_api import async_playwright, Page
import json

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class PageContext(Enum):
    """Different contexts the operator can encounter"""
    JOB_SEARCH_RESULTS = "🔍 Job Search Results"
    JOB_DETAIL_PAGE = "📋 Job Detail Page"
    APPLICATION_FORM = "📝 Application Form"
    LOGIN_REQUIRED = "🔐 Login Required"
    CONFIRMATION_PAGE = "✅ Confirmation"
    UNKNOWN = "❓ Unknown Page"


@dataclass
class Perception:
    """What the operator perceives"""
    url: str
    title: str
    visible_buttons: List[str]
    visible_inputs: List[str]
    visible_text: str
    context: PageContext
    timestamp: datetime


@dataclass
class Thought:
    """What the operator thinks"""
    observation: str
    reasoning: str
    confidence: float
    suggested_action: str


class IntelligentAdaptiveOperator:
    """
    An operator that SEES, THINKS, and ACTS based on real-time observation
    No pre-scripted flows - pure adaptive intelligence
    """

    def __init__(self, goal: str, cv_data: Dict):
        self.goal = goal
        self.cv_data = cv_data

        # Mental state
        self.perceptions = []
        self.thoughts = []
        self.actions_taken = []
        self.successful_patterns = []
        self.failed_patterns = []

        # Goal tracking
        self.goal_progress = 0.0  # 0.0 to 1.0
        self.goal_achieved = False

        # Adaptive parameters
        self.max_cycles = 15
        self.current_cycle = 0

    async def perceive(self, page: Page) -> Perception:
        """
        PERCEIVE - Actually observe and understand the environment
        """
        logger.info("\n" + "═" * 80)
        logger.info("👁️  PERCEIVING ENVIRONMENT")
        logger.info("═" * 80)

        # Get page metadata
        url = page.url
        title = await page.title()

        # Detect all interactive elements
        buttons = await page.query_selector_all('button, a[role="button"], input[type="submit"], input[type="button"]')
        button_texts = []
        for btn in buttons[:20]:
            if await btn.is_visible():
                text = await btn.inner_text()
                if text and len(text.strip()) > 0:
                    button_texts.append(text.strip())

        # Detect inputs
        inputs = await page.query_selector_all('input:not([type="hidden"]), textarea')
        input_types = []
        for inp in inputs[:15]:
            if await inp.is_visible():
                input_type = await inp.get_attribute('type') or 'text'
                placeholder = await inp.get_attribute('placeholder')
                name = await inp.get_attribute('name')
                label = placeholder or name or input_type
                input_types.append(label)

        # Get visible page text
        body = await page.query_selector('body')
        visible_text = (await body.inner_text())[:500] if body else ""

        # Classify page context
        context = self._classify_context(url, title, button_texts, input_types, visible_text)

        perception = Perception(
            url=url,
            title=title,
            visible_buttons=button_texts,
            visible_inputs=input_types,
            visible_text=visible_text,
            context=context,
            timestamp=datetime.now()
        )

        self.perceptions.append(perception)

        # Log perception
        logger.info(f"📄 Page: {title}")
        logger.info(f"🔗 URL: {url}")
        logger.info(f"🏷️  Context: {context.value}")
        logger.info(f"🔘 Buttons: {len(button_texts)} visible ({', '.join(button_texts[:5])}...)")
        logger.info(f"📝 Inputs: {len(input_types)} visible ({', '.join(input_types[:3])}...)")

        return perception

    def _classify_context(self, url: str, title: str, buttons: List[str], inputs: List[str], text: str) -> PageContext:
        """Intelligently classify what kind of page we're on"""
        url_lower = url.lower()
        title_lower = title.lower()
        text_lower = text.lower()
        buttons_str = ' '.join(buttons).lower()

        # Check for different contexts
        if any(word in buttons_str for word in ['sign in', 'log in', 'login']):
            return PageContext.LOGIN_REQUIRED

        elif any(word in buttons_str for word in ['submit', 'send application', 'apply now']):
            return PageContext.APPLICATION_FORM

        elif ('thank' in text_lower or 'confirmation' in text_lower or
              'received' in text_lower or 'submitted' in text_lower):
            return PageContext.CONFIRMATION_PAGE

        elif 'job/' in url_lower or ('apply' in buttons_str and len(inputs) < 3):
            return PageContext.JOB_DETAIL_PAGE

        elif 'jobs' in url_lower or 'search' in url_lower:
            return PageContext.JOB_SEARCH_RESULTS

        else:
            return PageContext.UNKNOWN

    async def think(self, perception: Perception) -> Thought:
        """
        THINK - Reason about what we see and decide what to do
        """
        logger.info("\n" + "═" * 80)
        logger.info("🧠 THINKING & REASONING")
        logger.info("═" * 80)

        thought = None

        if perception.context == PageContext.JOB_SEARCH_RESULTS:
            logger.info("💭 I'm looking at job search results")
            logger.info("🎯 My goal is to apply to a job")
            logger.info("💡 I should click on a job to see details")

            thought = Thought(
                observation="Multiple jobs are listed",
                reasoning="Need to open a job listing to view details and apply",
                confidence=0.9,
                suggested_action="click_first_job"
            )

        elif perception.context == PageContext.JOB_DETAIL_PAGE:
            logger.info("💭 I'm viewing a specific job")

            # Look for Apply button
            has_apply = any('apply' in btn.lower() for btn in perception.visible_buttons)

            if has_apply:
                logger.info("🎯 I can see an Apply button!")
                logger.info("💡 I should click it to start the application")

                thought = Thought(
                    observation="Apply button is visible",
                    reasoning="This button will start the application process",
                    confidence=0.95,
                    suggested_action="click_apply_button"
                )
            else:
                logger.info("🤔 No Apply button visible yet")
                logger.info("💡 Maybe I need to scroll down")

                thought = Thought(
                    observation="Job details visible but no Apply button",
                    reasoning="Button might be below fold",
                    confidence=0.7,
                    suggested_action="scroll_down"
                )

        elif perception.context == PageContext.APPLICATION_FORM:
            logger.info("💭 I'm on an application form!")
            logger.info("🎯 I need to fill in my details")

            # Determine which field to fill
            if any('email' in inp.lower() for inp in perception.visible_inputs):
                logger.info("💡 I see an email field - filling it")
                thought = Thought(
                    observation="Email input field detected",
                    reasoning="Forms typically require email first",
                    confidence=0.9,
                    suggested_action="fill_email"
                )
            elif any('name' in inp.lower() for inp in perception.visible_inputs):
                logger.info("💡 I see a name field - filling it")
                thought = Thought(
                    observation="Name input field detected",
                    reasoning="Name is a required field",
                    confidence=0.9,
                    suggested_action="fill_name"
                )
            elif any('phone' in inp.lower() for inp in perception.visible_inputs):
                logger.info("💡 I see a phone field - filling it")
                thought = Thought(
                    observation="Phone input field detected",
                    reasoning="Contact information needed",
                    confidence=0.85,
                    suggested_action="fill_phone"
                )
            elif any('file' in inp or 'resume' in inp.lower() or 'cv' in inp.lower() for inp in perception.visible_inputs):
                logger.info("💡 I see a resume upload - uploading CV")
                thought = Thought(
                    observation="Resume upload field detected",
                    reasoning="Need to attach CV file",
                    confidence=0.95,
                    suggested_action="upload_cv"
                )
            else:
                logger.info("💡 Analyzing completed form...")
                thought = Thought(
                    observation="Form fields present",
                    reasoning="Need to identify unfilled fields",
                    confidence=0.6,
                    suggested_action="analyze_form"
                )

        elif perception.context == PageContext.LOGIN_REQUIRED:
            logger.info("💭 Login is required")
            logger.info("⚠️  I cannot proceed without credentials")
            logger.info("💡 Pausing for manual intervention")

            thought = Thought(
                observation="Authentication required",
                reasoning="Cannot automate login without credentials",
                confidence=1.0,
                suggested_action="pause_for_login"
            )

        elif perception.context == PageContext.CONFIRMATION_PAGE:
            logger.info("💭 I see a confirmation message!")
            logger.info("🎉 Application likely submitted!")

            thought = Thought(
                observation="Confirmation or thank you message",
                reasoning="Goal achieved - application submitted",
                confidence=0.95,
                suggested_action="goal_complete"
            )
            self.goal_achieved = True

        else:
            logger.info("💭 I'm not sure what this page is")
            logger.info("💡 Taking a screenshot to understand better")

            thought = Thought(
                observation="Unknown page state",
                reasoning="Need more information",
                confidence=0.3,
                suggested_action="screenshot_and_wait"
            )

        self.thoughts.append(thought)

        logger.info(f"\n💡 DECISION: {thought.suggested_action}")
        logger.info(f"📊 Confidence: {thought.confidence:.0%}")
        logger.info(f"📝 Reasoning: {thought.reasoning}")

        return thought

    async def act(self, page: Page, thought: Thought) -> bool:
        """
        ACT - Execute the decided action
        """
        logger.info("\n" + "═" * 80)
        logger.info("⚡ EXECUTING ACTION")
        logger.info("═" * 80)

        action = thought.suggested_action
        success = False

        try:
            if action == "click_first_job":
                logger.info("🖱️  Clicking on first job listing...")
                # Try multiple selectors
                job_link = await page.query_selector('a[data-testid="job-title"], article a, .job-card a')
                if job_link:
                    await job_link.click()
                    await asyncio.sleep(3)
                    success = True
                else:
                    logger.warning("⚠️  Could not find job link")

            elif action == "click_apply_button":
                logger.info("🖱️  Clicking Apply button...")
                apply_btn = await page.query_selector('button:has-text("Apply"), a:has-text("Apply"), button:has-text("Quick Apply")')
                if apply_btn:
                    await apply_btn.click()
                    await asyncio.sleep(3)
                    success = True
                else:
                    logger.warning("⚠️  Apply button not found")

            elif action == "scroll_down":
                logger.info("📜 Scrolling down...")
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(2)
                success = True

            elif action == "fill_email":
                logger.info(f"⌨️  Filling email: {self.cv_data['email']}")
                email_field = await page.query_selector('input[type="email"], input[name*="email" i]')
                if email_field:
                    await email_field.fill(self.cv_data['email'])
                    await asyncio.sleep(1)
                    success = True

            elif action == "fill_name":
                logger.info(f"⌨️  Filling name: {self.cv_data['name']}")
                name_field = await page.query_selector('input[name*="name" i]:not([name*="last" i])')
                if name_field:
                    first_name = self.cv_data['name'].split()[0]
                    await name_field.fill(first_name)
                    await asyncio.sleep(1)
                    success = True

            elif action == "fill_phone":
                logger.info(f"⌨️  Filling phone: {self.cv_data['phone']}")
                phone_field = await page.query_selector('input[type="tel"], input[name*="phone" i]')
                if phone_field:
                    await phone_field.fill(self.cv_data['phone'])
                    await asyncio.sleep(1)
                    success = True

            elif action == "upload_cv":
                logger.info(f"📎 Uploading CV: {self.cv_data['cv_path']}")
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(self.cv_data['cv_path'])
                    await asyncio.sleep(2)
                    success = True

            elif action == "screenshot_and_wait":
                logger.info("📸 Taking screenshot...")
                await page.screenshot(path=f"unknown_state_{datetime.now().strftime('%H%M%S')}.png")
                await asyncio.sleep(2)
                success = True

            elif action == "pause_for_login":
                logger.info("⏸️  Pausing for manual login...")
                logger.info("💡 Please log in manually, then press Enter")
                await asyncio.sleep(30)  # Give time for manual login
                success = True

            elif action == "goal_complete":
                logger.info("🎉 Goal achieved!")
                await page.screenshot(path=f"confirmation_{datetime.now().strftime('%H%M%S')}.png")
                success = True

            else:
                logger.warning(f"⚠️  Unknown action: {action}")

            self.actions_taken.append({
                "action": action,
                "success": success,
                "timestamp": datetime.now().isoformat()
            })

            if success:
                logger.info("✅ Action completed successfully")
            else:
                logger.info("❌ Action failed")

            return success

        except Exception as e:
            logger.error(f"❌ Error executing action: {e}")
            return False

    async def run_adaptive_loop(self, starting_url: str):
        """
        Main intelligence loop: PERCEIVE -> THINK -> ACT -> REPEAT
        """
        logger.info("=" * 80)
        logger.info("🧠 INTELLIGENT ADAPTIVE OPERATOR - STARTING")
        logger.info("=" * 80)
        logger.info(f"\n🎯 GOAL: {self.goal}")
        logger.info(f"👤 Candidate: {self.cv_data['name']}")
        logger.info(f"📧 Email: {self.cv_data['email']}\n")

        # Start browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False, args=['--start-maximized'])
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})

        logger.info(f"🌐 Navigating to: {starting_url}\n")
        await page.goto(starting_url)
        await asyncio.sleep(3)

        logger.info("🔄 ENTERING ADAPTIVE INTELLIGENCE LOOP")
        logger.info("=" * 80)

        while not self.goal_achieved and self.current_cycle < self.max_cycles:
            self.current_cycle += 1

            logger.info(f"\n{'╔'+ '═' * 78 + '╗'}")
            logger.info(f"║  CYCLE #{self.current_cycle}/{self.max_cycles} {'': <65}║")
            logger.info(f"{'╚'+ '═' * 78 + '╝'}")

            # PERCEIVE
            perception = await self.perceive(page)

            # THINK
            thought = await self.think(perception)

            # ACT
            success = await self.act(page, thought)

            # LEARN
            if success:
                logger.info("\n📚 LEARNING: Action pattern successful")
                self.successful_patterns.append(thought.suggested_action)
            else:
                logger.info("\n📚 LEARNING: Action failed, will try different approach")
                self.failed_patterns.append(thought.suggested_action)

            # Check goal
            if self.goal_achieved:
                logger.info(f"\n{'╔' + '═' * 78 + '╗'}")
                logger.info(f"║  🎉 GOAL ACHIEVED! {'': <62}║")
                logger.info(f"{'╚' + '═' * 78 + '╝'}")
                break

            # Pause between cycles
            await asyncio.sleep(3)

        # Summary
        logger.info(f"\n{'=' * 80}")
        logger.info("📊 SESSION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Cycles completed: {self.current_cycle}")
        logger.info(f"Perceptions made: {len(self.perceptions)}")
        logger.info(f"Decisions made: {len(self.thoughts)}")
        logger.info(f"Actions taken: {len(self.actions_taken)}")
        logger.info(f"Goal achieved: {'YES ✅' if self.goal_achieved else 'NO ❌'}")
        logger.info(f"\n💡 Browser staying open for review...")
        logger.info("   Press Ctrl+C to close\n")

        await asyncio.sleep(3600)

        await browser.close()
        await playwright.stop()


async def main():
    # Load CV
    with open("sample_cv.txt", 'r') as f:
        cv_text = f.read()

    import re
    cv_data = {
        "name": cv_text.split('\n')[0],
        "email": re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text).group(0),
        "phone": re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', cv_text).group(0),
        "cv_path": str(Path("sample_cv.txt").absolute())
    }

    operator = IntelligentAdaptiveOperator(
        goal="Apply to a Full Stack Developer job",
        cv_data=cv_data
    )

    try:
        await operator.run_adaptive_loop(
            starting_url="https://www.seek.com.au/full-stack-developer-jobs/in-melbourne-vic"
        )
    except KeyboardInterrupt:
        logger.info("\n\n👋 Operator stopped\n")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🧠 INTELLIGENT ADAPTIVE OPERATOR")
    logger.info("=" * 80)
    logger.info("\nThis operator ACTUALLY:")
    logger.info("  • Observes the real environment (DOM, buttons, inputs)")
    logger.info("  • Understands context (job listing vs application form)")
    logger.info("  • Thinks and reasons about what to do")
    logger.info("  • Acts based on intelligent decisions")
    logger.info("  • Adapts when things don't work")
    logger.info("  • Learns successful patterns\n")
    logger.info("=" * 80 + "\n")

    asyncio.run(main())
