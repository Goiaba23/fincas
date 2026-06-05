"""Play the mashup through speakers"""
import soundfile as sf
import sounddevice as sd
import os

path = os.path.join(os.environ['TEMP'], 'opencode', 'output', 'mashup_professional.wav')

y, sr = sf.read(path)
print(f"Playing mashup ({len(y)/sr:.1f}s, {sr}Hz)...")
print("Press Ctrl+C to stop early")
sd.play(y, sr)
sd.wait()
print("Done!")
