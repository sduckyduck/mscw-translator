from __future__ import annotations

import os
import requests


class TranslatorService:
    def __init__(self) -> None:
        self.deepl_key = os.getenv("DEEPL_API_KEY", "").strip()

    def translate_to_chinese(self, text: str, glossary_note: str = "") -> str:
        if not text.strip():
            return ""
        if self.deepl_key:
            try:
                return self._translate_with_deepl(text)
            except Exception as exc:
                return self._fallback(text, glossary_note, error=str(exc))
        return self._fallback(text, glossary_note)

    def _translate_with_deepl(self, text: str) -> str:
        url = "https://api-free.deepl.com/v2/translate"
        response = requests.post(
            url,
            data={"auth_key": self.deepl_key, "text": text, "target_lang": "ZH"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data["translations"][0]["text"]

    @staticmethod
    def _fallback(text: str, glossary_note: str, error: str = "") -> str:
        lines = ["本地演示翻译模式：还没有配置真实翻译 API。", "", "识别原文：", text]
        if glossary_note:
            lines.extend(["", "术语提示：", glossary_note])
        if error:
            lines.extend(["", "翻译 API 错误：", error])
        return "\n".join(lines)
