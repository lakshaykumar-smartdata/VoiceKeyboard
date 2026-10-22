# VoiceKeyboard

System-wide speech-to-text for Windows. Works in any app, like a keyboard (Notepad, Teams, browser…).
Understands English, Hindi and Hinglish; Hindi is typed in Roman letters ("main ghar jaa rahaa hun").

## Setup

```
pip install -r requirements.txt
```

## Use

1. Run `run.bat` and minimise the console window.
2. Click into any text box.
3. Hold **Right Ctrl**, speak, release. The text is typed where the cursor is.

## Notes

- Uses Google speech recognition (`en-IN` + `hi-IN`, most confident wins), so it needs internet.
- To type into apps running as administrator, run `run.bat` as administrator.
- Settings (hotkey, languages) are at the top of `dictate.py`.
