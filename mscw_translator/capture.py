from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image
import mss


@dataclass
class CaptureRegion:
    left: int
    top: int
    width: int
    height: int

    def to_mss(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


class ScreenCaptureService:
    def capture_primary_monitor(self) -> Image.Image:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            shot = sct.grab(monitor)
            return Image.frombytes("RGB", shot.size, shot.rgb)

    def capture_region(self, region: CaptureRegion) -> Image.Image:
        with mss.mss() as sct:
            shot = sct.grab(region.to_mss())
            return Image.frombytes("RGB", shot.size, shot.rgb)

    def capture_default_chat_area(self) -> Image.Image:
        """Capture a conservative bottom-left area where MMO chat boxes often sit.

        This is only a starter default. The next version should include a visual
        region selector and save the user's preferred chat rectangle.
        """
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            width = int(monitor["width"] * 0.55)
            height = int(monitor["height"] * 0.28)
            left = monitor["left"]
            top = monitor["top"] + monitor["height"] - height
            shot = sct.grab({"left": left, "top": top, "width": width, "height": height})
            return Image.frombytes("RGB", shot.size, shot.rgb)
