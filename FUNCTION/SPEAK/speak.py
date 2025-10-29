# speak.py
import os
import time
import simpleaudio as sa
from BRAIN.tts_engine import TTSEngine

class JarvisSpeaker:
    def __init__(self):
        self.engine = TTSEngine() 

    def speak(self, text="Hello"):
        if not text.strip():
            return

        print(f"🗣 Speaking: {text}")
        os.makedirs("outputs", exist_ok=True)
        output_path = os.path.join("outputs", f"output_{int(time.time() * 1000)}.wav")

        # Generate & save instantly (no reinitialization)
        wav = self.engine.synthesize(text)
        if wav is None:
            print("⚠️ No audio generated.")
            return

        self.engine.save(wav, output_path)

        # Play using simpleaudio
        try:
            wave_obj = sa.WaveObject.from_wave_file(output_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            print(f"❌ Playback error: {e}")

if __name__ == "__main__":
    jarvis = JarvisSpeaker()
    while True:
        jarvis.speak("Hello, I am your assistant.")
        time.sleep(1)
