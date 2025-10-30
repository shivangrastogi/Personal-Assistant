import os
import time
import threading
import hashlib
import simpleaudio as sa
from queue import Queue
from BRAIN.tts_engine import TTSEngine

# -----------------------------
# Global State and Cache
# -----------------------------
_AUDIO_CACHE = {}
_CACHE_LOCK = threading.Lock()
_speech_queue = Queue()
_stop_signal = threading.Event()

def _set_speaking_flag(val: bool):
    os.environ["JARVIS_SPEAKING"] = "1" if val else "0"


# -----------------------------
# Jarvis Speaker Class
# -----------------------------
class JarvisSpeaker:
    _instance = None  # ✅ Singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(JarvisSpeaker, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Avoid reinitializing the same instance
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        # Initialize TTS engine once
        self.engine = TTSEngine()

        # Start a single worker thread to handle queued speech
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    # -----------------------------
    # Public Methods
    # -----------------------------
    def speak(self, text="Hello", interrupt=False):
        """Queue text for speech. If interrupt=True, clear queue and stop ongoing playback."""
        if not text.strip():
            return
        if interrupt:
            _stop_signal.set()
            with _speech_queue.mutex:
                _speech_queue.queue.clear()
            _stop_signal.clear()
        _speech_queue.put(text)

    def stop(self):
        """Immediately stop ongoing playback."""
        _stop_signal.set()

    # -----------------------------
    # Internal Helpers
    # -----------------------------
    def _get_cached_wav(self, text: str):
        """Generate or retrieve cached WAV file for given text."""
        key = hashlib.md5(text.encode("utf-8")).hexdigest()

        with _CACHE_LOCK:
            if key in _AUDIO_CACHE and os.path.exists(_AUDIO_CACHE[key]):
                return _AUDIO_CACHE[key]

        # Generate new TTS output
        wav = self.engine.synthesize(text)
        if wav is None:
            return None

        os.makedirs("FUNCTION/SPEAK/outputs", exist_ok=True)
        path = os.path.join("FUNCTION", "SPEAK", "outputs", f"tts_{key}.wav")

        self.engine.save(wav, path)
        with _CACHE_LOCK:
            _AUDIO_CACHE[key] = path
        return path

    def _play_wav(self, wav_path):
        """Play a WAV file and monitor stop signal."""
        try:
            wave_obj = sa.WaveObject.from_wave_file(wav_path)
            play_obj = wave_obj.play()
            while play_obj.is_playing():
                if _stop_signal.is_set():
                    play_obj.stop()
                    break
                time.sleep(0.05)
        except Exception as e:
            print(f"❌ Playback error: {e}")

    def _worker(self):
        """Continuously process the speech queue sequentially."""
        while True:
            text = _speech_queue.get()
            if not text:
                continue

            _set_speaking_flag(True)
            try:
                wav_path = self._get_cached_wav(text)
                if wav_path:
                    self._play_wav(wav_path)
                else:
                    print("⚠️ TTS produced no audio.")
            finally:
                _set_speaking_flag(False)
                _speech_queue.task_done()


# -----------------------------
# Testing Loop (for debugging)
# -----------------------------
if __name__ == "__main__":
    speaker = JarvisSpeaker()

    def is_speaking():
        return os.environ.get("JARVIS_SPEAKING") == "1"

    while True:
        # Queue both messages (no interrupt to keep sequence intact)
        speaker.speak("Hello, I am your assistant. This is a test.")
        time.sleep(1)
        speaker.speak("Second line after first.")

        # Wait until speaking is done
        while is_speaking():
            time.sleep(0.1)

        print("🟢 Cycle complete, repeating...\n")
        time.sleep(2)
