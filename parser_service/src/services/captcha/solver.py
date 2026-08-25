import asyncio
import random
import re

from nodriver import Element, Tab
from nodriver.core.tab import cdp

from .images import CaptchaImageLoader
from .models import (
    CAPTCHA_TEXTS,
    MAX_DRAG_ITERATIONS,
    CaptchaPosition,
    CaptchaSolveError,
)
from .puzzle_solver import PuzzleSolver


class OzonCaptchaSolver:
    def __init__(self, session):
        self.session = session
        self._image_loader = CaptchaImageLoader(session)

    async def solve_from_elements(
        self, image: Element, puzzle: Element, visualize: bool = False
    ) -> int:
        image_url = image.attrs.get("src")
        puzzle_url = puzzle.attrs.get("src")

        if not image_url or not puzzle_url:
            raise CaptchaSolveError("image_url or puzzle_url is None")

        image_np, puzzle_np = await self.load_images(
            image_url=image_url,
            puzzle_url=puzzle_url,
        )

        style = puzzle.attrs.get("style")
        if not style:
            raise CaptchaSolveError("style is None")
        position = PuzzleSolver.parse_position(style)

        return self.solve(
            captcha_img=image_np,
            puzzle_img=puzzle_np,
            initial_left=position.left,
            initial_top=position.top,
            visualize=visualize,
        )

    async def load_images(
        self, image_url: str, puzzle_url: str
    ) -> tuple:
        return await self._image_loader.load_images(image_url, puzzle_url)

    def parse_position(self, style: str) -> CaptchaPosition:
        return PuzzleSolver.parse_position(style)

    def solve(
        self,
        captcha_img,
        puzzle_img,
        initial_left: int,
        initial_top: int,
        visualize: bool = False,
    ) -> int:
        return PuzzleSolver.solve(
            captcha_img=captcha_img,
            puzzle_img=puzzle_img,
            initial_left=initial_left,
            initial_top=initial_top,
            visualize=visualize,
        )

    async def solve_captcha(self, page: Tab, max_attempts: int) -> None:
        for _ in range(max_attempts):
            if not await self.is_captcha(page):
                return
            await self._solve_attempt(page)
            if not await self.is_captcha(page):
                return
        raise CaptchaSolveError(f"Failed to solve captcha in {max_attempts} attempts")

    async def is_captcha(self, page: Tab) -> bool:
        for text in CAPTCHA_TEXTS:
            element = await page.find_element_by_text(text)
            if element is not None:
                return True
        return False

    async def get_captcha_elements(self, page: Tab) -> tuple[Element, Element]:
        captcha = await page.select("#captcha")

        if not isinstance(captcha, Element):
            raise CaptchaSolveError("Captcha element not found")

        image = await captcha.query_selector("#image")
        puzzle = await captcha.query_selector("#puzzle")

        if not isinstance(image, Element) or not isinstance(puzzle, Element):
            raise CaptchaSolveError("Captcha or puzzle element not found")
        return image, puzzle

    async def drag_slider(
        self, tab: Tab, slider_element: Element, distance_x: float, steps: int = 30
    ) -> tuple[int, int]:
        pos = await slider_element.get_position()
        start_x = pos.center[0]
        start_y = pos.center[1]

        await tab.send(
            cdp.input_.dispatch_mouse_event(
                type_="mousePressed",
                x=start_x,
                y=start_y,
                button=cdp.input_.MouseButton("left"),
                buttons=1,
                click_count=1,
            )
        )
        await asyncio.sleep(random.uniform(0.05, 0.15))

        current_x = start_x
        for i in range(1, steps + 1):
            progress = i / steps
            eased = 1 - (1 - progress) ** 2  # ease-out
            target_x = start_x + distance_x * eased
            jitter_y = start_y + random.uniform(-1.5, 1.5)

            await tab.send(
                cdp.input_.dispatch_mouse_event(
                    type_="mouseMoved",
                    x=target_x,
                    y=jitter_y,
                    button=cdp.input_.MouseButton("left"),
                    buttons=1,
                )
            )
            current_x = target_x
            await asyncio.sleep(random.uniform(0.01, 0.03))

        return current_x, start_y

    async def _release_slider(self, page: Tab, x: float, y: float) -> None:
        await page.send(
            cdp.input_.dispatch_mouse_event(
                type_="mouseReleased",
                x=x,
                y=y,
                button=cdp.input_.MouseButton("left"),
                buttons=0,
            )
        )

    async def _read_puzzle_left(self, puzzle: Element) -> int:
        attrs = await puzzle.get_js_attributes()
        left = str(attrs["style"]["left"])

        match = re.search(r"-?\d+(?:\.\d+)?", left)
        if match is None:
            raise CaptchaSolveError(f"Match of left is None. Left: {left}")
        return round(float(match.group()))

    async def _solve_attempt(self, page: Tab) -> None:
        image, puzzle = await self.get_captcha_elements(page)
        target_left = await self.solve_from_elements(image, puzzle)

        slider = await page.select("#slider")

        if not isinstance(slider, Element):
            raise CaptchaSolveError("Slider element is None")

        left_puzzle = await self._read_puzzle_left(puzzle)

        x, y = 0.0, 0.0
        drags = 0
        while left_puzzle < target_left and drags < MAX_DRAG_ITERATIONS:
            x, y = await self.drag_slider(page, slider, 10, 1)
            left_puzzle = await self._read_puzzle_left(puzzle)
            drags += 1

        await self._release_slider(page, x, y)
        await page.sleep(2)
