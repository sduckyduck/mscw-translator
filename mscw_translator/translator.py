from __future__ import annotations

import os
import re
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

    def _built_in_translate(self, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text.strip().lower())

        phrase_map = {
            "hi": "嗨。",
            "hello": "你好。",
            "hey": "嘿。",
            "hi any luck?": "嗨，有进展吗？/ 有消息了吗？",
            "any luck?": "有进展吗？/ 有消息了吗？",
            "any luck": "有进展吗？/ 有消息了吗？",
            "still there?": "还在吗？",
            "u there?": "你还在吗？",
            "you there?": "你还在吗？",
            "brb": "马上回来。",
            "afk": "暂时离开。",
            "ty": "谢谢。",
            "thx": "谢谢。",
            "thanks": "谢谢。",
            "np": "没问题。",
            "nvm": "没事，别在意。",
            "invite me": "请拉我进队。",
            "inv me": "请拉我进队。",
            "party full": "队伍满了。",
            "cc plz": "请换频道/请让图。",
            "how much?": "多少钱？",
            "price?": "价格多少？",
            "offer?": "你出价多少？",
            "sold": "已经卖了。",
        }

        if normalized in phrase_map:
            return phrase_map[normalized]

        patterns = [
            (r"^lf>\s*(.+)", "正在寻找：{x}"),
            (r"^l>\s*(.+)", "正在寻找：{x}"),
            (r"^r>\s*(.+)", "正在招募：{x}"),
            (r"^s>\s*(.+)", "正在出售：{x}"),
            (r"^b>\s*(.+)", "正在购买：{x}"),
            (r"^t>\s*(.+)", "想交换：{x}"),
            (r"(.+)\s+for\s+(.+)", "用/为了 {y}：{x}"),
        ]
        for pattern, template in patterns:
            match = re.search(pattern, normalized)
            if match:
                if len(match.groups()) == 1:
                    return template.format(x=match.group(1))
                return template.format(x=match.group(1), y=match.group(2))

        return "内置简易模式无法完整翻译这句话，但可以结合下方术语提示理解。"

    def _fallback(self, text: str, glossary_note: str, error: str = "") -> str:
        built_in = self._built_in_translate(text)
        lines = [
            "【中文意思】",
            built_in,
            "",
            "【说明】",
            "当前没有连接 Ollama，也没有使用外部翻译 API；这是程序内置的简易规则翻译。",
            "想要更自然的 AI 翻译，需要安装本地模型，例如 Ollama + qwen2.5:3b。",
            "",
            "【识别原文】",
            text,
        ]
        if glossary_note:
            lines.extend(["", "【术语提示】", glossary_note])
        if error:
            lines.extend(["", "【状态信息】", error])
        return "\n".join(lines)
