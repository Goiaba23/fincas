"""
Demucs stem separation using soundfile for audio loading (bypasses torchcodec issues)
"""
import soundfile as sf
import torch
import numpy as np
from demucs import separate
from demucs.pretrained import get_model
from demucs.apply import apply_model
import json
import os
import sys

def main():
    input_wav = r"C:\Users\alerrandro\AppData\Local\Temp\opencode\audio\mel_e_skunk.wav"
    out_dir = r"C:\Users\alerrandro\AppData\Local\Temp\opencode\stems\mel_e_skunk"
    os.makedirs(out_dir, exist_ok=True)
    
    print("Loading audio with soundfile...")
    data, sr = sf.read(input_wav)
    print(f"Loaded: shape={data.shape}, sr={sr}")
    
    # Convert to torch tensor [batch, channels, time]
    if data.ndim == 1:
        data = np.stack([data, data], axis=0)  # mono to stereo
    else:
        data = data.T  # [samples, channels] -> [channels, samples]
    
    wav = torch.from_numpy(data).float().unsqueeze(0)  # [1, C, T]
    print(f"Tensor shape: {wav.shape}")
    
    print("Loading htdemucs model...")
    model = get_model(name="htdemucs")
    model.eval()
    
    print("Running separation (this will take a while on CPU)...")
    # Apply model
    with torch.no_grad():
        sources = apply_model(model, wav, device='cpu', shifts=1)
    
    # sources shape: [1, sources, channels, time]
    sources = sources.squeeze(0)  # [sources, channels, time]
    
    # Source names
    source_names = model.sources  # ['drums', 'bass', 'other', 'vocals']
    print(f"Sources: {source_names}")
    
    for i, name in enumerate(source_names):
        src = sources[i]  # [channels, time]
        src_np = src.cpu().numpy().T  # [time, channels]
        
        out_path = os.path.join(out_dir, f"{name}.wav")
        sf.write(out_path, src_np, sr)
        print(f"  Saved {name}: {out_path}")

if __name__ == "__main__":
    main()
