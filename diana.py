import wave
from piper import PiperVoice, SynthesisConfig

voice = PiperVoice.load("./en_GB-cori-high.onnx")


with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav("""Oh boy, another one...  If you want to know more about Linux or Windows, I'm not going to spoon-feed it to you. You need to put in some effort to learn something new.""", wav_file, syn_config=SynthesisConfig(    
    volume=0.7,  # half as loud
    length_scale=1.0,  # twice as slow
    noise_scale=0.8,  # more audio variation
    noise_w_scale=1.0,  # more speaking variation
    normalize_audio=True,))
