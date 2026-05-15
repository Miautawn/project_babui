import argparse
import asyncio
import datetime
import random
import sys

from humanization import Humanization
from loguru import logger
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

from project_babui.utils.debug import enable_visual_mouse
from project_babui.utils.mimicing import (
    MouseState,
    get_viewport_dimensions,
    wait_and_do_something,
)
from project_babui.utils.scraping import find_candidate_listing
from project_babui.utils.state import StateManager
from project_babui.utils.telegram import TelegramBot, TelegramBotAsync

from . import candidate_threshold, chromium_url, humanization_config, state_file


async def main(args):
    playwright_context = None
    browser = None

    state_manager = StateManager(state_file)
    telegram_bot = TelegramBotAsync()
    try:
        print(f"[💫] Attaching to browser at {chromium_url}...")
        playwright_context = await async_playwright().start()
        browser = await playwright_context.chromium.connect_over_cdp(chromium_url)

        print("[✅] Browser Connected!")
        current_tab = browser.contexts[0].pages[0]
        human_agent = Humanization(current_tab, humanization_config)

        if args.debug:
            await enable_visual_mouse(current_tab)

        viewport = await get_viewport_dimensions(current_tab)
        mouse_state = MouseState(
            random.randint(viewport["width"] // 4, viewport["width"] // 2),
            random.randint(viewport["height"] // 4, viewport["height"] // 2),
        )

        print("[💫] Entering the Babui Playground! Ctrl+C to exit.")

        if not args.debug:
            await telegram_bot.send_message(
                "🚀<b>Babui is ONLINE!</b>🚀\n"
                "I'll be monitoring the listings and alerting you when I find a new candidate."
            )

        while True:
            # Humans sleep at 21:00 - shut down the bot as well
            if 7 > datetime.now().hour >= 24:
                print("[🌙] It's getting late... Shutting down for the night.")
                if not args.debug:
                    await telegram_bot.send_message(
                        "🌙<b>It's after 21:00</b>🌙\nSee you in the morning! ☀️"
                    )
                break

            if len(state_manager.candidates) >= candidate_threshold:
                print("[🎯] Candidate threshold reached! Taking a break...")
                if not args.debug:
                    await telegram_bot.send_message(
                        f"🎯<b>Candidate Threshold Reached:</b>🎯\n"
                        f"We currently have {len(state_manager.candidates)} candidates. Taking a break for now!"
                    )
                break

            candidate_id, candidate_locator = await find_candidate_listing(
                current_tab, state_manager.blacklist
            )

            if candidate_id is None:
                print("[🔍] No new candidates found. Retrying in a bit...")
                await wait_and_do_something(current_tab, viewport, mouse_state)
                await current_tab.reload()
                continue

            await human_agent.scroll_to(candidate_locator)
            await candidate_locator.wait_for(state="visible", timeout=10 * 1000)
            await human_agent.click_at(candidate_locator)

            await current_tab.wait_for_load_state("load", timeout=15 * 1000)

            button_locator = current_tab.locator("input.reageer-button")
            await human_agent.scroll_to(button_locator)
            await button_locator.wait_for(state="visible", timeout=10 * 1000)
            await human_agent.click_at(button_locator)

            if not args.debug:
                asyncio.create_task(
                    telegram_bot.send_message(
                        "🚨<b>Candidate Alert:</b>🚨\nwe subscribed to a new listing!"
                    )
                )
            state_manager.add_to_candidates(candidate_id)
            state_manager.save_state()

            info_popup = current_tab.locator("span.icon-br_kruis.mfp-close")
            await human_agent.human_correct(info_popup, overshoot_factor=1.5)
            await human_agent.click_at(info_popup)

            back_link = current_tab.locator(
                'a[history-link][href="/en/offerings/to-rent"]'
            )
            await human_agent.click_at(back_link)

    except asyncio.CancelledError:
        print("\n[🛑] Async task cancelled. Shutting down...")
        raise
    except PlaywrightError as e:
        print("[❌] Playwright error occurred:", e)
        if not args.debug:
            await telegram_bot.send_message(
                "❌<b>Babui PLAYWRIGHT ERROR:</b>❌\nShutting Down!"
            )
    except Exception as e:
        print("[💥] Something unexpected happened inside application:", e)
        if not args.debug:
            await telegram_bot.send_message(
                "💥<b>Babui APPLICATION ERROR:</b>💥\nShutting Down!"
            )

    finally:
        if browser:
            await browser.close()

        if playwright_context:
            await playwright_context.stop()

        await telegram_bot.close_client()


def start():
    parser = argparse.ArgumentParser(description="Amsterdam Sniper 2026")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable visual mouse tracking and disable telegram debug messages",
    )
    args = parser.parse_args()

    if not args.debug:
        logger.remove()
        logger.add(sys.stderr, level="ERROR")

    telegram_bot = TelegramBot()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("[⌨️] Ctrl+c detected, shutting down...")

    print("[👋] Goodbye from the Babui Playground!")
    if not args.debug:
        telegram_bot.send_message("👋👋 Babui is going offline for now. Bye Bye! 👋👋")

    telegram_bot.close_client()


if __name__ == "__main__":
    start()
