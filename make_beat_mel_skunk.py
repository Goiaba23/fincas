"""
Produção do beat Mel e Skunk (MC Paiva style)
123 BPM | D#m | Funk lento
Usa samples reais do drum kit + stems do demucs
"""
import soundfile as sf
import numpy as np
import os
from pedalboard import Pedalboard, Compressor, Reverb, HighpassFilter, LowpassFilter, Gain, Limiter, Delay
import subprocess

SR = 44100
BPM = 123
BEATS_PER_BAR = 4
SEC_PER_BEAT = 60.0 / BPM
SEC_PER_BAR = SEC_PER_BEAT * BEATS_PER_BAR
TOTAL_BARS = 82  # mesma estrutura da original
TOTAL_SEC = TOTAL_BARS * SEC_PER_BAR  # ~160s

TEMP = os.environ.get('TEMP', 'C:\\Temp')
STEMS_DIR = os.path.join(TEMP, 'opencode', 'stems', 'mel_e_skunk')
SAMPLES_DIR = os.path.join(TEMP, 'opencode', 'samples')
OUTPUT_DIR = os.path.join(TEMP, 'opencode', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"=== Mel e Skunk Beat - {BPM} BPM, D#m ===")
print(f"Total: {TOTAL_BARS} bars = {TOTAL_SEC:.1f}s")

# === CARREGAR STEMS DO DEMUCS ===
print("\nLoading stems from demucs...")
vocals_raw, _ = sf.read(os.path.join(STEMS_DIR, 'vocals.wav'))
drums_raw, _ = sf.read(os.path.join(STEMS_DIR, 'drums.wav'))
bass_raw, _ = sf.read(os.path.join(STEMS_DIR, 'bass.wav'))
other_raw, _ = sf.read(os.path.join(STEMS_DIR, 'other.wav'))
print(f"  Vocals: {vocals_raw.shape}")
print(f"  Drums:  {drums_raw.shape}")
print(f"  Bass:   {bass_raw.shape}")
print(f"  Other:  {other_raw.shape}")

# === CARREGAR SAMPLES DO DRUM KIT ===
print("\nLoading drum kit samples...")
funk_drums, sr_drums = sf.read(os.path.join(SAMPLES_DIR, 'funk_drums.wav'))
funk_808, sr_808 = sf.read(os.path.join(SAMPLES_DIR, 'funk_808.wav'))
funk_snare, _ = sf.read(os.path.join(SAMPLES_DIR, 'funk_snare.wav'))
funk_hats, _ = sf.read(os.path.join(SAMPLES_DIR, 'funk_hats.wav'))
print(f"  Drums loop: {funk_drums.shape}, sr={sr_drums}")
print(f"  808 sample: {funk_808.shape}, sr={sr_808}")
print(f"  Snare:      {funk_snare.shape}")

# Se mono, converter para stereo
def to_stereo(arr):
    if arr.ndim == 1:
        return np.stack([arr, arr], axis=1)
    return arr

funk_drums = to_stereo(funk_drums)
funk_808_s = to_stereo(funk_808)
funk_snare_s = to_stereo(funk_snare)
funk_hats_s = to_stereo(funk_hats)

# === D#m (D# minor) FREQUENCIES ===
NOTE_D2 = 73.42  # D#2 = ~77.78 Hz (fundamental + 5th harmonic)
NOTE_A2 = 110.0  # A#2 = ~116.54 Hz
NOTE_F2 = 87.31  # F#2 = ~92.50 Hz (minor third)

def note_to_pitch_ratio(target_hz, sample_hz):
    return target_hz / sample_hz

# 808 sample pitch - vamos detectar a frequencia dominante
def estimate_pitch(audio, sr):
    """Estimate dominant frequency of a sample"""
    from scipy import signal
    f, t, Zxx = signal.stft(audio[:, 0] if audio.ndim > 1 else audio, fs=sr, npershot=1024)
    # Find max frequency in first 10% of time
    mag = np.abs(Zxx[:, :5])
    idx = np.argmax(mag.mean(axis=1))
    return f[idx]

def resample_pitch(audio, sr_in, ratio):
    """Pitch shift by resampling"""
    from scipy.interpolate import interp1d
    orig_len = len(audio)
    new_len = int(orig_len / ratio)
    x_old = np.linspace(0, 1, orig_len)
    x_new = np.linspace(0, 1, new_len)
    if audio.ndim == 1:
        f = interp1d(x_old, audio)
        return f(x_new)
    else:
        result = np.zeros((new_len, audio.shape[1]))
        for ch in range(audio.shape[1]):
            f = interp1d(x_old, audio[:, ch])
            result[:, ch] = f(x_new)
        return result

# Detect 808 sample pitch
try:
    import scipy.signal as signal
    f_est = estimate_pitch(funk_808_s, sr_808)
    print(f"\n  808 estimated pitch: {f_est:.1f} Hz")
except:
    f_est = 80  # default assumption
    print(f"\n  808 using default pitch: {f_est:.1f} Hz")

# Pitch 808 to D#2 (~77.78 Hz)
TARGET_D2 = 77.78
pitch_ratio_808 = TARGET_D2 / f_est
print(f"  Pitch ratio for D#2: {pitch_ratio_808:.3f}")
funk_808_d2 = resample_pitch(funk_808_s, sr_808, pitch_ratio_808)

def make_sine_808(duration_sec, freq_hz, sr=44100):
    """Generate a clean sine 808 tail"""
    t = np.linspace(0, duration_sec, int(sr * duration_sec))
    env = np.exp(-t * 4.0)  # decay envelope
    sine = np.sin(2 * np.pi * freq_hz * t) * env
    # Add harmonics for thickness
    sine += 0.3 * np.sin(4 * np.pi * freq_hz * t) * env
    sine += 0.1 * np.sin(6 * np.pi * freq_hz * t) * env
    # Normalize
    sine /= np.max(np.abs(sine))
    return np.stack([sine, sine], axis=1)

# === BUILD THE BEAT ===
print("\nBuilding beat...")
total_samples = int(TOTAL_SEC * SR)
beat = np.zeros((total_samples, 2))

# --- Structure: bars from analysis ---
structure = [
    ("intro", 9),
    ("verse", 12),
    ("chorus", 12),
    ("verse", 13),
    ("chorus", 12),
    ("bridge", 12),
    ("outro", 12),
]

# --- 1. Drums (loop) ---
print("  Adding drums loop...")
drums_len = len(funk_drums)
drums_samples = int(SEC_PER_BAR * SR)  # 1 bar loop
# Fit the loop to exactly 1 bar at 123 BPM
if drums_len != drums_samples:
    # Resample to match bar length
    ratio = drums_samples / drums_len
    from scipy.interpolate import interp1d
    x_old = np.linspace(0, 1, drums_len)
    x_new = np.linspace(0, 1, drums_samples)
    drums_loop = np.zeros((drums_samples, 2))
    for ch in range(2):
        f = interp1d(x_old, funk_drums[:, ch])
        drums_loop[:, ch] = f(x_new)
else:
    drums_loop = funk_drums

# Layer drum loop throughout
pos = 0
bar = 0
for section_name, section_bars in structure:
    for b in range(section_bars):
        start = pos
        end = pos + drums_samples
        if end > total_samples:
            end = total_samples
        beat[start:end] += drums_loop[:(end-start)] * 0.6
        pos = end
        bar += 1

# --- 2. 808 Bassline ---
print("  Adding 808 bassline...")
# Padrão funk: D#2 (tônica) → A#2 (quinta) → F#2 (terça menor)
# General pattern: walk down D# → A# → F# → D#
bass_pattern_bars = [
    # (freq, duration_in_bars, accent)
    (77.78, 1.5, 1.0),  # D#2
    (77.78, 0.5, 0.7),
    (116.54, 1.0, 0.9),  # A#2
    (92.50, 1.0, 0.8),   # F#2
    (77.78, 1.5, 1.0),  # D#2
    (77.78, 0.5, 0.6),
    (116.54, 0.75, 0.85),
    (92.50, 0.25, 0.7),
    (77.78, 0.5, 0.9),
    (77.78, 0.5, 0.6),
    (77.78, 0.5, 0.7),
    (77.78, 0.5, 0.5),
]

for section_name, section_bars in structure:
    for b in range(section_bars):
        bar_start = (sum(s[1] for s in structure[:structure.index((section_name, section_bars))]) + b) * drums_samples
        # Generate 808 for this bar
        beat_808 = make_sine_808(SEC_PER_BAR, 77.78, SR)
        # Add a pitch drop for movement
        t = np.linspace(0, SEC_PER_BAR, len(beat_808))
        freq_mod = 77.78 - 5.0 * (1 - np.exp(-t * 2))
        beat_808 = np.sin(2 * np.pi * freq_mod[:, None] * t[:, None]) * np.exp(-t[:, None] * 3.5)
        beat_808 = beat_808 * 0.3 / np.max(np.abs(beat_808))
        
        # Layer the 808
        start = int(bar_start)
        end = start + len(beat_808)
        if end > total_samples:
            end = total_samples
        beat[start:end, :] += beat_808[:(end-start), :]

# --- 3. Snare accents ---
print("  Adding snare accents...")
snare_samples = len(funk_snare_s)
# Add snare on beats 2 and 4 of each bar
for section_name, section_bars in structure:
    section_offset = sum(s[1] for s in structure[:structure.index((section_name, section_bars))])
    for b in range(section_bars):
        bar_idx = section_offset + b
        for beat_num in [1, 3]:  # beats 2 and 4 (0-indexed)
            snare_pos = int((bar_idx * SEC_PER_BAR + beat_num * SEC_PER_BEAT) * SR)
            if snare_pos + snare_samples < total_samples:
                vol = 0.7 if section_name == "chorus" else 0.5
                beat[snare_pos:snare_pos + snare_samples] += funk_snare_s * vol

# --- 4. Vocals from demucs ---
print("  Adding vocals...")
vocals = vocals_raw
vocals_len = len(vocals)
# Fit vocals to beat length
if vocals_len < total_samples:
    # Pad with silence
    vocals_padded = np.zeros((total_samples, vocals.shape[1]))
    vocals_padded[:vocals_len] = vocals
elif vocals_len > total_samples:
    vocals_padded = vocals[:total_samples]
else:
    vocals_padded = vocals

beat += vocals_padded * 0.8

# --- 5. Add "other" (melody/synths) from demucs ---
print("  Adding melody layer...")
other = other_raw
other_len = len(other)
if other_len < total_samples:
    other_padded = np.zeros((total_samples, other.shape[1]))
    other_padded[:other_len] = other
elif other_len > total_samples:
    other_padded = other[:total_samples]
else:
    other_padded = other

beat += other_padded * 0.5

# --- MASTERING CHAIN ---
print("\nMastering...")
master = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=25),
    Compressor(threshold_db=-24, ratio=3.0),
    Compressor(threshold_db=-12, ratio=2.0),
    Limiter(threshold_db=-1.0),
])

beat = master(beat, SR)
# Final normalize
max_val = np.max(np.abs(beat))
if max_val > 0:
    beat = beat / max_val * 0.95

# === SAVE ===
output_wav = os.path.join(OUTPUT_DIR, "mel_e_skunk_beat.wav")
sf.write(output_wav, beat, SR)
print(f"\nSaved: {output_wav}")
print(f"  Size: {os.path.getsize(output_wav) / 1e6:.1f} MB")
print(f"  Duration: {len(beat)/SR:.1f}s")

# Also save vocals-only processed version
print("\nProcessing clean vocals...")
vocals_chain = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=80),
    Compressor(threshold_db=-18, ratio=2.5),
    Reverb(room_size=0.2, dry_level=1.0, wet_level=0.15),
    Gain(gain_db=2),
    Limiter(threshold_db=-2),
])

vocals_processed = vocals_chain(vocals_padded, SR)
vocals_out = os.path.join(OUTPUT_DIR, "mel_e_skunk_vocals_processed.wav")
sf.write(vocals_out, vocals_processed, SR)
print(f"Saved: {vocals_out}")

# === TRY FL STUDIO MCP ===
print("\nAttempting to set up FL Studio via MCP...")
try:
    import sys
    sys.path.insert(0, r'C:\Users\alerrandro\Music\Nova pasta (2)')
    from fl_studio_mcp_client import FLStudioClient
    client = FLStudioClient()
    
    # Rename channels for Mel e Skunk project
    client.rename_channel(0, "Mel Drums")
    client.rename_channel(1, "Mel 808")
    client.rename_channel(2, "Mel Hat")
    client.rename_channel(3, "Mel Clap")
    client.rename_channel(4, "Mel Synth")
    
    # Route to mixer
    client.route_channel_to_mixer(0, 1)
    client.route_channel_to_mixer(1, 2)
    client.route_channel_to_mixer(2, 3)
    client.route_channel_to_mixer(3, 4)
    client.route_channel_to_mixer(4, 5)
    
    # Rename mixer tracks
    client.rename_mixer_track(1, "Drums")
    client.rename_mixer_track(2, "808 Bass")
    client.rename_mixer_track(3, "HiHat")
    client.rename_mixer_track(4, "Snare")
    client.rename_mixer_track(5, "Synth")
    
    print("  FL Studio channels and mixer updated!")
except Exception as e:
    print(f"  Could not update FL Studio: {e}")
    print("  (User can load the WAV directly)")

print("\n=== DONE ===")
print(f"Final WAV: {output_wav}")
print(f"Vocals:    {vocals_out}")
