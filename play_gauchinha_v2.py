import soundfile as sf
import sounddevice as sd
import os

TEMP = os.environ.get('TEMP', r'C:\Users\alerrandro\AppData\Local\Temp')
path = os.path.join(TEMP, 'opencode', 'output', 'gauchinha_funk_v2.wav')

print(f"Playing: {path}")
y, sr = sf.read(path)
print(f"Duration: {len(y)/sr:.1f}s | {y.shape}")
sd.play(y, sr)
sd.wait()
