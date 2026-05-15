from typing import Optional

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Locator, Page

SEARCH_LISTING_DIV_SELECTOR = "div.list-item-content"


async def search_get_listing_ids(page: Page) -> list[str]:
    js_code = f"""
    () => {{
        return Array.from(document.querySelectorAll('{SEARCH_LISTING_DIV_SELECTOR}'))
            .map(el => {{
                const link = el.querySelector('a[href*="/details/"]');
                return link ? link.getAttribute('href').split('/details/')[1] : null;
            }})
            .filter(href => href !== null);
    }}
    """
    listing_urls = await page.evaluate(js_code)
    return listing_urls if listing_urls else []


async def find_candidate_listing(
    page: Page, blacklist: set[str]
) -> Optional[tuple[str, Locator]]:
    try:
        first_room = page.locator(SEARCH_LISTING_DIV_SELECTOR).first
        await first_room.wait_for(state="visible", timeout=5 * 1000)
    except PlaywrightError:
        return None, None

    listing_ids = await search_get_listing_ids(page)
    if len(listing_ids) == 0:
        return None, None

    candidates_ids = [id for id in listing_ids if id not in blacklist]
    if len(candidates_ids) == 0:
        return None, None

    candidate_id = candidates_ids[0]
    candidate_locator = (
        page.locator(f"div.list-item-content a[href*='/details/{candidate_id}']")
        .first.locator("div.object-tile-header")
        .first
    )

    return candidate_id, candidate_locator
