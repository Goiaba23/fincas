import numpy as np, soundfile as sf, os, json, warnings
warnings.filterwarnings('ignore')
from scipy import signal as sig
from scipy.ndimage import zoom

SR = 44100
BPM = 179
BEAT_S = 60.0 / BPM
BAR_S = BEAT_S * 4

# Paths
BASE_BRF2 = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats"
BASE_REL = r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2"

# Find actual reliquia folder name
import glob
rel_subdirs = [d for d in os.listdir(BASE_REL) if os.path.isdir(os.path.join(BASE_REL, d))]
if rel_subdirs:
    REL = os.path.join(BASE_REL, rel_subdirs[0])
else:
    REL = BASE_REL
print(f"REL folder: {REL}")

def load_wav(path):
    y, sr = sf.read(path)
    if sr != SR:
        from scipy import signal
        y = signal.resample(y, int(len(y) * SR / sr))
    if y.ndim > 1: y = y.mean(axis=1)
    return y

def pitch_shift(y, factor):
    """Pitch shift by resampling. factor > 1 = higher pitch."""
    if abs(factor - 1.0) < 0.001: return y
    new_len = int(len(y) / factor)
    return zoom(y, new_len / len(y))

def place_sample(buffer, sample, start_sample, amp=1.0):
    end = start_sample + len(sample)
    if end > len(buffer):
        sample = sample[:len(buffer) - start_sample]
        end = len(buffer)
    if start_sample < 0: return
    buffer[start_sample:start_sample+len(sample)] += sample * amp

# ============================================================
# LOAD SAMPLES
# ============================================================
print("Loading samples...")

# 808 - best matching F#1
s_808 = load_wav(os.path.join(BASE_BRF2, "808", "[BRF2] 808 (6).wav"))
s_808 = s_808 / np.max(np.abs(s_808)) * 0.95

# Caixa - try Caixa 4 for brightness
s_caixa = load_wav(os.path.join(REL, "Caixa", "JF No Beat - RF2 - Caixa 4.wav"))
s_caixa = s_caixa / np.max(np.abs(s_caixa)) * 0.95

# Closed hat - short
s_hat_cl = load_wav(os.path.join(BASE_BRF2, "Hats", "[BRF2] Hat (11).wav"))
s_hat_cl = s_hat_cl / np.max(np.abs(s_hat_cl)) * 0.95

# Open hat - longer
s_hat_op = load_wav(os.path.join(BASE_BRF2, "Hats", "[BRF2] Hat (1).wav"))
s_hat_op = s_hat_op / np.max(np.abs(s_hat_op)) * 0.95

# Pontinho one-shot
s_pont = load_wav(os.path.join(REL, "Pontinho", "One-Shot", "JF No Beat - RF2 - One Shot 1.wav"))
s_pont = s_pont / np.max(np.abs(s_pont)) * 0.95

print(f"  808 len: {len(s_808)/SR:.2f}s, Caixa: {len(s_caixa)/SR:.2f}s, Hat_cl: {len(s_hat_cl)/SR:.3f}s")

# ============================================================
# BUILD SEQUENCE
# ============================================================
TOTAL_BARS = 64
TOTAL_SAMPLES = int(TOTAL_BARS * BAR_S * SR)
print(f"\nTotal: {TOTAL_BARS} bars = {TOTAL_BARS*BAR_S:.1f}s = {TOTAL_SAMPLES} samples")

# Create tracks
track_808 = np.zeros(TOTAL_SAMPLES, dtype=np.float64)
track_caixa = np.zeros(TOTAL_SAMPLES, dtype=np.float64)
track_hat = np.zeros(TOTAL_SAMPLES, dtype=np.float64)
track_pont = np.zeros(TOTAL_SAMPLES, dtype=np.float64)
track_pad = np.zeros(TOTAL_SAMPLES, dtype=np.float64)

# Chord progression: D#m (i) -> G#m (iv) -> A#m (v) -> D#m (i)
# 808 root notes: D#2 (38.9Hz), G#2 (51.9Hz), A#2 (58.3Hz), D#2 (38.9Hz)
# Reference: 808(6).wav is tuned to F#1 (46Hz)
# Pitch shift factors:
# F#1(46) -> D#2(38.9): 38.9/46 = 0.846
# F#1(46) -> G#2(51.9): 51.9/46 = 1.128
# F#1(46) -> A#2(58.3): 58.3/46 = 1.267
# F#1(46) -> D#2(38.9): 38.9/46 = 0.846

pitches = {
    'D#': 38.9 / 46.0,  # 0.846
    'G#': 51.9 / 46.0,  # 1.128
    'A#': 58.3 / 46.0,  # 1.267
    'F#': 1.0,          # reference
}

# Pre-pitch all 808 samples
print("Pitch-shifting 808 samples...")
s_808_dsharp = pitch_shift(s_808, pitches['D#'])
s_808_gsharp = pitch_shift(s_808, pitches['G#'])
s_808_asharp = pitch_shift(s_808, pitches['A#'])
s_808_fn = s_808  # reference

progression = ['D#', 'G#', 'A#', 'D#']  # 4 chords, each 16 bars
# Actually let me do 8-bar phrases to make it more varied
# Bars 0-7: D#m (intro/verse feels)
# Bars 8-15: D#m
# Bars 16-23: G#m
# Bars 24-31: A#m
# Bars 32-39: D#m
# Bars 40-47: D#m
# Bars 48-55: G#m
# Bars 56-63: A#m -> D#m

chord_map = []
for bar in range(TOTAL_BARS):
    if bar < 16: chord_map.append('D#')
    elif bar < 24: chord_map.append('G#')
    elif bar < 32: chord_map.append('A#')
    elif bar < 48: chord_map.append('D#')
    elif bar < 56: chord_map.append('G#')
    elif bar < 64: chord_map.append('A#')
chord_map.append('D#')  # last bar resolution

chord_808 = {'D#': s_808_dsharp, 'G#': s_808_gsharp, 'A#': s_808_asharp}

# ============================================================
# 808 PATTERN
# ============================================================
# Funk 808: plays on 8th notes with accent pattern
# Pattern per bar: 1 . 2 . 3 . 4 .  (all 8th notes)
# Or more syncopated: 1 . . . 3 . . .

print("Building 808 pattern...")

for bar in range(TOTAL_BARS):
    chord = chord_map[bar]
    s = chord_808[chord]
    bar_start = int(bar * BAR_S * SR)
    
    if bar < 4:  # Intro - lighter
        # Single hit on 1
        place_sample(track_808, s, bar_start, amp=0.5)
    elif bar < 16:  # Verse - standard
        place_sample(track_808, s, bar_start, amp=0.7)
        place_sample(track_808, s, bar_start + int(2 * BEAT_S * SR), amp=0.7)
    elif bar < 32:  # Chorus/build
        place_sample(track_808, s, bar_start, amp=1.0)
        place_sample(track_808, s, bar_start + int(2 * BEAT_S * SR), amp=0.9)
        # Extra 8th note feel
        place_sample(track_808, s, bar_start + int(BEAT_S * SR), amp=0.5)
        place_sample(track_808, s, bar_start + int(3 * BEAT_S * SR), amp=0.5)
    elif bar < 48:  # Verse 2
        place_sample(track_808, s, bar_start, amp=0.8)
        place_sample(track_808, s, bar_start + int(2 * BEAT_S * SR), amp=0.8)
    else:  # Finale
        place_sample(track_808, s, bar_start, amp=1.0)
        place_sample(track_808, s, bar_start + int(2 * BEAT_S * SR), amp=0.9)
        place_sample(track_808, s, bar_start + int(BEAT_S * SR), amp=0.6)
        place_sample(track_808, s, bar_start + int(3 * BEAT_S * SR), amp=0.6)

# Decorate with F# passing notes on last 8 bars
for bar in range(56, 64):
    bar_start = int(bar * BAR_S * SR)
    place_sample(track_808, s_808_fn, bar_start + int(1.5 * BEAT_S * SR), amp=0.4)
    place_sample(track_808, s_808_fn, bar_start + int(3.5 * BEAT_S * SR), amp=0.4)

# ============================================================
# CAIXA PATTERN
# ============================================================
print("Building caixa pattern...")
for bar in range(TOTAL_BARS):
    bar_start = int(bar * BAR_S * SR)
    if bar < 4:  # Intro - no caixa
        continue
    elif bar < 16:  # Verse - on 2 and 4
        place_sample(track_caixa, s_caixa, bar_start + int(2 * BEAT_S * SR), amp=0.8)
        place_sample(track_caixa, s_caixa, bar_start + int(4 * BEAT_S * SR), amp=0.8)
    else:  # Full on 2 and 4
        place_sample(track_caixa, s_caixa, bar_start + int(2 * BEAT_S * SR), amp=1.0)
        place_sample(track_caixa, s_caixa, bar_start + int(4 * BEAT_S * SR), amp=1.0)
        # Ghost notes on 8ths before 2 and 4 in finale
        if bar >= 48:
            place_sample(track_caixa, s_caixa, bar_start + int(1.5 * BEAT_S * SR), amp=0.3)
            place_sample(track_caixa, s_caixa, bar_start + int(3.5 * BEAT_S * SR), amp=0.3)

# ============================================================
# HAT PATTERN (16th notes with swing)
# ============================================================
print("Building hi-hat pattern...")
swing = 0.15  # 15% swing
for bar in range(TOTAL_BARS):
    bar_start = int(bar * BAR_S * SR)
    for step in range(16):  # 16th notes in a bar
        t = step / 16.0 * BAR_S * SR
        # Add swing to even-numbered 16th notes (offbeats)
        if step % 2 == 1:
            t += swing * 0.5 * BEAT_S * SR
        pos = int(bar_start + t)
        
        if bar < 4:  # Intro - quieter
            amp = 0.3
        elif bar < 32:  # Verse/Chorus
            amp = 0.7 if step % 2 == 0 else 0.5
        else:  # Full
            amp = 0.9 if step % 2 == 0 else 0.6
        
        if step == 0 or step == 8:  # Accent on 1 and 3
            amp *= 1.0
        
        if pos < TOTAL_SAMPLES:
            track_hat[pos:pos+len(s_hat_cl)] += s_hat_cl * amp

    # Open hat accent on 4& (last upbeat) in chorus sections
    if bar >= 16 and bar < 48 and bar % 4 == 0:
        open_pos = bar_start + int(3.75 * BEAT_S * SR)
        if open_pos < TOTAL_SAMPLES:
            track_hat[open_pos:open_pos+len(s_hat_op)] += s_hat_op * 0.5

# ============================================================
# PONTINHO (One-shot embellishments)
# ============================================================
print("Building pontinho pattern...")
for bar in range(8, TOTAL_BARS):
    if bar % 4 == 0:  # Every 4 bars
        bar_start = int(bar * BAR_S * SR)
        # Pontinho on the 4& of previous bar or start of next
        pont_pos = bar_start - int(0.25 * BEAT_S * SR)
        if pont_pos > 0 and pont_pos < TOTAL_SAMPLES:
            amp = 0.6 if bar < 32 else 0.8
            place_sample(track_pont, s_pont, pont_pos, amp=amp)

# ============================================================
# SIMPLE PAD (sawtooth with filtering)
# ============================================================
print("Building pad...")
pad_notes = {
    'D#': [38.9/2, 58.3, 73.4, 92.5],  # D#2, A#3, D#4, F#4 
    'G#': [51.9, 77.8, 103.8],          # G#2, D#3, G#3
    'A#': [58.3, 87.3, 116.5],          # A#2, F#3, A#3
    'F#': [46.0, 69.3, 92.5],           # F#2, C#3, F#3
}

for bar in range(8, TOTAL_BARS):
    chord = chord_map[bar]
    bar_start = int(bar * BAR_S * SR)
    bar_len = int(BAR_S * SR)
    for note_hz in pad_notes.get(chord, [100]):
        note = np.sin(2 * np.pi * note_hz * np.arange(bar_len) / SR)
        note += 0.3 * np.sin(2 * np.pi * note_hz * 2 * np.arange(bar_len) / SR)  # slight harmonic
        env = np.linspace(0.3, 0.0, bar_len)  # fade out
        note = note * env * 0.1
        track_pad[bar_start:bar_start+bar_len] += note

# ============================================================
# MIX
# ============================================================
print("Mixing tracks...")
tracks = {
    '808': track_808,
    'Caixa': track_caixa,
    'Hat': track_hat,
    'Pontinho': track_pont,
    'Pad': track_pad,
}

# Clipping prevention via headroom
for name, t in tracks.items():
    peak = np.max(np.abs(t))
    if peak > 0:
        print(f"  {name}: peak={peak:.3f}, rms={np.sqrt(np.mean(t**2)):.4f}")

# Submix
mix = track_808 * 1.0 + track_caixa * 0.5 + track_hat * 0.2 + track_pont * 0.4 + track_pad * 0.4

# Normalize individual peaks
peak_mix = np.max(np.abs(mix))
if peak_mix > 1.0:
    mix = mix / peak_mix * 0.95
    print(f"\nNormalized mix (was {peak_mix:.2f})")

print(f"Final mix: peak={np.max(np.abs(mix)):.3f}, rms={np.sqrt(np.mean(mix**2)):.4f}")

# ============================================================
# MASTERING with pedalboard
# ============================================================
print("\nApplying mastering...")

from pedalboard import Pedalboard, Compressor, LowpassFilter, HighpassFilter, Gain, Limiter

# Light mastering chain
board = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=25.0),
    Compressor(threshold_db=-18, ratio=3.0, attack_ms=5, release_ms=100),
    LowpassFilter(cutoff_frequency_hz=18000.0),
    Gain(gain_db=2.0),
    Limiter(threshold_db=-0.5, release_ms=50),
])

mastered = board.process(mix, SR)
mastered = mastered / np.max(np.abs(mastered)) * 0.95

print(f"Mastered: peak={np.max(np.abs(mastered)):.3f}, rms={np.sqrt(np.mean(mastered**2)):.4f}")

# ============================================================
# EXPORT
# ============================================================
out_path = os.path.expandvars(r'%TEMP%\opencode\mundo_louco_beat.wav')
sf.write(out_path, mastered, SR)
file_size = os.path.getsize(out_path)
print(f"\nExported: {out_path}")
print(f"Size: {file_size/1024/1024:.1f}MB")
print(f"Duration: {len(mastered)/SR:.1f}s")
print(f"BPM: {BPM}, Bars: {TOTAL_BARS}")
print(f"Progression: {' - '.join(list(dict.fromkeys(chord_map)))}")
print("\nDone!")
