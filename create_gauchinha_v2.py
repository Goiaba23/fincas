"""
GAUCHINHA-STYLE FUNK TRACK (v2 - rhythm corrected)
BPM: 129 | Key: C#m | Structure: 32 bars
Based on deep analysis of Gauchinha by MenoK / DJ Japa NK
"""
import numpy as np
import soundfile as sf
import librosa
import os

TEMP  = os.environ['TEMP']
STEMS = os.path.join(TEMP, 'opencode', 'stems', 'gauchinha_intro')
OUT   = os.path.join(TEMP, 'opencode', 'output')
os.makedirs(OUT, exist_ok=True)

SR   = 44100
BPM  = 129.0
BAR  = int(60 / BPM * 4 * SR)
NUM_BARS = 32

print("=" * 60)
print("GAUCHINHA FUNK v2 (Padrao Real)")
print(f"BPM: {BPM:.0f} | Key: C#m | Bars: {NUM_BARS}")
print("=" * 60)

notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

# -------------------------------------------------------------------
# Load Gauchinha stems
# -------------------------------------------------------------------
def load_stereo(path, label=''):
    if not os.path.exists(path):
        return None
    y, sr = librosa.load(path, sr=SR, mono=False)
    if len(y.shape) == 1:
        y = np.stack([y, y])
    return y.astype(np.float64)

gauchinha_dir = os.path.join(STEMS, 'gauchinha_intro')
vocals   = load_stereo(os.path.join(gauchinha_dir, 'vocals.wav'), 'Vocals')
drums    = load_stereo(os.path.join(gauchinha_dir, 'drums.wav'), 'Drums')
bass_    = load_stereo(os.path.join(gauchinha_dir, 'bass.wav'), 'Bass')
other    = load_stereo(os.path.join(gauchinha_dir, 'other.wav'), 'Other')
no_voc   = load_stereo(os.path.join(gauchinha_dir, 'no_vocals.wav'), 'Instr')

print("Stems loaded OK")

# -------------------------------------------------------------------
# 808 BASS - CORRECTED GAUCHINHA PATTERN
# -------------------------------------------------------------------
print("\n-- Creating 808 Bass --")

def note_to_hz(midi):
    return 440 * (2 ** ((midi - 69) / 12))

def render_808(note_midi, duration_sec, sr, amp=0.7):
    t = np.linspace(0, duration_sec, int(duration_sec * sr), False)
    freq = note_to_hz(note_midi)
    note = np.sin(2 * np.pi * freq * t)
    note += 0.4 * np.sin(2 * np.pi * freq * 2 * t)
    note += 0.15 * np.sin(2 * np.pi * freq * 3 * t)
    env = np.exp(-t * 3.5)
    note = note * env * amp
    note = np.tanh(note * 2.5)
    return note / max(np.abs(note)) * amp

# Bass follows kick pattern: hits on steps 3, 11 (off 16th of beats 1 & 3)
# Plus some passing notes for movement
# C#m progression: C#m - B - A - B
BAR_SAMPLES = int(BAR)
positions_16th = []
bass_audio = np.zeros(NUM_BARS * BAR_SAMPLES)
for bar_idx in range(NUM_BARS):
    bar_offset = bar_idx * 4  # 4 quarter notes per bar
    progression_idx = bar_idx % 4
    # C#m(0), B(1), A(2), B(3)
    if progression_idx == 0:  # C#m
        base_midi = 37
        alt_midi = 44
    elif progression_idx == 1:  # B
        base_midi = 35
        alt_midi = 42
    elif progression_idx == 2:  # A
        base_midi = 33
        alt_midi = 40
    else:  # B
        base_midi = 35
        alt_midi = 42
    
    # Bass hits on steps 3, 11 (syncopated with kick)
    positions_16th.append((bar_idx, base_midi, 3))
    positions_16th.append((bar_idx, alt_midi, 11))
    # Extra passing note on step 7 for movement
    if bar_idx % 2 == 0:
        positions_16th.append((bar_idx, base_midi + 3, 7))  # minor 3rd accent
    
    # Longer root note on beat 1
    t = np.linspace(0, 0.4, int(0.4 * SR), False)
    freq = note_to_hz(base_midi - 12)  # sub octave
    sub = np.sin(2 * np.pi * freq * t)
    sub *= np.exp(-t * 2)
    sub *= 0.5
    sub = np.tanh(sub * 2)
    start = bar_idx * BAR_SAMPLES
    end = start + len(sub)
    bass_audio[start:end] += sub

for bi, midi, step in positions_16th:
    bs = step / 16 * BAR_SAMPLES
    dur_s = 0.15
    note = render_808(midi, dur_s, SR, 0.75)
    start = bi * BAR_SAMPLES + int(bs)
    end = start + len(note)
    if end > len(bass_audio):
        end = len(bass_audio)
        note = note[:end-start]
    bass_audio[start:end] += note[:end-start]

# Normalize bass
bass_audio = np.clip(bass_audio, -1, 1)

bass_stereo = np.stack([bass_audio, bass_audio])
print(f"  808 Bass: {NUM_BARS} bars ({NUM_BARS*BAR_SAMPLES/SR:.1f}s)")

# -------------------------------------------------------------------
# DRUM PATTERNS (CORRECT GAUCHINHA RHYTHM)
# -------------------------------------------------------------------
print("-- Creating Drums (Gauchinha pattern) --")

def beat_noise(dur_sec, sr, color='white'):
    """Generate noise for percussion"""
    n = int(dur_sec * sr)
    if n == 0:
        return np.array([])
    noise = np.random.randn(n)
    if color == 'white':
        return noise
    elif color == 'pink':
        from scipy import signal
        b, a = signal.butter(2, 2000/(sr/2), 'low')
        return signal.lfilter(b, a, noise)
    return noise

def kick_synth(dur_sec, sr, freq_start=150, freq_end=40, amp=0.95):
    n = int(dur_sec * sr)
    t = np.linspace(0, dur_sec, n, False)
    freq = freq_start * (freq_end/freq_start) ** (t/dur_sec)
    phase = 2 * np.pi * np.cumsum(freq) / sr
    click = np.exp(-t * 80) * 0.3
    body = np.sin(phase) * np.exp(-t * 4)
    return (click + body * 0.4) * amp

def clap_synth(dur_sec, sr, amp=0.8):
    n = int(dur_sec * sr)
    t = np.linspace(0, dur_sec, n, False)
    noise = np.random.randn(n)
    env = np.exp(-t * 15)
    noise *= env
    # Add tonal component
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 20)
    return (noise + tone * 0.3) * amp * 0.6

def hat_synth(dur_sec, sr, amp=0.5):
    n = int(dur_sec * sr)
    t = np.linspace(0, dur_sec, n, False)
    noise = np.random.randn(n)
    env = np.exp(-t * 30)
    hp_noise = noise - np.convolve(noise, np.ones(50)/50, mode='same')
    return hp_noise * env * amp

def snare_synth(dur_sec, sr, amp=0.7):
    n = int(dur_sec * sr)
    t = np.linspace(0, dur_sec, n, False)
    noise = np.random.randn(n) * np.exp(-t * 12)
    tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 8)
    return (noise + tone * 0.5) * amp * 0.5

# Gauchinha pattern:
# Kick: steps 3, 11 (off 16th of beats 1 & 3)
# Clap: steps 7, 15 (off 16th of beats 2 & 4)
# Hi-hat: steps 0, 3, 6, 9, 12, 15 (triplet swing - every 3rd)
# Snare: steps 6, 14 (ghost/accents)

total_samples = NUM_BARS * BAR_SAMPLES

# Build all drum hits
drum_tracks = {
    'kick': np.zeros(total_samples),
    'clap': np.zeros(total_samples),
    'hat':  np.zeros(total_samples),
    'snare': np.zeros(total_samples),
}

# Hit durations in seconds
kick_hit = kick_synth(0.2, SR, 120, 35)
clap_hit = clap_synth(0.15, SR)
hat_hit  = hat_synth(0.08, SR)
snare_hit = snare_synth(0.18, SR)

# Section definitions for variation
# Each section: (start_bar, end_bar, density_multiplier)
# density = 1.0 means hits on defined steps
# density = 0.5 means 50% chance of each hit
sections = [
    (0, 2, 0.0),    # INTRO - silence
    (2, 4, 0.3),    # BUILD - sparse hat only
    (4, 8, 0.7),    # VERSE - medium
    (8, 12, 0.8),   # CHORUS
    (12, 16, 0.5),  # BRIDGE - stripped back
    (16, 24, 0.9),  # DROP2 - full
    (24, 32, 0.85), # OUTRO
]

for bar_idx in range(NUM_BARS):
    # Find section density
    density = 1.0
    for sb, eb, d in sections:
        if sb <= bar_idx < eb:
            density = d
            break
    
    bar_start = bar_idx * BAR_SAMPLES
    
    if density == 0.0:
        continue
    
    # KICK: steps 3, 11 (always on if density > 0.3)
    if density > 0.3:
        for step in [3, 11]:
            pos = bar_start + int(step / 16 * BAR_SAMPLES)
            if pos + len(kick_hit) <= total_samples:
                drum_tracks['kick'][pos:pos+len(kick_hit)] += kick_hit * density
            elif density > 0.6:
                # Extra kick on step 7 for fuller sections
                pos7 = bar_start + int(7 / 16 * BAR_SAMPLES)
                if pos7 + len(kick_hit) <= total_samples:
                    drum_tracks['kick'][pos7:pos7+len(kick_hit)] += kick_hit * 0.5
    
    # CLAP: steps 7, 15
    if density > 0.3:
        for step in [7, 15]:
            pos = bar_start + int(step / 16 * BAR_SAMPLES)
            if pos + len(clap_hit) <= total_samples:
                vol = 1.0 if step in [7, 15] else 0.5
                drum_tracks['clap'][pos:pos+len(clap_hit)] += clap_hit * vol * density
    
    # HI-HAT: triplet feel (steps 0, 3, 6, 9, 12, 15)
    if density > 0.1:
        hat_steps = [0, 3, 6, 9, 12, 15]
        if density < 0.5:
            hat_steps = [0, 6, 12]  # sparse
        for step in hat_steps:
            pos = bar_start + int(step / 16 * BAR_SAMPLES)
            if pos + len(hat_hit) <= total_samples:
                drum_tracks['hat'][pos:pos+len(hat_hit)] += hat_hit * density
    
    # SNARE: ghost notes
    if density > 0.5:
        for step in [4, 10]:
            pos = bar_start + int(step / 16 * BAR_SAMPLES)
            if pos + len(snare_hit) <= total_samples:
                drum_tracks['snare'][pos:pos+len(snare_hit)] += snare_hit * 0.3

# Mix drums
drums_mix = np.zeros((2, total_samples))
for name, track in drum_tracks.items():
    track = np.clip(track, -1, 1)
    drums_mix[0] += track * 0.5
    drums_mix[1] += track * 0.5

# -------------------------------------------------------------------
# VOCAL HOOKS
# -------------------------------------------------------------------
print("-- Processing Vocals --")
if vocals is not None:
    v_mono = librosa.to_mono(vocals)
    from pedalboard import Pedalboard, Reverb, Compressor, HighpassFilter, Gain
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=80),
        Compressor(threshold_db=-15, ratio=3.0, attack_ms=5, release_ms=50),
        Reverb(room_size=0.15, dry_level=0.85, wet_level=0.2),
        Gain(gain_db=-0.5),
    ])
    v_processed = board(v_mono, SR)
    vocal_stereo = np.stack([v_processed, v_processed])
else:
    vocal_stereo = None

# -------------------------------------------------------------------
# ASSEMBLE MIX
# -------------------------------------------------------------------
print("-- Assembling --")
mix = np.zeros((2, total_samples))

# Bass layer
bass_layer = bass_stereo[:, :total_samples]
mix[0] += bass_layer[0] * 0.6
mix[1] += bass_layer[1] * 0.6

# Drums layer
mix += drums_mix[:, :total_samples] * 0.8

# Vocals (loop the 60s stem across the track)
if vocal_stereo is not None:
    v_resized = np.zeros((2, total_samples))
    v_len = vocal_stereo.shape[1]
    for i in range(0, total_samples, v_len):
        chunk = min(v_len, total_samples - i)
        v_resized[:, i:i+chunk] = vocal_stereo[:, :chunk]
    mix[0] += v_resized[0] * 0.35
    mix[1] += v_resized[1] * 0.35

# Section volume automation
for bar_idx in range(NUM_BARS):
    bs = bar_idx * BAR_SAMPLES
    be = (bar_idx + 1) * BAR_SAMPLES
    if bar_idx < 2:  # INTRO
        vol = 0.15
    elif bar_idx < 4:  # BUILD
        vol = 0.3 + (bar_idx - 2) * 0.15
    elif bar_idx < 8:  # VERSE
        vol = 0.6
    elif bar_idx < 12:  # CHORUS
        vol = 0.8
    elif bar_idx < 16:  # BRIDGE
        vol = 0.4
    elif bar_idx < 24:  # DROP2
        vol = 0.85
    else:
        vol = 0.7
    mix[:, bs:be] *= vol

# Normalize pre-master
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.95

sf.write(os.path.join(OUT, 'gauchinha_funk_premaster.wav'), mix.T, SR)
print("  Pre-master saved")

# -------------------------------------------------------------------
# MASTERING
# -------------------------------------------------------------------
print("-- Mastering --")
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Compressor, Limiter, Gain

master = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=22.0),
    Compressor(threshold_db=-18, ratio=3.0, attack_ms=3, release_ms=40),
    LowpassFilter(cutoff_frequency_hz=18500.0),
    Gain(gain_db=0.8),
    Limiter(threshold_db=-0.3, release_ms=80),
])

print("  Processing...")
mastered = master(mix, SR)
peak = np.max(np.abs(mastered))
if peak > 0:
    mastered = mastered / peak * 0.95

output = os.path.join(OUT, 'gauchinha_funk_v2.wav')
sf.write(output, mastered.T, SR)

size_mb = os.path.getsize(output) / 1024**2
print(f"\n{'='*60}")
print(f"  COMPLETE: {output}")
print(f"  Duration: {mastered.shape[1]/SR:.1f}s ({mastered.shape[1]/SR/60:.1f} min)")
print(f"  Size: {size_mb:.1f} MB")
print(f"  BPM: {BPM:.0f} | Key: C#m")
print(f"  Rhythm: Gauchinha authentic pattern")
print(f"{'='*60}")
