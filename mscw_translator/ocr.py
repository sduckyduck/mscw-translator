from __future__ import annotations

from PIL import Image


class OCRService:
    def __init__(self) -> None:
        self.reader = None
        self.backend_name = ""
        self.error_message = ""
        self._init_paddleocr()

    @property
    def available(self) -> bool:
        return self.reader is not None

    def _init_paddleocr(self) -> None:
        try:
            from paddleocr import PaddleOCR

            try:
                self.reader = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            except TypeError:
                try:
                    self.reader = PaddleOCR(use_angle_cls=True, lang="en")
                except TypeError:
                    self.reader = PaddleOCR(lang="en")
            self.backend_name = "PaddleOCR"
        except Exception as exc:
            self.reader = None
            self.error_message = str(exc)

    def read_image(self, image: Image.Image) -> str:
        if self.reader is None:
            return ""

        image = image.convert("RGB")
        try:
            import numpy as np
            image_input = np.array(image)
        except Exception:
            image_input = image

        try:
            result = self.reader.ocr(image_input, cls=True)
        except TypeError:
            result = self.reader.ocr(image_input)

        return self._extract_text(result)

    def _extract_text(self, result) -> str:
        lines: list[str] = []

        if isinstance(result, dict):
            texts = result.get("rec_texts") or result.get("texts") or []
            return "\n".join(str(x) for x in texts if str(x).strip()).strip()

        for page in result or []:
            if isinstance(page, dict):
                texts = page.get("rec_texts") or page.get("texts") or []
                lines.extend(str(x) for x in texts if str(x).strip())
                continue

            for row in page or []:
                try:
                    if len(row) >= 2 and row[1]:
                        item = row[1]
                        if isinstance(item, (list, tuple)) and item:
                            text = item[0]
                        else:
                            text = item
                        if str(text).strip():
                            lines.append(str(text))
                except Exception:
                    continue

        return "\n".join(lines).strip()
