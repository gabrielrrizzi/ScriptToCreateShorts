from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
import wave
import contextlib
import os

def text_speech_en(text,keyword):
    path = "D:\Python\TTS\.models.json"

    model_manager = ModelManager(path)

    model_path, config_path, model_item = model_manager.download_model("tts_models/en/ljspeech/tacotron2-DDC")

    voc_path, voc_config_path, _ = model_manager.download_model(model_item["default_vocoder"])

    syn = Synthesizer(
        tts_checkpoint=model_path,
        tts_config_path=config_path,
        vocoder_checkpoint=voc_path,
        vocoder_config=voc_config_path
    )  

    outputs = syn.tts(text)
    syn.save_wav(outputs, os.path.dirname(__file__) + "\\"+ keyword + ".wav")
    duration = get_wav_length(os.path.dirname(__file__) + "\\"+ keyword + ".wav")
    return duration

def get_wav_length(file_path):
    with contextlib.closing(wave.open(file_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        duration = round(duration,0)
        return duration

    