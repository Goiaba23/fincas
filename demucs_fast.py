"""Fast demucs separation on short audio segment using htdemucs (faster model)"""
import librosa
import soundfile as sf
import numpy as np
import os, sys
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torch

SR = 44100
TEMP = os.environ.get('TEMP')
INPUT = os.path.join(TEMP, 'opencode', 'audio', 'hit_em_up_intro.wav')
OUTPUT = os.path.join(TEMP, 'opencode', 'stems', 'hit_em_up_intro')
os.makedirs(OUTPUT, exist_ok=True)

print(f"Loading {INPUT}...")
audio, sr = librosa.load(INPUT, sr=SR, mono=False)
print(f"Loaded: shape={audio.shape}, dur={audio.shape[1]/SR:.1f}s")

print("Loading demucs model (htdemucs - faster)...")
model = get_model('htdemucs')
model.eval()
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
print(f"Device: {device}")

wav_t = torch.from_numpy(audio).float().unsqueeze(0)
if device == 'cuda':
    wav_t = wav_t.cuda()

print("Separating stems...")
with torch.no_grad():
    sources = apply_model(model, wav_t, device=device, shifts=1, split=True, overlap=0.25, progress=True)

sources_np = sources[0].cpu().numpy()
names = ['drums', 'bass', 'other', 'vocals']
for i, name in enumerate(names):
    path = os.path.join(OUTPUT, f'{name}.wav')
    sf.write(path, sources_np[i].T, SR)
    print(f"  {name}: {path}")

no_vocals = sources_np[0] + sources_np[1] + sources_np[2]
path = os.path.join(OUTPUT, 'no_vocals.wav')
sf.write(path, no_vocals.T, SR)
print(f"  no_vocals: {path}")
print("Done!")
