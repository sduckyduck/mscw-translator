from __future__ import annotations

import os
import requests


class TranslatorService:
    def __init__(self) -> None:
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate").strip()
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b").strip()
        self.deepl_key = os.getenv("DEEPL_API_KEY", "").strip()

    def translate_to_chinese(self, text: str, glossary_note: str = "") -> str:
        if not text.strip():
            return ""

        # Priority 1: fully local open-weight model through Ollama.
        try:
            return self._translate_with_ollama(text, glossary_note)
        except Exception as ollama_error:
            # Priority 2: optional external API only if user configured it.
            if self.deepl_key:
                try:
                    return self._translate_with_deepl(text)
                except Exception as deepl_error:
                    return self._fallback(
                        text,
                        glossary_note,
                        error="Ollama 本地模型不可用：" + str(ollama_error) + "\nDeepL 也不可用：" + str(deepl_error),
                    )
            return self._fallback(text, glossary_note, error="Ollama 本地模型不可用：" + str(ollama_error))

    def _translate_with_ollama(self, text: str, glossary_note: str = "") -> str:
        prompt = self._build_game_translation_prompt(text, glossary_note)
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }
        response = requests.post(self.ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()
        if not answer:
            raise RuntimeError("Ollama 返回为空。")
        return answer

    def _build_game_translation_prompt(self, text: str, glossary_note: str = "") -> str:
        return (
            "你是冒险岛 MapleStory Classic World 的中英聊天翻译助手。\n"
            "任务：把玩家英文聊天翻译成自然中文，并解释游戏缩写。\n"
            "要求：\n"
            "1. 保留价格、数字、道具名、职业名和缩写。\n"
            "2. 对 LF、R>、S>、B>、CPQ、KPQ、LPQ、HS、HB、SE 等术语要按冒险岛语境解释。\n"
            "3. 输出格式必须简洁：\n"
            "【中文意思】\n"
            "一句自然中文翻译。\n\n"
            "【术语解释】\n"
            "列出命中的游戏术语。\n\n"
            "【推荐回复】\n"
            "给 3 条地道英文回复。\n\n"
            "本地词库提示：\n"
            + (glossary_note or "无")
            + "\n\n玩家原文：\n"
            + text
        )

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
        lines = [
            "本地解释模式：还没有连接到 Ollama 本地大语言模型。",
            "",
            "解决方法：安装 Ollama，并运行：ollama run qwen2.5:3b",
            "",
            "识别原文：",
            text,
        ]
        if glossary_note:
            lines.extend(["", "术语提示：", glossary_note])
        if error:
            lines.extend(["", "状态信息：", error])
        return "\n".join(lines)
