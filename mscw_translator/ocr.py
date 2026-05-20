from __future__ import annotations

from PIL import Image


class OCRService:
    def __init__(self) -> None:
        self.reader = None
        self.error_message = ""
        try:
            from paddleocr import PaddleOCR
            self.reader = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        except Exception as exc:
            self.error_message = str(exc)

    @property
    def available(self) -> bool:
        return self.reader is not None

    def read_image(self, image: Image.Image) -> str:
        if self.reader is None:
            return ""
        result = self.reader.ocr(image, cls=True)
        lines: list[str] = []
        for page in result or []:
            for row in page or []:
                if len(row) >= 2 and row[1]:
                    text = row[1][0]
                    if text:
                        lines.append(str(text))
        return "\n".join(lines).strip()
