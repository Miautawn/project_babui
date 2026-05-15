import asyncio
import math
import random
from dataclasses import dataclass

from playwright.async_api import Page


@dataclass
class MouseState:
    x: float
    y: float


async def wait_and_do_something(
    page: Page, viewport: dict[str, int], mouse_state: MouseState
):
    try:
        async with asyncio.timeout(random.uniform(5, 120)):
            while True:
                tasks = []
                if random.random() < 0.5:
                    tasks.append(human_mouse_wiggle(page, viewport, mouse_state))
                if random.random() < 0.3:
                    tasks.append(human_random_scroll(page))
                tasks.append(asyncio.sleep(random.uniform(0.5, 1.5)))
                await asyncio.gather(*tasks)
    except TimeoutError:
        return


async def get_viewport_dimensions(page: Page) -> dict[str, int]:
    """Gets the current viewport dimensions."""
    dimensions = await page.evaluate(
        """() => {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        }"""
    )
    return dimensions


async def human_random_scroll(
    page: Page,
    min_distance: int = 500,
    max_distance: int = 2000,
    allow_horizontal: bool = False,
):
    """
    Human-like random scrolling behavior.

    Features:
    - variable scroll distance
    - acceleration/deceleration
    - wheel burst scrolling
    - tiny hesitation pauses
    - occasional reverse correction
    - optional horizontal drift
    """

    # Direction preference (humans usually continue current direction)
    direction = random.choice([1, 1, 1, -1, -1, -1, -1])

    total_distance = random.randint(min_distance, max_distance)
    total_distance *= direction

    # Humans scroll in bursts
    bursts = random.randint(3, 8)

    remaining = total_distance

    for burst in range(bursts):
        if abs(remaining) <= 5:
            break

        # Portion of remaining distance
        burst_distance = remaining / (bursts - burst)

        # Add randomness
        burst_distance *= random.uniform(0.7, 1.3)

        # Number of wheel events
        steps = random.randint(5, 20)

        for i in range(steps):
            t = i / max(steps - 1, 1)

            # Ease curve
            eased = 0.5 - 0.5 * math.cos(math.pi * t)

            delta_y = burst_distance / steps

            # Speed modulation
            delta_y *= 0.5 + eased

            # Small hand inconsistency
            delta_y *= random.uniform(0.8, 1.2)

            # Tiny horizontal wobble
            if allow_horizontal:
                delta_x = random.uniform(-2, 2)
            else:
                delta_x = 0

            await page.mouse.wheel(
                delta_x=delta_x,
                delta_y=delta_y,
            )

            # Human timing variation
            await asyncio.sleep(random.uniform(0.01, 0.06))

        remaining -= burst_distance

        # Tiny reading pause
        if random.random() < 0.7:
            await asyncio.sleep(random.uniform(0.1, 1.2))

    # Occasional small correction scroll
    if random.random() < 0.35:
        correction = random.randint(20, 120)

        # Usually opposite direction
        correction *= -1 if direction == 1 else 1

        correction_steps = random.randint(2, 6)

        for _ in range(correction_steps):
            await page.mouse.wheel(
                delta_x=0,
                delta_y=correction / correction_steps,
            )

            await asyncio.sleep(random.uniform(0.02, 0.08))


async def human_mouse_wiggle(
    page: Page,
    viewport: dict[str, int],
    mouse_state: MouseState,
):
    width = viewport["width"]
    height = viewport["height"]

    start_x = mouse_state.x
    start_y = mouse_state.y

    # New target
    end_x = random.randint(50, width - 50)
    end_y = random.randint(50, height - 50)

    # Optional overshoot
    overshoot = random.random() < 0.35

    if overshoot:
        target_x = end_x + random.randint(-25, 25)
        target_y = end_y + random.randint(-25, 25)
    else:
        target_x = end_x
        target_y = end_y

    distance = math.hypot(target_x - start_x, target_y - start_y)
    steps = max(20, min(int(distance / 7), 120))

    # Bezier controls
    cp1_x = start_x + (target_x - start_x) * random.uniform(0.2, 0.4)
    cp1_y = start_y + (target_y - start_y) * random.uniform(0.0, 1.0)

    cp2_x = start_x + (target_x - start_x) * random.uniform(0.6, 0.9)
    cp2_y = start_y + (target_y - start_y) * random.uniform(0.0, 1.0)

    def bezier(t, p0, p1, p2, p3):
        return (
            (1 - t) ** 3 * p0
            + 3 * (1 - t) ** 2 * t * p1
            + 3 * (1 - t) * t**2 * p2
            + t**3 * p3
        )

    for i in range(steps):
        t = i / (steps - 1)

        # ease in/out
        eased = 0.5 - 0.5 * math.cos(math.pi * t)

        x = bezier(
            eased,
            start_x,
            cp1_x,
            cp2_x,
            target_x,
        )

        y = bezier(
            eased,
            start_y,
            cp1_y,
            cp2_y,
            target_y,
        )

        # subtle jitter
        jitter = (1 - t) * 2

        x += random.uniform(-jitter, jitter)
        y += random.uniform(-jitter, jitter)

        await page.mouse.move(x, y)

        # IMPORTANT:
        # update tracked mouse position
        mouse_state.x = x
        mouse_state.y = y

        await asyncio.sleep(random.uniform(0.004, 0.015))

    # Overshoot correction
    if overshoot:
        correction_steps = random.randint(6, 15)

        sx = mouse_state.x
        sy = mouse_state.y

        for i in range(correction_steps):
            t = (i + 1) / correction_steps

            x = sx + (end_x - sx) * t
            y = sy + (end_y - sy) * t

            x += random.uniform(-0.5, 0.5)
            y += random.uniform(-0.5, 0.5)

            await page.mouse.move(x, y)

            mouse_state.x = x
            mouse_state.y = y

            await asyncio.sleep(random.uniform(0.005, 0.02))
