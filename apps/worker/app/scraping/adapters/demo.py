from __future__ import annotations

from datetime import datetime, timezone
from typing import AsyncIterator

from playwright.async_api import Playwright

from ...schemas import NormalizedJob
from .base import AdapterContext, BaseSiteAdapter


class DemoBoardAdapter(BaseSiteAdapter):
    """Reference adapter that demonstrates scraping workflow expectations."""

    slug = "demo-board"
    display_name = "Demo Job Board"
    rate_limit_per_minute = 10

    def __init__(self, context: AdapterContext):
        super().__init__(context)
        self._html_document = """
            <html>
                <body>
                    <ul id="jobs">
                        <li data-id="demo-1" data-url="https://jobs.example/demo-1">
                            <h2>Senior Platform Engineer</h2>
                            <span class="company">Example Corp</span>
                            <span class="location">Remote - North America</span>
                        </li>
                        <li data-id="demo-2" data-url="https://jobs.example/demo-2">
                            <h2>Product Designer</h2>
                            <span class="company">Example Corp</span>
                            <span class="location">Austin, TX</span>
                        </li>
                    </ul>
                </body>
            </html>
        """

    async def scrape(self, playwright: Playwright) -> AsyncIterator[NormalizedJob]:
        browser_type = getattr(playwright, self.context.browser_name)
        browser = await browser_type.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(f"data:text/html,{self._html_document}")
            listings = await page.eval_on_selector_all(
                "#jobs li",
                "els => els.map(el => ({\n"
                "    id: el.getAttribute('data-id'),\n"
                "    url: el.getAttribute('data-url'),\n"
                "    title: el.querySelector('h2')?.textContent?.trim(),\n"
                "    company: el.querySelector('.company')?.textContent?.trim(),\n"
                "    location: el.querySelector('.location')?.textContent?.trim(),\n"
                "}))",
            )
            now = datetime.now(timezone.utc)
            for listing in listings:
                yield NormalizedJob(
                    external_id=listing["id"],
                    title=listing["title"],
                    company=listing["company"],
                    description="Demo listing generated for integration tests.",
                    source_url=listing["url"],
                    location=listing["location"],
                    remote="Remote" in (listing.get("location") or ""),
                    employment_type="full_time",
                    scraped_at=now,
                    metadata={"demo": True},
                )
        finally:
            await page.close()
            await browser.close()

