# Safety and Anti-Cheat Notes

This project is designed as a conservative screen-reading translator.

## Allowed design principles

- Capture only visible pixels from the user's own screen.
- Run OCR on screenshots.
- Translate recognized text.
- Provide reply suggestions.
- Copy selected replies to clipboard.
- Require the user to paste manually.

## Avoided behaviors

Do not add features that:

- Read or scan game memory.
- Hook the game process.
- Inject DLLs.
- Inspect network packets.
- Modify client files.
- Automatically move, attack, loot, or farm.
- Automatically send chat messages without user review.

## Fullscreen behavior

Exclusive full screen may block or blank normal screenshots after focus changes. For the best experience, recommend:

1. Windowed mode.
2. Borderless windowed mode.
3. Manual paste fallback if exclusive full screen does not capture correctly.

## Alt+Tab trigger concept

The focus-change workflow is technically feasible, but it should be treated as a convenience trigger only. The app should not interact with the game process. It should simply respond when its own window becomes active, then capture visible screen pixels.

## Practical recommendation

The safest MVP is:

- No global keyboard listener at first.
- No automatic typing.
- No overlay injected into the game.
- Button-based capture plus manual clipboard paste.

After that works, add optional hotkeys carefully and make them user-configurable.
