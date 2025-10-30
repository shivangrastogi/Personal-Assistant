# listen.py
import os
import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from colorama import Fore, Style, init as colorama_init
from datetime import datetime

# Optional: install webrtcvad for better VAD (voice activity detection)
try:
    import webrtcvad
    VAD_AVAILABLE = True
except Exception:
    VAD_AVAILABLE = False

colorama_init(autoreset=True)

MODEL_PATH = r"D:\JARV-pycharm\Backend\DATA\LISTEN MODAL\Vosk Modal\vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
TIMEOUT_SEC = 10             # base timeout when waiting for audio blocks
MAX_SILENCE_BLOCKS = 12      # how many consecutive empty reads before giving up
BLOCKSIZE = 8000

if not os.path.isdir(MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at: {MODEL_PATH}")
vosk_model = Model(MODEL_PATH)

def now():
    return datetime.now().strftime("%H:%M:%S")

def _is_speaking():
    """Check speaking flag - simple IPC via env var.
       Returns True while Jarvis is speaking (set by speak.py).
    """
    return os.environ.get("JARVIS_SPEAKING", "0") == "1"

def listen():
    """
    Listen until speech recognized or timeout. Pauses automatically while Jarvis is speaking.
    Returns the recognized text (lowercased) or "" on timeout/error.
    """
    print(Fore.CYAN + f"[{now()}] Ready to listen. Speak into the microphone!")
    q = queue.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            print(Fore.RED + f"Audio Device Error: {status}")
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE,
                               dtype='int16', channels=1, callback=audio_callback):
            rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)
            if VAD_AVAILABLE:
                vad = webrtcvad.Vad(1)  # aggressive=1
            print(Fore.LIGHTGREEN_EX + "🟢 Listening... (Say something)")
            print(Fore.YELLOW + "⬤", end="", flush=True)

            silence_count = 0
            partial_text = ""
            last_audio_time = time.time()

            while True:
                # If Jarvis is speaking, pause listening until finished
                if _is_speaking():
                    print(Fore.MAGENTA + "\r[PAUSED] Jarvis is speaking — pausing listen...", end="", flush=True)
                    # Drain the queue to avoid filling memory
                    try:
                        while not q.empty():
                            q.get_nowait()
                    except Exception:
                        pass
                    # Sleep briefly and continue checking the speaking flag
                    time.sleep(0.1)
                    continue

                try:
                    data = q.get(timeout=TIMEOUT_SEC)
                    last_audio_time = time.time()
                except queue.Empty:
                    silence_count += 1
                    if silence_count >= MAX_SILENCE_BLOCKS:
                        print(Fore.RED + f"\n[{now()}] Timeout: No speech detected.")
                        return ""
                    continue

                # Optional VAD check (if installed)
                if VAD_AVAILABLE:
                    try:
                        is_speech = vad.is_speech(data, SAMPLE_RATE)
                        if not is_speech:
                            # not speech chunk — continue
                            continue
                    except Exception:
                        pass

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    recognized_txt = result.get("text", "").strip()
                    if recognized_txt:
                        recognized_txt = recognized_txt.lower()
                        print(Style.RESET_ALL + "\r" + Fore.BLUE + f"🔹 Mr Shivang: {recognized_txt}")
                        return recognized_txt
                    else:
                        print(Style.RESET_ALL + "\r" + Fore.RED + f"[{now()}] Sorry, couldn't recognize.")
                        return ""
                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial and partial != partial_text:
                        partial_text = partial
                        print(Style.RESET_ALL + "\r" + Fore.LIGHTYELLOW_EX + f"[... ] {partial}" + " " * 30, end="", flush=True)

    except Exception as exc:
        print(Fore.RED + f"\n[{now()}] Audio Error: {exc}")
        return ""


def hearing():
    """Simpler wake-word wait — same speaking pause considered."""
    print(Fore.CYAN + f"[{now()}] Waiting for wake word...")
    q = queue.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            print(Fore.RED + f"Audio Device Error: {status}")
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE,
                               dtype='int16', channels=1, callback=audio_callback):
            rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)
            while True:
                if _is_speaking():
                    time.sleep(0.1)
                    continue
                try:
                    data = q.get(timeout=TIMEOUT_SEC)
                except queue.Empty:
                    print(Fore.RED + f"\n[{now()}] Wake word timeout.")
                    return ""
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    recognized_txt = result.get("text", "").strip()
                    if recognized_txt:
                        recognized_txt = recognized_txt.lower()
                        print(Fore.CYAN + f"\n[{now()}] Wake Command Heard: {recognized_txt}")
                        return recognized_txt
                    else:
                        continue
    except Exception as exc:
        print(Fore.RED + f"\n[{now()}] Audio Error: {exc}")
        return ""


# For demo / debug mode — normally your main.py will call listen()
if __name__ == "__main__":
    while True:
        text = listen()
        print("Got:", text)
