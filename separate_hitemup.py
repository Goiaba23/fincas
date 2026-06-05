"""Separate Hit 'Em Up stems using demucs Python API (avoids torchcodec CLI bug)"""
import librosa
import soundfile as sf
import numpy as np
import os
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torch

SR = 44100
TEMP = os.environ.get('TEMP') + '\\opencode\\audio'
INPUT = os.path.join(TEMP, 'hit_em_up.wav')
OUTPUT = os.environ.get('TEMP') + '\\opencode\\stems\\hit_em_up'
os.makedirs(OUTPUT, exist_ok=True)

print(f"Loading {INPUT}...")
audio, sr = librosa.load(INPUT, sr=SR, mono=False)
print(f"Loaded: shape={audio.shape}, dur={audio.shape[1]/SR:.1f}s")

print("Loading demucs model (htdemucs_ft)...")
model = get_model('htdemucs_ft')
model.eval()
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
print(f"Device: {device}")

wav_t = torch.from_numpy(audio).float().unsqueeze(0)
if device == 'cuda':
    wav_t = wav_t.cuda()

print("Separating stems (this takes a while)...")
with torch.no_grad():
    sources = apply_model(model, wav_t, device=device, shifts=1, split=True, overlap=0.25, progress=True)

sources_np = sources[0].cpu().numpy()
print(f"Sources: {sources_np.shape}")

names = ['drums', 'bass', 'other', 'vocals']
for i, name in enumerate(names):
    path = os.path.join(OUTPUT, f'{name}.wav')
    sf.write(path, sources_np[i].T, SR)
    print(f"  Saved {name}: {path}")

# Create no_vocals mix
no_vocals = sources_np[0] + sources_np[1] + sources_np[2]
path = os.path.join(OUTPUT, 'no_vocals.wav')
sf.write(path, no_vocals.T, SR)
print(f"  Saved no_vocals: {path}")

print("Done! All stems saved to", OUTPUT)
