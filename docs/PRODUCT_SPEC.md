# MSCW Translator Product Spec

## Goal

Build a lightweight Windows desktop companion for MapleStory Classic World players who need to understand English chat quickly and reply naturally.

## MVP workflow

### Workflow A: manual paste

1. Player copies or types English text into the app.
2. App detects MapleStory terms.
3. App shows Chinese explanation and quick English replies.
4. Player copies a reply and pastes it manually into the game.

### Workflow B: screen OCR button

1. Player keeps game in windowed or borderless windowed mode.
2. Player opens this app and presses Capture chat area + OCR.
3. App captures the lower-left screen region.
4. App OCRs the image and fills the source box.
5. App shows terms, translation, and replies.

### Workflow C: future hotkey

A global hotkey can trigger the same capture workflow. This should remain screen-read only and should not inject into the game process.

## Feature modules

### OCR

- Default backend: PaddleOCR.
- Input: screenshot image.
- Output: text lines.
- Fallback: manual text paste.

### Glossary

Local JSON glossary for:

- Server status.
- Trade terms.
- Casual chat abbreviations.
- Scrolls and equipment terms.
- Jobs.
- Skills and buffs.
- Hunting, maps, channels, party quests.

### Translation

- Current MVP: local explanatory mode plus optional DeepL API key.
- Future: LLM provider with prompt context.

Suggested translation prompt for future LLM mode:

```text
You are translating MapleStory Classic World chat. Preserve game abbreviations when useful. Explain slang in Chinese. Keep trade prices and item names exact.
```

### Quick replies

Template categories:

- Party request.
- Trade negotiation.
- Channel/map interaction.
- General agreement/refusal/wait.

## Non-goals

The app should not:

- Read game memory.
- Modify game files.
- Inject overlays into the game process.
- Send packets.
- Auto-play or farm.
- Automatically type or spam messages in-game.

## Recommended next build steps

1. Add a region selector so the player can drag-select the chat box.
2. Save settings to a local config file.
3. Add a real translation provider setting page.
4. Add a term editor so users can expand the glossary.
5. Package with PyInstaller.
