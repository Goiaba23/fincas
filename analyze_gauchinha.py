"""Analyze Gauchinha BPM, key, and structure"""
import librosa
import numpy as np
import os

path = os.path.join(os.environ['TEMP'], 'opencode', 'audio', 'gauchinha.wav')
print(f"Loading {path}...")
y, sr = librosa.load(path, sr=22050, mono=True)
print(f"Duration: {len(y)/sr:.1f}s, SR: {sr}Hz")

# BPM detection
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
bpm_val = tempo[0] if isinstance(tempo, np.ndarray) else tempo
print(f"\nDetected BPM: {bpm_val:.1f}")
print(f"Beats found: {len(beats)}")

# Key detection using Krumhansl-Schmuckler
chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
chroma_avg = np.mean(chroma, axis=1)

# Krumhansl-Schmuckler key profiles
major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Normalize
chroma_avg_norm = chroma_avg / np.max(chroma_avg) if np.max(chroma_avg) > 0 else chroma_avg
major_profile_norm = major_profile / np.max(major_profile)
minor_profile_norm = minor_profile / np.max(minor_profile)

keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Correlation for each key (rotate chroma)
best_key = None
best_score = -999
best_mode = ''
for i in range(12):
    rotated_chroma = np.roll(chroma_avg_norm, i)
    major_score = np.corrcoef(rotated_chroma, major_profile_norm)[0, 1]
    minor_score = np.corrcoef(rotated_chroma, minor_profile_norm)[0, 1]
    
    if major_score > best_score:
        best_score = major_score
        best_key = keys[i]
        best_mode = 'major'
    if minor_score > best_score:
        best_score = minor_score
        best_key = keys[i]
        best_mode = 'minor'

print(f"\nDetected Key: {best_key} {best_mode} (score: {best_score:.3f})")

# Camelot wheel
camelot_major = {0:'11B',1:'6B',2:'1B',3:'8B',4:'3B',5:'10B',6:'5B',7:'12B',8:'7B',9:'2B',10:'9B',11:'4B'}
camelot_minor = {0:'5A',1:'12A',2:'7A',3:'2A',4:'9A',5:'4A',6:'11A',7:'6A',8:'1A',9:'8A',10:'3A',11:'10A'}
key_idx = keys.index(best_key) if best_key in keys else 0
if best_mode == 'major':
    print(f"Camelot: {camelot_major[key_idx]}")
else:
    print(f"Camelot: {camelot_minor[key_idx]}")

# Structure analysis - detect sections by energy
hop_length = 512
rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
# Smooth RMS
from scipy.ndimage import gaussian_filter1d
rms_smooth = gaussian_filter1d(rms, sigma=10)

# Find section boundaries (big energy changes)
energy_diff = np.diff(rms_smooth)
threshold = np.std(energy_diff) * 1.5
boundaries = np.where(np.abs(energy_diff) > threshold)[0]
time_boundaries = boundaries * hop_length / sr

print(f"\nSection boundaries (seconds):")
prev = 0
for i, t in enumerate(time_boundaries):
    if t > 1.0 and t - prev > 3.0:  # Sections > 3 seconds
        print(f"  {prev:.1f}s -> {t:.1f}s")
        prev = t
print(f"  {prev:.1f}s -> {len(y)/sr:.1f}s")
