import cv2
import numpy as np
from aiohttp import ClientResponseError
from aiohttp.client import ClientSession

from .models import CaptchaSolveError


class CaptchaImageLoader:
    def __init__(self, session: ClientSession):
        self.session = session

    async def load_images(
        self, image_url: str, puzzle_url: str
    ) -> tuple[np.ndarray, np.ndarray]:
        image_bytes = await self._image_bytes(image_url)
        puzzle_bytes = await self._image_bytes(puzzle_url)

        image_np = self._to_np_array(image_bytes)
        puzzle_np = self._to_np_array(puzzle_bytes)

        return image_np, puzzle_np

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

    @staticmethod
    def _to_np_array(image_bytes: bytes) -> np.ndarray:
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
