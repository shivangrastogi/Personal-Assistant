# synthesizer.py
import numpy as np
import torch

from DATA.TTS_MINIMAL.config import load_config
from DATA.TTS_MINIMAL.tts.models import setup_model as setup_tts_model
from DATA.TTS_MINIMAL.utils.audio import AudioProcessor
from DATA.TTS_MINIMAL.utils.audio.numpy_transforms import save_wav as tts_save_wav
from DATA.TTS_MINIMAL.vocoder.models import setup_model as setup_vocoder_model
from DATA.TTS_MINIMAL.tts.utils.synthesis import synthesis, trim_silence
from typing import List


class Synthesizer:
    def __init__(self, tts_checkpoint, tts_config_path, vocoder_checkpoint, vocoder_config, use_cuda=False):
        self.use_cuda = use_cuda and torch.cuda.is_available()

        # Load TTS
        self.tts_config = load_config(tts_config_path)
        self.tts_model = setup_tts_model(self.tts_config)
        self.tts_model.load_checkpoint(self.tts_config, tts_checkpoint, eval=True)
        if self.use_cuda:
            self.tts_model.cuda()

        self.ap = self.tts_model.ap
        self.sample_rate = self.tts_config.audio["sample_rate"]

        # Load vocoder
        self.vocoder_config = load_config(vocoder_config)
        self.vocoder_ap = AudioProcessor(verbose=False, **self.vocoder_config.audio)
        self.vocoder_model = setup_vocoder_model(self.vocoder_config)
        self.vocoder_model.load_checkpoint(self.vocoder_config, vocoder_checkpoint, eval=True)
        if self.use_cuda:
            self.vocoder_model.cuda()

    def tts(self, text):
        outputs = synthesis(
            model=self.tts_model,
            text=text,
            CONFIG=self.tts_config,
            use_cuda=self.use_cuda,
            use_griffin_lim=False
        )

        wav = outputs["wav"]
        if torch.is_tensor(wav):
            wav = wav.cpu().numpy()
        elif isinstance(wav, list):
            wav = np.array(wav)

        mel = outputs["outputs"]["model_outputs"][0].detach().cpu().numpy()
        mel = self.ap.denormalize(mel.T).T
        voc_in = self.vocoder_ap.normalize(mel.T)
        voc_in = torch.tensor(voc_in).unsqueeze(0)

        if self.use_cuda:
            voc_in = voc_in.cuda()

        voc_output = self.vocoder_model.inference(voc_in)
        if torch.is_tensor(voc_output):
            voc_output = voc_output.cpu().numpy()

        voc_output = voc_output.squeeze()
        if self.tts_config.audio.get("do_trim_silence", False):
            voc_output = trim_silence(voc_output, self.ap)

        return voc_output

    def save_wav(self, wav: List[int], path: str, pipe_out=None) -> None:
        if torch.is_tensor(wav):
            wav = wav.cpu().numpy()
        if isinstance(wav, list):
            wav = np.array(wav)

        tts_save_wav(wav=wav, path=path, sample_rate=self.sample_rate, pipe_out=pipe_out)
