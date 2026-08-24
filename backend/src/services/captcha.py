import asyncio
import random
import re

from aiohttp import ClientResponseError
from aiohttp.client import ClientSession
import cv2
from nodriver import Element, Tab
from nodriver.core.tab import cdp
import numpy as np

from pydantic import BaseModel


CAPTCHA_TEXTS = (
    "Подтвердите, что вы не бот",
    "Подтвердите, что Вы не бот",
    "Сопоставьте пазл",
    "передвигая ползунок",
)

MAX_DRAG_ITERATIONS = 50


class CaptchaPosition(BaseModel):
    top: int
    left: int


class CaptchaSolveError(RuntimeError):
    pass


class OzonCaptchaSolver:
    def __init__(self, session: ClientSession):
        self.session = session

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
        position = self.parse_position(style)

        return self.solve(
            captcha_img=image_np,
            puzzle_img=puzzle_np,
            initial_left=position.left,
            initial_top=position.top,
            visualize=visualize,
        )

    async def _image_bytes(self, url: str) -> bytes:
        async with self.session.get(url) as response:
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                raise CaptchaSolveError(
                    f"Captcha image fetch failed: HTTP {e.status} {e.message}; "
                    f"url={e.request_info.real_url}"
                ) from e
            image_bytes = await response.read()
            return image_bytes

    async def load_images(
        self, image_url: str, puzzle_url: str
    ) -> tuple[np.ndarray, np.ndarray]:
        image_bytes = await self._image_bytes(image_url)
        puzzle_bytes = await self._image_bytes(puzzle_url)

        image_np = self._to_np_array(image_bytes)
        puzzle_np = self._to_np_array(puzzle_bytes)

        return image_np, puzzle_np

    def parse_position(self, style: str) -> CaptchaPosition:
        top = self._parse_px(style, "top")
        left = self._parse_px(style, "left")

        return CaptchaPosition(
            top=top,
            left=left,
        )

    def _parse_px(self, style: str, property_name: str) -> int:
        match = re.search(
            rf"{property_name}:\s*(-?\d+)px",
            style,
        )

        return int(match.group(1)) if match else 0

    def _to_np_array(self, image_bytes: bytes) -> np.ndarray:
        """
        Converts image bytes to an OpenCV image (BGR or BGRA).

        :param image_bytes: Image data in bytes
        :return: OpenCV BGR/BGRA image as a NumPy array
        """
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise CaptchaSolveError("Failed to decode image bytes.")
        return img

    def solve(
        self,
        captcha_img: np.ndarray,
        puzzle_img: np.ndarray,
        initial_left: int,
        initial_top: int,
        visualize: bool = False,
    ) -> int:
        """
        Calculates horizontal position (puzzle_target_x) required to match puzzle piece with captcha hole.

        :param captcha_img: OpenCV BGR image of the full captcha frame
        :param puzzle_img: OpenCV BGR or BGRA image of the puzzle piece overlay
        :param initial_left: Initial X coordinate (left) from CSS style
        :param initial_top: Initial Y coordinate (top) from CSS style
        :param visualize: If True, opens a window displaying the solution with bounding boxes, original puzzle, and delta info
        :return: Matched puzzle target X position in pixels on background image
        """
        # Ensure BGR captcha grayscale
        if captcha_img.ndim == 3 and captcha_img.shape[2] == 4:
            bg_gray = cv2.cvtColor(captcha_img[:, :, :3], cv2.COLOR_BGR2GRAY)
        elif captcha_img.ndim == 3:
            bg_gray = cv2.cvtColor(captcha_img, cv2.COLOR_BGR2GRAY)
        else:
            bg_gray = captcha_img

        # Process puzzle piece image (grayscale + alpha channel)
        if puzzle_img.ndim == 3 and puzzle_img.shape[2] == 4:
            pz_gray = cv2.cvtColor(puzzle_img[:, :, :3], cv2.COLOR_BGR2GRAY)
            alpha = puzzle_img[:, :, 3]
        elif puzzle_img.ndim == 3:
            pz_gray = cv2.cvtColor(puzzle_img, cv2.COLOR_BGR2GRAY)
            alpha = np.ones(puzzle_img.shape[:2], dtype=np.uint8) * 255
        else:
            pz_gray = puzzle_img
            alpha = np.ones(puzzle_img.shape[:2], dtype=np.uint8) * 255

        # Crop puzzle piece to its tight alpha bounding box
        ys, xs = np.where(alpha > 0)
        if len(xs) == 0 or len(ys) == 0:
            raise CaptchaSolveError("Puzzle image alpha channel has no valid content.")

        min_x_in_pz = xs.min()
        crop_pz_gray = pz_gray[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
        crop_alpha = alpha[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]

        # Extract edges using Canny
        bg_edges = cv2.Canny(bg_gray, 50, 150)
        pz_edges = cv2.Canny(crop_pz_gray, 50, 150)
        pz_edges[crop_alpha == 0] = 0

        h_crop, _ = pz_edges.shape

        # Search band in Y row around initial_top
        if initial_top is not None and initial_top + h_crop <= bg_edges.shape[0]:
            search_region = bg_edges[initial_top : initial_top + h_crop, :]
            res = cv2.matchTemplate(search_region, pz_edges, cv2.TM_CCOEFF_NORMED)
            _, _, _, max_loc = cv2.minMaxLoc(res)
            matched_x = max_loc[0]
        else:
            res = cv2.matchTemplate(bg_edges, pz_edges, cv2.TM_CCOEFF_NORMED)
            _, _, _, max_loc = cv2.minMaxLoc(res)
            matched_x = max_loc[0]

        puzzle_target_x = int(matched_x - min_x_in_pz)

        if visualize:
            vis = (
                captcha_img[:, :, :3].copy()
                if captcha_img.ndim == 3
                else cv2.cvtColor(captcha_img, cv2.COLOR_GRAY2BGR)
            )
            w_crop = crop_pz_gray.shape[1]

            # Initial position (yellow)
            cv2.rectangle(
                vis,
                (initial_left, initial_top),
                (initial_left + w_crop, initial_top + h_crop),
                (0, 255, 255),
                1,
            )

            # Solved target position (green)
            cv2.rectangle(
                vis,
                (puzzle_target_x, initial_top),
                (puzzle_target_x + w_crop, initial_top + h_crop),
                (0, 255, 0),
                2,
            )

            info_str = f"puzzle_target_x: {puzzle_target_x}px"
            cv2.putText(
                vis, info_str, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

            cv2.imshow("Ozon Captcha Solution", vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return puzzle_target_x

    async def solve_captcha(self, page: Tab, max_attempts: int = 3) -> None:
        # raise CaptchaSolveError(f"Failed to solve captcha in {max_attempts} attempts")

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

        # 1. Зажимаем — mousePressed, БЕЗ mouseReleased
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

        # 2. Двигаем мышь пошагово, кнопка всё ещё "зажата" (buttons=1)
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
