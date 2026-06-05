import numpy as np, soundfile as sf, os, warnings
warnings.filterwarnings('ignore')
from scipy import signal as sig

SR = 44100
BPM = 179
BEAT_S = 60.0 / BPM
BAR_S = BEAT_S * 4

# Paths
BASE_BRF2 = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats"
BASE_REL = r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2"
rel_subdirs = [d for d in os.listdir(BASE_REL) if os.path.isdir(os.path.join(BASE_REL, d))]
REL = os.path.join(BASE_REL, rel_subdirs[0])

def load_wav(path):
    y, sr = sf.read(path)
    if y.ndim > 1: y = y.mean(axis=1)
    if sr != SR:
        old_len = len(y)
        new_len = int(old_len * SR / sr)
        y = sig.resample(y, new_len)
    return y / (np.max(np.abs(y)) + 1e-10)

def place(buffer, sample, pos, amp=1.0):
    if pos < 0 or pos >= len(buffer): return
    end = pos + len(sample)
    if end > len(buffer):
        sample = sample[:len(buffer) - pos]
        end = len(buffer)
    buffer[pos:pos+len(sample)] += sample * amp

# ============================================================
# SYNTHESIZED 808 - CLEAN, NO PITCH SHIFTING
# ============================================================
print("Synthesizing 808...")

def synth_808(freq_hz, duration_s=1.5, sr=SR):
    n = int(duration_s * sr)
    t = np.arange(n) / sr
    
    # Main sine with pitch decay (classic 808)
    pitch_decay = np.exp(-t * 12.0) * 5.0  # rapid pitch drop
    osc_freq = freq_hz + freq_hz * pitch_decay
    phase = np.cumsum(osc_freq) / sr * 2 * np.pi
    sine = np.sin(phase)
    
    # Sub layer (pure sine one octave down)
    sub_freq = freq_hz / 2
    sub_phase = np.cumsum(np.full(n, sub_freq)) / sr * 2 * np.pi
    sub = np.sin(sub_phase) * 0.5
    
    # Attack click (transient)
    click = np.zeros(n)
    click_len = int(0.008 * sr)
    click[:click_len] = np.sin(np.linspace(0, np.pi, click_len)) * 0.8
    click_env = np.exp(-t * 200)
    click = click * click_env
    
    # Distortion / saturation
    body = sine * 0.7 + sub * 0.5
    body = np.tanh(body * 3.0) * 0.5  # soft clip
    
    # Envelope
    env = np.ones(n)
    attack = int(0.003 * sr)
    env[:attack] = np.linspace(0, 1, attack)
    decay = np.exp(-t * 2.5)
    env = env * decay
    
    result = (body * env + click * 0.3) * 0.9
    return result / (np.max(np.abs(result)) + 1e-10)

# F#1 = 46.2Hz (the root of Mundo Louco - key of F#)
# Bailao funk often stays on one tonal center
# Use F# as the main 808 pitch (matches the original)
s_808_fn = synth_808(46.2, duration_s=1.5)  # F#1
s_808_fn_short = synth_808(46.2, duration_s=0.4)  # shorter version

# ============================================================
# LOAD REAL SAMPLES
# ============================================================
print("Loading samples...")

# Caixa - use Caixa 12 (short and snappy, 4119Hz centroid)
s_caixa = load_wav(os.path.join(REL, "Caixa", "JF No Beat - RF2 - Caixa 12.wav"))
s_caixa2 = load_wav(os.path.join(REL, "Caixa", "JF No Beat - RF2 - Caixa 4.wav"))

# Hats
s_hh_cl = load_wav(os.path.join(BASE_BRF2, "Hats", "[BRF2] Hat (11).wav"))
s_hh_op = load_wav(os.path.join(BASE_BRF2, "Hats", "[BRF2] Hat (1).wav"))

# Pontinho one-shot
s_pont = load_wav(os.path.join(REL, "Pontinho", "One-Shot", "JF No Beat - RF2 - One Shot 1.wav"))

# Find some good percussion loops
# Check loops that might work - find short loops
percs_dir = os.path.join(BASE_BRF2, "Percs")
shakers = []
for f in sorted(os.listdir(percs_dir)):
    if f.endswith('.wav'):
        y, sr_t = sf.read(os.path.join(percs_dir, f))
        if y.ndim > 1: y = y.mean(axis=1)
        dur = len(y)/sr_t
        if 0.2 < dur < 0.6:  # short percussion one-shots
            shakers.append(f)
        if len(shakers) >= 3: break

shaker_samples = []
for s in shakers:
    shaker_samples.append(load_wav(os.path.join(percs_dir, s)))

print(f"  Loaded {len(shaker_samples)} shakers")

# ============================================================
# BUILD TRACKS
# ============================================================
TOTAL_BARS = 48  # shorter, ~64s
TOTAL = int(TOTAL_BARS * BAR_S * SR)

track_808 = np.zeros(TOTAL, dtype=np.float64)
track_caixa = np.zeros(TOTAL, dtype=np.float64)
track_hat = np.zeros(TOTAL, dtype=np.float64)
track_perc = np.zeros(TOTAL, dtype=np.float64)

print(f"\nTotal: {TOTAL_BARS} bars = {TOTAL_BARS*BAR_S:.1f}s")

# ============================================================
# 808 PATTERN - Bailao style
# ============================================================
# Bailao 808: strong on beat 1, often also on beat 3
# With some 8th note variation for movement
print("Building 808...")
for bar in range(TOTAL_BARS):
    bs = int(bar * BAR_S * SR)
    
    if bar < 4:  # Intro - just pulse on 1
        place(track_808, s_808_fn_short, bs, amp=0.5)
    elif bar < 16:  # Verse 
        place(track_808, s_808_fn, bs, amp=0.8)
        place(track_808, s_808_fn_short, bs + int(2 * BEAT_S * SR), amp=0.6)
        # Syncopated hit on the 'and' of 3
        if bar % 2 == 0:
            place(track_808, s_808_fn_short, bs + int(2.5 * BEAT_S * SR), amp=0.4)
    elif bar < 32:  # Chorus - fuller
        place(track_808, s_808_fn, bs, amp=1.0)
        place(track_808, s_808_fn_short, bs + int(2 * BEAT_S * SR), amp=0.7)
        place(track_808, s_808_fn_short, bs + int(1 * BEAT_S * SR), amp=0.4)
        place(track_808, s_808_fn_short, bs + int(3 * BEAT_S * SR), amp=0.4)
        # Extra bounce
        place(track_808, s_808_fn_short, bs + int(0.5 * BEAT_S * SR), amp=0.3)
        place(track_808, s_808_fn_short, bs + int(2.5 * BEAT_S * SR), amp=0.3)
    else:  # Finale
        place(track_808, s_808_fn, bs, amp=1.0)
        place(track_808, s_808_fn_short, bs + int(2 * BEAT_S * SR), amp=0.8)
        place(track_808, s_808_fn_short, bs + int(1 * BEAT_S * SR), amp=0.5)
        place(track_808, s_808_fn_short, bs + int(3 * BEAT_S * SR), amp=0.5)
        place(track_808, s_808_fn_short, bs + int(0.5 * BEAT_S * SR), amp=0.4)
        place(track_808, s_808_fn_short, bs + int(2.5 * BEAT_S * SR), amp=0.4)

# ============================================================
# CAIXA PATTERN - 2 and 4 (funk standard)
# ============================================================
print("Building caixa...")
for bar in range(TOTAL_BARS):
    bs = int(bar * BAR_S * SR)
    if bar < 4: continue
    if bar < 16:  # Verse - single caixa
        place(track_caixa, s_caixa, bs + int(1.99 * BEAT_S * SR), amp=0.7)  # slight swing
        place(track_caixa, s_caixa, bs + int(3.99 * BEAT_S * SR), amp=0.7)
    else:  # Full
        caixa = s_caixa2 if bar % 2 == 0 else s_caixa  # alternate for interest
        place(track_caixa, caixa, bs + int(1.98 * BEAT_S * SR), amp=1.0)
        place(track_caixa, caixa, bs + int(3.98 * BEAT_S * SR), amp=1.0)

# ============================================================
# HI-HAT - 16th notes with swing
# ============================================================
print("Building hats...")
swing_amt = 0.12
for bar in range(TOTAL_BARS):
    bs = int(bar * BAR_S * SR)
    hat_vol = 0.25 if bar < 4 else (0.5 if bar < 16 else 0.7)
    
    for step in range(16):
        t = step / 16.0 * BAR_S
        if step % 2 == 1:
            t += swing_amt * 0.25 * BEAT_S
        pos = int(bs + t * SR)
        if pos >= TOTAL: break
        
        amp = hat_vol * (1.2 if step % 4 == 0 else 0.8)
        place(track_hat, s_hh_cl, pos, amp=amp)
    
    # Open hat accent
    if bar >= 16 and bar % 2 == 0:
        open_pos = int(bs + 3.75 * BEAT_S * SR)
        place(track_hat, s_hh_op, open_pos, amp=0.3)

# ============================================================
# PERCUSSION / SHAKERS
# ============================================================
print("Building percussion...")
for bar in range(8, TOTAL_BARS):
    bs = int(bar * BAR_S * SR)
    if len(shaker_samples) > 0:
        sh = shaker_samples[bar % len(shaker_samples)]
        # Shaker on 2& and 4&
        place(track_perc, sh, bs + int(2.5 * BEAT_S * SR), amp=0.2)
        place(track_perc, sh, bs + int(4.5 * BEAT_S * SR), amp=0.2)

# ============================================================
# MIX
# ============================================================
print("Mixing...")
# Mix levels
mix = (track_808 * 1.0 + track_caixa * 0.45 + track_hat * 0.18 + track_perc * 0.15)

# Normalize
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.92

print(f"Peak: {np.max(np.abs(mix)):.3f}, RMS: {np.sqrt(np.mean(mix**2)):.4f}")

# ============================================================
# MASTERING
# ============================================================
print("Mastering...")
from pedalboard import Pedalboard, Compressor, HighpassFilter, LowpassFilter, Gain, Limiter
board = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=28.0),
    Compressor(threshold_db=-16, ratio=3.0, attack_ms=5, release_ms=80),
    Gain(gain_db=2.5),
    Limiter(threshold_db=-0.5, release_ms=50),
])
mastered = board.process(mix, SR)
mastered = mastered / np.max(np.abs(mastered)) * 0.95

print(f"Mastered peak: {np.max(np.abs(mastered)):.3f}, RMS: {np.sqrt(np.mean(mastered**2)):.4f}")

# Convert to stereo by duplicating with slight width
stereo = np.zeros((len(mastered), 2), dtype=np.float64)
stereo[:, 0] = mastered * 0.8
stereo[:, 1] = mastered * 0.8
# Add width: put some percussion in sides
perc_side = track_perc * 0.1
stereo[:-len(perc_side), 0] += perc_side * 0.5
stereo[:-len(perc_side), 1] -= perc_side * 0.5

stereo = stereo / np.max(np.abs(stereo)) * 0.95

# Export
out = os.path.expandvars(r'%TEMP%\opencode\mundo_louco_beat_v2.wav')
sf.write(out, stereo, SR)
local = r"C:\Users\alerrandro\Music\Nova pasta (2)\mundo_louco_beat_v2.wav"
sf.write(local, stereo, SR)

print(f"\nExported: {local}")
print(f"Duration: {len(mastered)/SR:.1f}s = {TOTAL_BARS} bars @ {BPM} BPM")
print(f"Size: {os.path.getsize(local)/1024/1024:.1f}MB")
print("Done!")
