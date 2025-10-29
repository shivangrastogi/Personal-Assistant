# tts_engine.py
import os
import torch
from TTS.utils.synthesizer import Synthesizer

class TTSEngine:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("🔄 Loading FastPitch + HiFiGAN TTS engine for the first time...")
            cls._instance = super(TTSEngine, cls).__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        else:
            print("⚡ Using preloaded TTS engine.")
        return cls._instance

    def _initialize(self, base_dir=r"D:\JARVIS\DATA\SPEAK MODAL\local_tts_modal", device="cpu"):
        """Initialize Synthesizer once using local models"""
        tts_model_path = os.path.join(base_dir, "tts_models--en--ljspeech--fast_pitch", "model_file.pth")
        tts_config_path = os.path.join(base_dir, "tts_models--en--ljspeech--fast_pitch", "config.json")
        vocoder_model_path = os.path.join(base_dir, "vocoder_models--en--ljspeech--hifigan_v2", "model_file.pth")
        vocoder_config_path = os.path.join(base_dir, "vocoder_models--en--ljspeech--hifigan_v2", "config.json")

        self.synthesizer = Synthesizer(
            tts_checkpoint=tts_model_path,
            tts_config_path=tts_config_path,
            vocoder_checkpoint=vocoder_model_path,
            vocoder_config=vocoder_config_path,
            use_cuda=(device == "cuda")
        )
        print("✅ TTS Engine loaded and ready for instant speech synthesis.")

    def synthesize(self, text: str):
        """Generate audio waveform from text"""
        if not text.strip():
            return None
        return self.synthesizer.tts(text)

    def save(self, wav, output_path: str):
        """Save generated waveform to WAV file"""
        self.synthesizer.save_wav(wav, output_path)
