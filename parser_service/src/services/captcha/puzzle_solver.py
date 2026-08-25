import re

import cv2
import numpy as np

from .models import CaptchaPosition, CaptchaSolveError


class PuzzleSolver:
    """Pure computer-vision logic for matching a puzzle piece to the captcha hole."""

    @staticmethod
    def parse_position(style: str) -> CaptchaPosition:
        top = PuzzleSolver._parse_px(style, "top")
        left = PuzzleSolver._parse_px(style, "left")

        return CaptchaPosition(
            top=top,
            left=left,
        )

    @staticmethod
    def _parse_px(style: str, property_name: str) -> int:
        match = re.search(
            rf"{property_name}:\s*(-?\d+)px",
            style,
        )

        return int(match.group(1)) if match else 0

    @staticmethod
    def solve(
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
