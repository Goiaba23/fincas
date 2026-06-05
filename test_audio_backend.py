import os
import torchaudio
import sys

# Force use of soundfile backend
try:
    torchaudio.set_audio_backend("soundfile")
    print("Soundfile backend set successfully")
except Exception as e:
    print(f"Could not set soundfile backend: {e}")

# Test loading
wav_path = r"C:\Users\alerrandro\AppData\Local\Temp\opencode\audio\mel_e_skunk.wav"
try:
    wav, sr = torchaudio.load(wav_path)
    print(f"Loaded: {wav.shape}, sr={sr}")
except Exception as e:
    print(f"Error loading: {e}")
    # Check what backends are available
    print(f"Available backends: {toraudio.list_audio_backends() if hasattr(torchaudio, 'list_audio_backends') else 'N/A'}")
