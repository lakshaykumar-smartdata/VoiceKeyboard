"""Hold HOTKEY, speak, release: the text is typed into whatever window has focus."""
import ctypes
import time

import keyboard
import pyaudiowpatch as pyaudio
import speech_recognition as sr

from romanize import romanize

HOTKEY = 0xA3           # hold to talk; Win32 virtual-key code, 0xA3 = Right Ctrl
# Google tries each language and keeps the most confident result, so English,
# Hindi and Hinglish all work. Needs internet.
LANGUAGES = ["en-IN", "hi-IN"]
RATE = 16000
CHUNK = 1024

recognizer = sr.Recognizer()
pa = pyaudio.PyAudio()


def held():
    # Real key state from Windows; keyboard's hook-based is_pressed/wait miss releases.
    return bool(ctypes.windll.user32.GetAsyncKeyState(HOTKEY) & 0x8000)


def record():
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    while held():
        frames.append(stream.read(CHUNK, exception_on_overflow=False))
    stream.close()
    return b"".join(frames)


def transcribe(raw):
    if len(raw) < RATE * 2 * 0.3:  # accidental tap (16-bit samples = 2 bytes each)
        return ""
    audio = sr.AudioData(raw, RATE, 2)
    best, best_conf = "", -1.0
    for lang in LANGUAGES:
        try:
            result = recognizer.recognize_google(audio, language=lang, show_all=True)
        except sr.RequestError as e:
            print(f"[Google error ({lang}): {e}]")
            continue
        if not result or "alternative" not in result:
            continue
        alt = result["alternative"][0]
        conf = alt.get("confidence", 0.0)
        if alt.get("transcript") and conf > best_conf:
            best, best_conf = alt["transcript"], conf
    return romanize(best).strip()  # Devanagari -> "main ghar jaa rahaa hun"


if __name__ == "__main__":
    print("Ready. Hold [Right Ctrl] and speak. Ctrl+C here to quit.")
    try:
        while True:
            while not held():
                time.sleep(0.02)
            print("listening...", end="", flush=True)
            text = transcribe(record())
            print(f"\r{text or '(nothing heard)'}")
            if text:
                keyboard.write(text + " ")
    except KeyboardInterrupt:
        print("\nBye.")
