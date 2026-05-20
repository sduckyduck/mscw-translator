from __future__ import annotations


class ReplyService:
    def suggest(self, text: str) -> list[tuple[str, str]]:
        lowered = text.lower()
        replies: list[tuple[str, str]] = []

        if any(token in lowered for token in ["lf>", "l>", "r>", "party", "pt", "cpq", "kpq", "lpq"]):
            replies.extend([
                ("愿意加入", "Sure, invite me please!"),
                ("稍等一下", "One sec, I can join soon."),
                ("队伍满了", "Sorry, our party is full."),
            ])

        if any(token in lowered for token in ["s>", "b>", "offer", "c/o", "a/w", "sold", "price"]):
            replies.extend([
                ("询问价格", "How much are you looking for?"),
                ("给出报价", "Can you do a little lower?"),
                ("确认购买", "Deal, I can buy it now."),
            ])

        if any(token in lowered for token in ["cc", "map", "ks", "train", "grind"]):
            replies.extend([
                ("礼貌回应", "No problem, I will change channel."),
                ("请求组队", "Can we share the map or party up?"),
                ("说明情况", "Sorry, I did not notice you were here."),
            ])

        if not replies:
            replies.extend([
                ("通用同意", "Sure, sounds good."),
                ("通用拒绝", "Sorry, I cannot right now."),
                ("通用稍等", "One moment please."),
            ])

        seen = set()
        unique: list[tuple[str, str]] = []
        for label, reply in replies:
            if reply not in seen:
                unique.append((label, reply))
                seen.add(reply)
        return unique[:6]
