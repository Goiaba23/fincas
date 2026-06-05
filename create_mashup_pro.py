"""
PROFESSIONAL MASHUP: 2Pac - Hit 'Em Up (Am, 95 BPM) + Kanye West - Can't Tell Me Nothing (Fm/Cm, 80 BPM)
Blend: Cm (5A)  Target BPM: 95  High-quality Rubberband + Pedalboard mastering
"""
import numpy as np
import soundfile as sf
import librosa
import pyrubberband as pyrb
import os

TEMP  = os.environ['TEMP']
STEMS = os.path.join(TEMP, 'opencode', 'stems')
OUT   = os.path.join(TEMP, 'opencode', 'output')
os.makedirs(OUT, exist_ok=True)

SR         = 44100
BPM_HIT    = 95.0
BPM_KANYE  = 80.0
TARGET_BPM = 95.0
STRETCH    = TARGET_BPM / BPM_KANYE   # 1.1875
PITCH      = 3                        # Am -> Cm (+3 semitones)

# File paths
HIT_NO_VOX = os.path.join(STEMS, 'hit_em_up_intro', 'no_vocals.wav')
HIT_DRUMS  = os.path.join(STEMS, 'hit_em_up_intro', 'drums.wav')
HIT_BASS   = os.path.join(STEMS, 'hit_em_up_intro', 'bass.wav')
HIT_OTHER  = os.path.join(STEMS, 'hit_em_up_intro', 'other.wav')

KANYE_INSTR = os.path.join(OUT, 'cant_tell_instrumental.wav')
KANYE_DRUMS = os.path.join(OUT, 'cant_tell_drums.wav')
KANYE_BASS  = os.path.join(OUT, 'cant_tell_bass.wav')
KANYE_OTHER = os.path.join(OUT, 'cant_tell_other.wav')

def load_stereo(path, label=''):
    if not os.path.exists(path):
        print(f"  * {label} not found, using zeros")
        return np.zeros((2, 44100))
    y, sr = librosa.load(path, sr=SR, mono=False)
    if len(y.shape) == 1:
        y = np.stack([y, y])
    print(f"  * {label}: {y.shape[1]/SR:.1f}s")
    return y.astype(np.float64)

# -------------------------------------------------------------------
# 1. LOAD STEMS
# -------------------------------------------------------------------
print("=" * 60)
print("PRO MASHUP: Hit Em Up x Cant Tell Me Nothing")
print("=" * 60)

print("\n-- Loading stems --")
print("Hit 'Em Up (intro 60s, no vocals):")
hit_no_vox = load_stereo(HIT_NO_VOX, 'Hit instrumental')
hit_drums  = load_stereo(HIT_DRUMS, 'Hit drums')
hit_bass   = load_stereo(HIT_BASS, 'Hit bass')
hit_other  = load_stereo(HIT_OTHER, 'Hit other')

print("Cant Tell Me Nothing (full, no vocals):")
kanye_instr = load_stereo(KANYE_INSTR, 'Kanye instrumental')
kanye_drums = load_stereo(KANYE_DRUMS, 'Kanye drums')
kanye_bass  = load_stereo(KANYE_BASS, 'Kanye bass')
kanye_other = load_stereo(KANYE_OTHER, 'Kanye other')

# -------------------------------------------------------------------
# 2. TIME-STRETCH KANYE (80 -> 95 BPM) with Rubberband
# -------------------------------------------------------------------
print(f"\n-- Time-stretch Kanye {BPM_KANYE}->{TARGET_BPM} BPM (rubberband) --")
def stretch_stereo(y, rate, label=''):
    chs = []
    for ch in range(2):
        print(f"  Stretching {label} ch{ch}...")
        chs.append(pyrb.time_stretch(y[ch], SR, rate).astype(np.float64))
    return np.array(chs)

kanye_other = stretch_stereo(kanye_other, STRETCH, 'Kanye-other')
kanye_drums = stretch_stereo(kanye_drums, STRETCH, 'Kanye-drums')
kanye_bass  = stretch_stereo(kanye_bass,  STRETCH, 'Kanye-bass')
kanye_instr = stretch_stereo(kanye_instr, STRETCH, 'Kanye-instr')

# -------------------------------------------------------------------
# 3. PITCH-SHIFT HIT EM UP (Am -> Cm, +3) with Rubberband
# -------------------------------------------------------------------
print(f"\n-- Pitch-shift Hit Em Up Am->Cm (+{PITCH} semitones, rubberband) --")
def shift_stereo(y, n_steps, label=''):
    chs = []
    for ch in range(2):
        print(f"  Shifting {label} ch{ch}...")
        chs.append(pyrb.pitch_shift(y[ch], SR, n_steps).astype(np.float64))
    return np.array(chs)

hit_no_vox = shift_stereo(hit_no_vox, PITCH, 'Hit-instr')
hit_drums  = shift_stereo(hit_drums,  PITCH, 'Hit-drums')
hit_bass   = shift_stereo(hit_bass,   PITCH, 'Hit-bass')
hit_other  = shift_stereo(hit_other,  PITCH, 'Hit-other')

# -------------------------------------------------------------------
# 4. ARRANGEMENT
# -------------------------------------------------------------------
print(f"\n-- Building arrangement --")
B = int(60 / TARGET_BPM * 4 * SR)  # samples per bar

def sb(bar):
    """sample index for a given bar position"""
    return bar * B

def get(audio, start_bar, num_bars):
    """Extract num_bars from audio at bar position, wrapping/truncating as needed."""
    s = start_bar * B
    n = num_bars * B
    if s >= audio.shape[1]:
        return np.zeros((2, n))
    available = audio.shape[1] - s
    result = audio[:, s:s+min(n, available)]
    if result.shape[1] < n:
        extra = np.zeros((2, n - result.shape[1]))
        result = np.concatenate([result, extra], axis=1)
    return result[:, :n]

# Structure: Intro(16) + Build(16) + Drop(32) + Breakdown(16) + Final(32) + Outro(8) = 120 bars
# Use get() for safe bounds-checked extraction

intro = np.zeros((2, 16 * B))
intro[:, :8*B] += get(kanye_other, 0, 8) * 0.50
intro[:, 8*B:16*B] += get(kanye_other, 8, 8) * 0.50 + get(kanye_drums, 8, 8) * 0.40

build = np.zeros((2, 16 * B))
build[:, :8*B] += get(kanye_other, 16, 8) * 0.60 + get(kanye_drums, 16, 8) * 0.50
build[:, :8*B] += get(hit_bass, 0, 8) * 0.20
build[:, 8*B:16*B] += get(kanye_instr, 24, 8) * 0.60
build[:, 8*B:16*B] += get(hit_other, 0, 8) * 0.30

print("  Section A: Intro (Kanye only, 16 bars)")
print("  Section B: Build (16 bars)")
print("  Section C: Drop! (32 bars)")

drop = np.zeros((2, 32 * B))
hit_len = hit_no_vox.shape[1]
for i in range(4):
    off = i * 8 * B
    ko  = (32 + i*8) * B
    # Kanye backbone
    drop[:, off:off+8*B] += kanye_instr[:, ko:ko+8*B] * 0.50
    # Hit em up layers (loop and trim)
    h_start = (i * 8 * B) % hit_len
    h_end = h_start + 8*B
    if h_end > hit_len:
        h_end = hit_len
    h_len = h_end - h_start
    if h_len > 0:
        drop[:, off:off+h_len] += hit_no_vox[:, h_start:h_end] * 0.45
        drop[:, off:off+h_len] += hit_drums[:, h_start:h_end] * 0.35

print("  Section D: Breakdown (16 bars)")
breakdown = np.zeros((2, 16 * B))
breakdown[:, :8*B] += get(kanye_other, 64, 8) * 0.35
breakdown[:, :8*B] += get(hit_bass, 0, 8) * 0.50
breakdown[:, 8*B:16*B] += get(kanye_drums, 72, 8) * 0.50 + get(kanye_other, 72, 8) * 0.40

print("  Section E: Final Drop (32 bars)")
final = np.zeros((2, 32 * B))
for i in range(4):
    off = i * 8 * B
    final[:, off:off+8*B] += get(kanye_instr, 80 + i*8, 8) * 0.60
    final[:, off:off+8*B] += get(hit_no_vox, i*8, 8) * 0.50
    final[:, off:off+8*B] += get(hit_drums, i*8, 8) * 0.40

print("  Section F: Outro (8 bars)")
outro = np.zeros((2, 8 * B))
outro[:, :4*B] += get(kanye_other, 112, 4) * 0.30 + get(kanye_drums, 112, 4) * 0.20
outro[:, 4*B:8*B] += get(kanye_other, 116, 4) * 0.15

print("\n-- Gluing sections --")
raw = np.concatenate([intro, build, drop, breakdown, final, outro], axis=1)
print(f"  Raw mix: {raw.shape[1]/SR:.1f}s")

peak = np.max(np.abs(raw))
if peak > 0:
    raw = raw / peak * 0.90

sf.write(os.path.join(OUT, 'mashup_premaster.wav'), raw.T, SR)
print("  Saved: mashup_premaster.wav")

# -------------------------------------------------------------------
# 5. PROFESSIONAL MASTERING with Pedalboard
# -------------------------------------------------------------------
print(f"\n-- Professional Mastering Chain (Pedalboard) --")
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Compressor, Limiter, Gain

board = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=30.0),
    Compressor(threshold_db=-18.0, ratio=3.0, attack_ms=5, release_ms=50),
    LowpassFilter(cutoff_frequency_hz=18000.0),
    Gain(gain_db=1.0),
    Limiter(threshold_db=-0.5, release_ms=100),
])

print("  Processing...")
mastered = board(raw, SR)

peak = np.max(np.abs(mastered))
if peak > 0:
    mastered = mastered / peak * 0.95

output_path = os.path.join(OUT, 'mashup_professional.wav')
sf.write(output_path, mastered.T, SR)
print(f"  Mastered: saved to {output_path}")
print(f"  Duration: {mastered.shape[1]/SR:.1f}s ({mastered.shape[1]/SR/60:.1f} min)")
print(f"  Size: {os.path.getsize(output_path)/1024**2:.1f} MB")
print(f"  BPM: {TARGET_BPM} | Key: Cm (5A)")
print(f"  Chain: HPF(30Hz)->Comp(-18dB)->LPF(18kHz)->Gain(+1dB)->Limiter(-0.5dB)")
print("\nDone!")
