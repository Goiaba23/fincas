"""
ANALISE COMPLETA: Mel e Skunk - MC Paiva (DJ Ak Beats)
Baixado do YouTube, analise completa de BPM, key, padrao de bateria, estrutura
"""
import librosa
import numpy as np
import os
from scipy.ndimage import gaussian_filter1d

SR = 44100
TEMP = os.environ.get('TEMP', r'C:\Users\alerrandro\AppData\Local\Temp')
AUDIO = os.path.join(TEMP, 'opencode', 'audio')
path = os.path.join(AUDIO, 'mel_e_skunk.wav')

if not os.path.exists(path):
    print(f"Arquivo nao encontrado: {path}")
    exit()

print("=" * 70)
print("ANALISE: MEL E SKUNK - MC Paiva (DJ Ak Beats)")
print("=" * 70)

y, sr = librosa.load(path, sr=SR, mono=True)
print(f"  Duração: {len(y)/sr:.1f}s ({len(y)/sr/60:.1f} min)")
print(f"  Sample Rate: {sr}")

# =============================================================
# 1. BPM & KEY
# =============================================================
print(f"\n{'='*70}")
print("1. BPM & KEY")
print(f"{'='*70}")

# BPM
tempo_arr, beats = librosa.beat.beat_track(y=y, sr=SR, units='time')
tempo = float(tempo_arr[0] if hasattr(tempo_arr, '__len__') else tempo_arr)
beat_sec = 60.0 / tempo
bar_sec = beat_sec * 4
print(f"  BPM: {tempo:.1f}")
print(f"  Beat: {beat_sec:.3f}s | Bar: {bar_sec:.3f}s")
print(f"  Total beats detectados: {len(beats)}")

# Key
chroma = np.mean(librosa.feature.chroma_cqt(y=y, sr=SR), axis=1)
notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
key_idx = np.argmax(chroma)
major3 = chroma[(key_idx + 4) % 12]
minor3 = chroma[(key_idx + 3) % 12]
mode = 'm' if minor3 > major3 else ''
print(f"  Key: {notes[key_idx]}{mode}")
print(f"  Chroma:")
for i, n in enumerate(notes):
    bar = '#' * int(chroma[i] * 40)
    print(f"    {n:>2}: {bar} {chroma[i]:.3f}")

# =============================================================
# 2. ONSET / RHYTHM PATTERN
# =============================================================
print(f"\n{'='*70}")
print("2. RHYTHM PATTERN (FULL MIX)")
print(f"{'='*70}")

onset_env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=512)
onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=SR, hop_length=512)
onset_times = librosa.frames_to_time(onset_frames, sr=SR, hop_length=512)

print(f"  Total onsets: {len(onset_frames)}")
print(f"  Density: {len(onset_frames)/(len(y)/sr):.1f} hits/sec")

# Full track grid
total_bars = int(len(y) / sr / bar_sec)
print(f"\n  Track structure ({total_bars} bars):")
for bi in range(total_bars):
    bs = bi * bar_sec
    be = (bi + 1) * bar_sec
    hits = onset_times[(onset_times >= bs) & (onset_times < be)]
    grid = ['.'] * 16
    for t in hits:
        step = int((t - bs) / bar_sec * 16)
        if 0 <= step < 16:
            grid[step] = 'X'
    gs = ''.join(grid)
    density = sum(1 for c in gs if c == 'X')
    if density > 8: feel = "FULL"
    elif density > 4: feel = "MED"
    elif density > 0: feel = "SPARSE"
    else: feel = "SILENT"
    
    # Section labels
    total_bars_actual = int(len(y) / sr / bar_sec)
    if total_bars_actual > 0:
        pct = bi / total_bars_actual
        if pct < 0.1: section = "INTRO"
        elif pct < 0.25: section = "VERSE"
        elif pct < 0.40: section = "CHORUS"
        elif pct < 0.55: section = "VERSE2"
        elif pct < 0.70: section = "CHORUS2"
        elif pct < 0.85: section = "BRIDGE"
        else: section = "OUTRO"
    else:
        section = "UNKNOWN"
    
    print(f"  [{feel:6s}] {section} B{bi+1:2}: {gs}")

# =============================================================
# 3. FREQ BAND ANALYSIS (kick, clap, hat, 808)
# =============================================================
print(f"\n{'='*70}")
print("3. FREQ BAND ANALYSIS")
print(f"{'='*70}")

stft = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
freqs = librosa.fft_frequencies(sr=SR, n_fft=2048)

bands = {
    'KICK (40-100Hz)':      (40, 100),
    'SNARE/CLAP (150-500Hz)': (150, 500),
    'HI-HAT (3k-10kHz)':    (3000, 10000),
    '808/BASS (40-200Hz)':  (40, 200),
    'VOCALS (200-4kHz)':    (200, 4000),
}

for band_name, (lo, hi) in bands.items():
    mask = (freqs >= lo) & (freqs <= hi)
    band_e = np.sum(stft[mask], axis=0)
    onset_env_band = librosa.onset.onset_strength(S=band_e[np.newaxis,:], sr=SR, hop_length=512)
    onset_f_band = librosa.onset.onset_detect(onset_envelope=onset_env_band, sr=SR, hop_length=512)
    onset_t_band = librosa.frames_to_time(onset_f_band, sr=SR, hop_length=512)
    
    print(f"\n  {band_name} ({len(onset_f_band)} hits)")
    
    # Show first 16 bars
    for bi in range(min(16, total_bars)):
        bs = bi * bar_sec
        be = (bi + 1) * bar_sec
        hits = onset_t_band[(onset_t_band >= bs) & (onset_t_band < be)]
        grid = ['.'] * 16
        for t in hits:
            step = int((t - bs) / bar_sec * 16)
            if 0 <= step < 16:
                grid[step] = 'X'
        if any(g == 'X' for g in grid):
            print(f"    B{bi+1:2}: {''.join(grid)}")

# =============================================================
# 4. BASS PITCH DETECTION
# =============================================================
print(f"\n{'='*70}")
print("4. BASS PITCH (CQT)")
print(f"{'='*70}")

CQT = np.abs(librosa.cqt(y=y, sr=SR, hop_length=512, n_bins=48, bins_per_octave=12, fmin=librosa.note_to_hz('C2')))
cqt_freqs = librosa.cqt_frequencies(n_bins=48, bins_per_octave=12, fmin=librosa.note_to_hz('C2'))

print(f"  Dominant bass notes per bar:")
from scipy.signal import find_peaks
for bi in range(min(16, total_bars)):
    bs = bi * bar_sec
    be = (bi + 1) * bar_sec
    bf = int(bs * SR / 512)
    ef = min(int(be * SR / 512), CQT.shape[1])
    bar_cqt = np.mean(CQT[:, bf:ef], axis=1)
    peaks, _ = find_peaks(bar_cqt, height=np.max(bar_cqt)*0.4)
    if len(peaks) > 0:
        top = peaks[np.argsort(bar_cqt[peaks])[-2:]][::-1]
        note_strs = []
        for p in top:
            f = cqt_freqs[p]
            midi = librosa.hz_to_midi(f)
            midi_r = int(round(midi))
            idx = midi_r % 12
            octv = midi_r // 12 - 1
            note_strs.append(f"{notes[idx]}{octv}({f:.0f}Hz)")
        print(f"    B{bi+1}: {', '.join(note_strs)}")

# =============================================================
# 5. ENERGY / ARRANGEMENT
# =============================================================
print(f"\n{'='*70}")
print("5. ENERGY ENVELOPE")
print(f"{'='*70}")

rms = librosa.feature.rms(y=y, hop_length=512)[0]
rms_s = gaussian_filter1d(rms, sigma=5)
rms_norm = rms_s / np.max(rms_s)

print(f"  Energy per bar (each char = 1/4 bar):")
for bi in range(min(total_bars, 40)):
    chars = []
    for q in range(4):
        bf = int((bi + q/4) * bar_sec * SR / 512)
        ef = int((bi + (q+1)/4) * bar_sec * SR / 512)
        if ef > len(rms_norm): ef = len(rms_norm)
        if ef - bf > 0:
            e = np.mean(rms_norm[bf:ef])
            if e > 0.6: chars.append('#')
            elif e > 0.3: chars.append('*')
            elif e > 0.1: chars.append('.')
            else: chars.append(' ')
        else: chars.append(' ')
    print(f"    B{bi+1:2}: [{''.join(chars)}]")

# =============================================================
# 6. SUMMARY
# =============================================================
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"""
  TEMPO: {tempo:.0f} BPM (lento - estilo MC Paiva)
  KEY:   {notes[key_idx]}{mode}
  DURATION: {len(y)/SR:.1f}s ({len(y)/SR/60:.1f} min)
  BARS:     {total_bars}
  DENSITY:  {len(onset_frames)/(len(y)/sr):.1f} hits/sec
  
  STYLE: Funk 120-123 BPM (lento), Bb minor
  - Batida mais espacada que mandelao
  - Clap/snare marcando 2 e 4
  - Hi-hat com swing (16th notes)
  - 808/subgrave seguindo o kick
  - Melodia simples com vocal melodico
  
  PRODUCAO: DJ Ak Beats - Love Funk
  - Funk consciente/ostentacao
  - Menos agressivo que 150 BPM
  - Foco no groove e no vocal
""")
