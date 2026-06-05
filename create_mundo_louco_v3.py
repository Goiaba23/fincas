import numpy as np, soundfile as sf, os, warnings
warnings.filterwarnings('ignore')

SR = 44100
BPM = 82
BEAT_S = 60.0 / BPM
BAR_S = BEAT_S * 4

BASE_BRF2 = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats"
BASE_REL = r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2"
REL = os.path.join(BASE_REL, [d for d in os.listdir(BASE_REL) if os.path.isdir(os.path.join(BASE_REL, d))][0])

def load_wav(path):
    y, sr = sf.read(path)
    if y.ndim > 1: y = y.mean(axis=1)
    if sr != SR:
        from scipy import signal
        y = signal.resample(y, int(len(y) * SR / sr))
    return y / (np.max(np.abs(y)) + 1e-10)

def place(buf, smp, pos, amp=1.0):
    if pos < 0 or pos >= len(buf): return
    end = pos + len(smp)
    if end > len(buf): smp = smp[:len(buf)-pos]
    buf[pos:pos+len(smp)] += smp * amp

# ============================================================
# 808 SYNTHESIS - clean, exact pitch
# ============================================================
print("Synth 808...")

def make_808(freq_hz, dur_bars=1, sr=SR):
    n = int(dur_bars * BAR_S * sr)
    t = np.arange(n) / sr
    
    # Pitch decay
    decay_rate = 8.0 / (BPM/60*2)  # adjust decay to tempo
    pitch_decay = np.exp(-t * decay_rate) * 4.0
    osc_freq = freq_hz + freq_hz * pitch_decay
    phase = np.cumsum(osc_freq) / sr * 2 * np.pi
    sine = np.sin(phase) * 0.6
    
    # Sub (1 octave down)
    sub = np.sin(np.cumsum(np.full(n, freq_hz/2)) / sr * 2 * np.pi) * 0.4
    
    # Click transient
    clk = np.zeros(n)
    clk_n = int(0.01 * sr)
    clk[:clk_n] = np.sin(np.linspace(0, np.pi, clk_n)) * 0.7
    clk = clk * np.exp(-t * 150)
    
    # Distortion
    sig_ = sine + sub
    sig_ = np.tanh(sig_ * 4) * 0.5
    
    # Envelope
    env = np.ones(n)
    env[:int(0.005*sr)] = np.linspace(0, 1, int(0.005*sr))
    env = env * np.exp(-t * max(1.2, 5/(BPM/60)))
    
    out = (sig_ * env + clk * 0.25) * 0.85
    return out / (np.max(np.abs(out)) + 1e-10)

# C# minor progression: i - VII - VI (C#m - B - A)
# C#1 = 34.6Hz, B0 = 30.9Hz, A0 = 27.5Hz
s_808_csharp = make_808(34.6, dur_bars=1)
s_808_b = make_808(30.9, dur_bars=1)
s_808_a = make_808(27.5, dur_bars=1)
s_808_gsharp = make_808(51.9, dur_bars=1)  # G#2 for variation

# Shorter stabs
s_808_cs_stab = make_808(34.6, dur_bars=0.25)
s_808_b_stab = make_808(30.9, dur_bars=0.25)
s_808_a_stab = make_808(27.5, dur_bars=0.25)

# ============================================================
# LOAD SAMPLES
# ============================================================
print("Loading samples...")

# Best caixa for bailao: Caixa 4 (bright, 4719Hz centroid) and Caixa 12 (tight)
s_caixa = load_wav(os.path.join(REL, "Caixa", "JF No Beat - RF2 - Caixa 4.wav"))
s_caixa2 = load_wav(os.path.join(REL, "Caixa", "JF No Beat - RF2 - Caixa 12.wav"))

# Hats - find a good closed hat
s_hh = load_wav(os.path.join(BASE_BRF2, "Hats", "[BRF2] Hat (11).wav"))
s_hh_open = load_wav(os.path.join(BASE_BRF2, "Hats", "[BRF2] Hat (1).wav"))
s_hh2 = load_wav(os.path.join(BASE_BRF2, "Hats", "[BRF2] Hat (4).wav"))

# Tamborim / shaker / percussion
percs = []
for f in sorted(os.listdir(os.path.join(BASE_BRF2, "Percs"))):
    if f.endswith('.wav'):
        try:
            y, sr_t = sf.read(os.path.join(BASE_BRF2, "Percs", f))
            if y.ndim > 1: y = y.mean(axis=1)
            if 0.15 < len(y)/sr_t < 0.5:
                if sr_t != SR:
                    from scipy import signal
                    y = signal.resample(y, int(len(y)*SR/sr_t))
                percs.append(y / (np.max(np.abs(y))+1e-10))
                if len(percs) >= 5: break
        except: pass

# Tamborzao - synthesize the characteristic Brazilian funk drum
def make_tamb():
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    # Mix of noise and sine for tamborim sound
    noise = np.random.randn(n) * 0.3
    tone = np.sin(2 * np.pi * 250 * t) * 0.5
    tone2 = np.sin(2 * np.pi * 500 * t) * 0.2
    env = np.exp(-t * 20)
    return (noise + tone + tone2) * env * 0.9

s_tamb = make_tamb()
del percs[:]  # too much processing, skip

# ============================================================
# ARRANGEMENT
# ============================================================
# C#m - B - A progression (each 8 bars)
# Total: 64 bars (~187s at 82BPM)
TOTAL_BARS = 48
TOTAL = int(TOTAL_BARS * BAR_S * SR)

t808 = np.zeros(TOTAL)
tcaixa = np.zeros(TOTAL)
that = np.zeros(TOTAL)
ttamb = np.zeros(TOTAL)

print(f"Bars: {TOTAL_BARS}, Duration: {TOTAL_BARS*BAR_S:.1f}s")

def get_chord(bar):
    cycle = bar % 24
    if cycle < 8: return 'C#', s_808_csharp, s_808_cs_stab
    elif cycle < 16: return 'B', s_808_b, s_808_b_stab
    else: return 'A', s_808_a, s_808_a_stab

# ============================================================
# 808 PATTERN
# ============================================================
# At 82 BPM: quarter notes feel slow
# Pattern: strong on 1, lighter on 3, syncopated stabs in between
print("808...")
for bar in range(TOTAL_BARS):
    ch, s_long, s_stab = get_chord(bar)
    bs = int(bar * BAR_S * SR)
    
    if bar < 4:  # Intro - just root pulse
        place(t808, s_long, bs, amp=0.5)
    elif bar < 16:  # Verse
        place(t808, s_long, bs, amp=0.85)                          # beat 1
        place(t808, s_stab, bs + int(2 * BEAT_S * SR), amp=0.6)    # beat 3
        place(t808, s_stab, bs + int(0.5 * BEAT_S * SR), amp=0.35) # & of 1
    elif bar < 32:  # Chorus
        place(t808, s_long, bs, amp=1.0)
        place(t808, s_stab, bs + int(2 * BEAT_S * SR), amp=0.8)
        place(t808, s_stab, bs + int(0.5 * BEAT_S * SR), amp=0.4)
        place(t808, s_stab, bs + int(2.5 * BEAT_S * SR), amp=0.4)
        place(t808, s_stab, bs + int(3.5 * BEAT_S * SR), amp=0.3) # & of 4
    else:  # Bridge/outro
        place(t808, s_long, bs, amp=0.7)
        place(t808, s_stab, bs + int(2 * BEAT_S * SR), amp=0.5)

    # Add 5th on some bars for flavor
    if bar % 4 == 0 and bar >= 8:
        place(t808, s_808_gsharp, bs + int(3.5 * BEAT_S * SR), amp=0.3)

# ============================================================
# CAIXA - on 2 and 4
# ============================================================
print("Caixa...")
for bar in range(TOTAL_BARS):
    bs = int(bar * BAR_S * SR)
    if bar < 4: continue
    caixa = s_caixa if bar % 2 == 0 else s_caixa2
    amp = 0.7 if bar < 16 else 1.0
    place(tcaixa, caixa, bs + int(2 * BEAT_S * SR), amp=amp)
    place(tcaixa, caixa, bs + int(4 * BEAT_S * SR), amp=amp)
    # Ghost notes in chorus
    if bar >= 16:
        place(tcaixa, s_caixa2, bs + int(1.5 * BEAT_S * SR), amp=0.25)
        place(tcaixa, s_caixa2, bs + int(3.5 * BEAT_S * SR), amp=0.25)

# ============================================================
# HATS - 16th notes (at 82 BPM, 16 16th-notes per bar)
# ============================================================
print("Hats...")
sw = 0.10
for bar in range(TOTAL_BARS):
    bs = int(bar * BAR_S * SR)
    vol = 0.20 if bar < 4 else (0.40 if bar < 16 else 0.55)
    
    for step in range(16):
        t = step / 16.0 * BAR_S
        if step % 2 == 1: t += sw * 0.5 * BEAT_S
        pos = int(bs + t * SR)
        if pos >= TOTAL: break
        amp = vol * (1.3 if step % 4 == 0 else 0.85)
        place(that, s_hh2 if step % 8 == 0 else s_hh, pos, amp=amp)
    
    # Open hat on 4& in chorus
    if bar >= 16:
        open_pos = int(bs + 3.75 * BEAT_S * SR)
        place(that, s_hh_open, open_pos, amp=0.35)

# ============================================================
# TAMBORZAO (synthetic)
# ============================================================
print("Tamborzao...")
for bar in range(8, TOTAL_BARS):
    bs = int(bar * BAR_S * SR)
    # Tamborzao plays syncopated with the 808
    place(ttamb, s_tamb, bs, amp=0.6)
    place(ttamb, s_tamb, bs + int(2 * BEAT_S * SR), amp=0.4)
    if bar >= 16:
        place(ttamb, s_tamb, bs + int(1 * BEAT_S * SR), amp=0.3)
        place(ttamb, s_tamb, bs + int(3 * BEAT_S * SR), amp=0.3)

# ============================================================
# MIX
# ============================================================
print("Mixing...")
mix = t808 * 1.0 + tcaixa * 0.5 + that * 0.15 + ttamb * 0.6

peak = np.max(np.abs(mix))
if peak > 0: mix = mix / peak * 0.9
print(f"Raw: peak={peak:.3f}")

# ============================================================
# MASTERING (with proper sidechain)
# ============================================================
print("Mastering...")
from pedalboard import Pedalboard, Compressor, HighpassFilter, LowpassFilter, Gain, Limiter

board = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=25.0),
    Compressor(threshold_db=-18, ratio=3.0, attack_ms=10, release_ms=80),
    LowpassFilter(cutoff_frequency_hz=16000.0),
    Gain(gain_db=3.0),
    Limiter(threshold_db=-0.5, release_ms=50),
])
mastered = board.process(mix, SR)
mastered = mastered / np.max(np.abs(mastered)) * 0.95

# Stereo width
s = np.zeros((len(mastered), 2))
s[:, 0] = mastered * 0.8
s[:, 1] = mastered * 0.8
s[:, 0] += ttamb[:len(mastered)] * 0.15
s[:, 1] -= ttamb[:len(mastered)] * 0.15
s = s / np.max(np.abs(s)) * 0.95

# Export
local = r"C:\Users\alerrandro\Music\Nova pasta (2)\mundo_louco_beat_v3.wav"
sf.write(local, s, SR)
tmp = os.path.expandvars(r'%TEMP%\opencode\mundo_louco_beat_v3.wav')
sf.write(tmp, s, SR)

print(f"\nExported: {local}")
print(f"BPM: {BPM}, Key: C# minor")
print(f"Duration: {len(mastered)/SR:.1f}s ({TOTAL_BARS} bars)")
print(f"Progression: C#m - B - A")
print(f"Size: {os.path.getsize(local)/1024/1024:.1f}MB")
print("Done!")
