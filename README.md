# MSCW Translator

A Windows desktop helper for MapleStory Classic World players who need fast English/Chinese chat understanding.

The MVP is designed around a conservative rule:

**screen-read only, no game memory access, no DLL injection, no packet inspection, no auto-playing.**

It captures the visible screen or a selected region, runs OCR, applies a MapleStory glossary, translates the text, and provides safe one-click copy replies.

## Core MVP features

- Floating PyQt6 desktop window.
- Global hotkey capture workflow.
- Alt+Tab / window-focus capture workflow.
- OCR service wrapper, prepared for PaddleOCR.
- MapleStory glossary replacement for common terms such as LF, R>, S>, B>, HS, HB, Zak, KPQ, LPQ, GFA, WS, CS, NL, DK, Bishop, and more.
- Quick reply suggestions for party, trade, server, and casual chat.
- Clipboard copy for replies.
- Safety guardrails: no memory reading, no automatic typing into the game client.

## Why this exists

Normal translators often fail on MapleStory slang. For example:

- `LF> bishop for cpq` means looking for a Bishop for a party quest context.
- `S> 10 att WG 500m` means selling 10 weapon attack Work Gloves for 500 million mesos.
- `cc plz` means please change channel.

This app adds a game-specific glossary layer before translation/reply generation.

## Install locally

Use Windows PowerShell:

```powershell
git clone https://github.com/sduckyduck/mscw-translator.git
cd mscw-translator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m mscw_translator
```

PaddleOCR is listed as an optional OCR backend. The app still launches without it, but real OCR requires installing its dependencies correctly.

## Recommended safe usage

Use the game in **windowed** or **borderless windowed** mode. Exclusive full screen may hide the game from normal screenshot APIs after Alt+Tab.

Suggested workflow:

1. See English chat in game.
2. Press the configured hotkey, or Alt+Tab into this app.
3. App captures the screen/region and OCRs the chat.
4. App shows original text, glossary-aware explanation, and Chinese translation.
5. Choose a reply and copy it.
6. Return to the game and paste manually.

## Anti-cheat note

This project intentionally avoids memory access, packet hooks, input automation, and overlays injected into the game process. That reduces risk, but no third-party helper can guarantee acceptance under every game's terms or anti-cheat behavior. Keep it screen-read only and manual-paste only.

## Project structure

```text
mscw-translator/
  mscw_translator/
    app.py
    capture.py
    glossary.py
    hotkeys.py
    ocr.py
    replies.py
    translator.py
    ui.py
    utils.py
    data/glossary.zh-CN.json
  docs/
    PRODUCT_SPEC.md
    SAFETY_AND_ANTICHEAT.md
  requirements.txt
```

## Next milestones

- Add region selector for chat box.
- Add local cache of OCR results.
- Add DeepL or LLM translation provider.
- Add MapleStory quest text database search.
- Add packaged Windows EXE via PyInstaller.
