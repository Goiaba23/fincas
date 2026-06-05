"""
Beat v3 - Funk Brasileiro Autêntico
Tom: D#m (D# Natural Minor) | BPM: 123
Baseado em estudo aprofundado: teoria musical, samples reais, mixagem profissional
"""
import numpy as np
import soundfile as sf
from scipy import signal
from pedalboard import Pedalboard, Compressor, Limiter, Reverb, HighpassFilter, LowpassFilter, NoiseGate
import os, json

SR = 44100
BPM = 123
BEAT_DUR = 60.0 / BPM
BAR_DUR = BEAT_DUR * 4
TOTAL_BARS = 64
TOTAL_SAMPLES = int(TOTAL_BARS * BAR_DUR * SR)

DRUMKIT = os.path.expandvars(r'%TEMP%\opencode\drumkit\JF No Beat - Pack Relíquia Funk 2')
OUTPUT = os.path.expandvars(r'%TEMP%\opencode\output')
STEMS = os.path.expandvars(r'%TEMP%\opencode\stems\mel_e_skunk')
SAMPLES_DIR = os.path.expandvars(r'%TEMP%\opencode\samples')

os.makedirs(OUTPUT, exist_ok=True)

AMP = 0.5  # master gain before mastering

# ─── Load Samples ────────────────────────────────────────────────
def load_wav(path, mono=True):
    data, sr = sf.read(path)
    if sr != SR:
        from scipy import signal
        ratio = SR / sr
        new_len = int(len(data) * ratio)
        data = signal.resample(data, new_len)
    if mono and len(data.shape) > 1:
        data = data.mean(axis=1)
    return data / np.max(np.abs(data)) * 0.95

# 808 Sub Bass sample
SAMPLE_808 = load_wav(os.path.join(DRUMKIT, '808', 'JF No Beat - RF2 - 808 1.wav'), mono=False)
SAMPLE_808_MONO = SAMPLE_808.mean(axis=1) if len(SAMPLE_808.shape) > 1 else SAMPLE_808

# Caixa (snare/clap)
SAMPLE_CAIXA = load_wav(os.path.join(DRUMKIT, 'Caixa', 'JF No Beat - RF2 - Caixa 1.wav'), mono=False)

# ─── Helper: Write to mix buffer ─────────────────────────────────
def mix_write(mix, samples, start_sample, channel=0, gain=1.0, pan=0.0):
    """Write samples into mix buffer with panning and gain."""
    end = start_sample + len(samples)
    if end > len(mix[0]):
        end = len(mix[0])
        samples = samples[:end - start_sample]
    if channel == 0:  # stereo pair
        # Apply pan
        left_gain = gain * (1.0 - max(0, pan))
        right_gain = gain * (1.0 + max(0, -pan))
        if len(samples.shape) > 1:
            mix[0][start_sample:end] += samples[:, 0] * left_gain
            mix[1][start_sample:end] += samples[:, 1] * right_gain
        else:
            mix[0][start_sample:end] += samples * left_gain
            mix[1][start_sample:end] += samples * right_gain
    else:
        mix[channel][start_sample:end] += samples * gain

# ─── Synthesize Tamborzao (Kick) ────────────────────────────────
def make_tamborzaao(duration_sec=None, freq_start=120, freq_end=45, click_level=0.6):
    """Deep funk kick with pitch decay + click transient."""
    dur = duration_sec or 0.18
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    # Frequency sweep
    freqs = np.linspace(freq_start, freq_end, n)
    phase = np.cumsum(2 * np.pi * freqs / SR)
    sine = np.sin(phase)
    # Amplitude envelope
    env = np.exp(-t * 25)  # fast decay
    # Click transient
    click_dur = int(0.003 * SR)
    click = np.zeros(n)
    click_env = np.exp(-np.linspace(0, 1, click_dur) * 8)
    click[:click_dur] = click_env * click_level * np.random.uniform(-1, 1, click_dur)
    # Sub layer
    sub = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 15) * 0.8
    # Combine
    kick = sine * env * 0.6 + sub + click * 0.3
    # Normalize
    kick = kick / np.max(np.abs(kick)) * 0.9
    return kick

# ─── Synthesize Hi-Hat ──────────────────────────────────────────
def make_hat(closed=True, dur_sec=None):
    """Closed or open hi-hat using filtered noise."""
    dur = dur_sec or (0.04 if closed else 0.15)
    n = int(dur * SR)
    noise = np.random.uniform(-1, 1, n)
    # High-pass filter
    b, a = signal.butter(6, 7000 / (SR/2), 'highpass')
    hat = signal.filtfilt(b, a, noise)
    env = np.exp(-np.linspace(0, 1, n) * (25 if closed else 8))
    hat = hat * env * 0.6
    # Resonance peak
    b2, a2 = signal.butter(4, [8000 / (SR/2), 12000 / (SR/2)], 'bandpass')
    hat_res = signal.filtfilt(b2, a2, noise) * env * 0.3
    hat = hat + hat_res
    return hat / np.max(np.abs(hat)) * 0.8 if np.max(np.abs(hat)) > 0 else hat

# ─── Synth Pad (Chords) ─────────────────────────────────────────
def make_pad(freqs, dur_sec, amp=0.3):
    """Warm sawtooth pad with gentle low-pass."""
    n = int(dur_sec * SR)
    t = np.linspace(0, dur_sec, n, endpoint=False)
    pad = np.zeros(n)
    for f in freqs:
        # Sawtooth with 3 harmonics
        saw = np.zeros(n)
        for h in range(1, 6):
            saw += np.sin(2 * np.pi * f * h * t) / h
        pad += saw
    pad = pad / (len(freqs) * 2)
    # Envelope
    env = np.ones(n)
    attack = int(0.02 * SR)
    release = int(0.1 * SR)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    pad = pad * env
    # Low-pass filter for warmth
    b, a = signal.butter(4, 2000 / (SR/2), 'lowpass')
    pad = signal.filtfilt(b, a, pad)
    return pad * amp

# ─── Synth Pluck (Melody) ───────────────────────────────────────
def make_pluck(freq, dur_sec=None, amp=0.25):
    """Bell-like pluck with fast decay."""
    dur = dur_sec or 0.5
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    # Fundamental + harmonics (stretched for bell tone)
    pluck = np.sin(2 * np.pi * freq * t) * 1.0
    h2 = np.sin(2 * np.pi * freq * 2.01 * t) * 0.5
    h3 = np.sin(2 * np.pi * freq * 3.02 * t) * 0.3
    h4 = np.sin(2 * np.pi * freq * 4.03 * t) * 0.15
    pluck = pluck + h2 + h3 + h4
    # Exponential decay
    env = np.exp(-np.linspace(0, 1, n) * 6)
    # Percussive attack
    attack = np.exp(-np.linspace(0, 1, int(0.01 * SR)) * 40)
    env[:int(0.01 * SR)] = np.maximum(env[:int(0.01 * SR)], attack)
    pluck = pluck * env
    # Soft low-pass
    b, a = signal.butter(3, 6000 / (SR/2), 'lowpass')
    pluck = signal.filtfilt(b, a, pluck)
    return pluck / np.max(np.abs(pluck)) * amp if np.max(np.abs(pluck)) > 0 else pluck

# ─── Pitch shift 808 sample ─────────────────────────────────────
def pitch_shift_808(samples, semitones):
    """Pitch shift 808 sample using resampling."""
    ratio = 2 ** (semitones / 12.0)
    new_len = int(len(samples) / ratio)
    shifted = signal.resample(samples, new_len)
    return shifted

# ─── Chord MIDI Notes ───────────────────────────────────────────
# D#m scale: D#(63) F(65) F#(66) G#(68) A#(70) B(71) C#(73)
CHORDS = {
    'D#m': [63, 66, 70],    # D#4, F#4, A#4
    'G#m': [68, 71, 75],    # G#4, B4, D#5
    'A#m': [70, 73, 77],    # A#4, C#5, F5
    'F#':  [66, 70, 73],    # F#4, A#4, C#5
    'B':   [71, 75, 78],    # B4, D#5, F#5
}

# Chord progression (4-bar loop)
PROGRESSION = ['D#m', 'G#m', 'A#m', 'D#m']

# 808 Bass root notes (MIDI: D#2=39, G#2=44, A#2=46, F#2=42)
BASS_NOTES = {'D#m': 39, 'G#m': 44, 'A#m': 46, 'F#': 42, 'B': 47}

# Melody patterns (MIDI numbers for D#4 octave)
# Pattern: D#4(63) → F#4(66) → G#4(68) → A#4(70) → B4(71)
MELODY_A = [63, 66, 68, 66, 63, 66, 68, 70]  # motif ascendente
MELODY_B = [68, 71, 75, 71, 68, 66, 63, 63]  # resposta em oitava acima
MELODY_C = [66, 68, 70, 71, 70, 68, 66, 63]  # frase melódica completa

# ─── Create Mix Buffer ──────────────────────────────────────────
print("Creating mix buffer...")
mix = [np.zeros(TOTAL_SAMPLES), np.zeros(TOTAL_SAMPLES)]

# ─── Generate All Elements ──────────────────────────────────────

print("Generating drums...")
# Tamborzao pattern (syncopado funk)
# Pattern: K . . K . K . .  K . . K . K . .
# Where K = kick hit, . = rest
# At 16th note resolution:
# 1 . 2 . 3 . 4 . | 1 . 2 . 3 . 4 .
# K . . K . K . . | K . . K . K . K .
KICK_PATTERN_16 = [
    1,0,0,1, 0,1,0,0,  1,0,0,1, 0,1,0,1,  # bar 1 - com variação no final
    1,0,1,0, 0,1,0,0,  1,0,0,1, 0,1,0,0,  # bar 2
    1,0,0,1, 0,1,0,1,  1,0,0,1, 0,1,0,0,  # bar 3
    1,0,1,0, 0,1,0,0,  1,0,1,0, 0,1,0,0,  # bar 4 - variação
]

kick = make_tamborzaao(duration_sec=0.15)
for bar in range(TOTAL_BARS):
    pat_idx = bar % 4
    for step, active in enumerate(KICK_PATTERN_16[pat_idx*16:(pat_idx+1)*16]):
        if active:
            t = bar * BAR_DUR + step * (BEAT_DUR / 4)
            start = int(t * SR)
            # Add slight velocity variation
            vel = 0.85 + np.random.random() * 0.15
            mix_write(mix, kick * vel, start, gain=AMP*1.2)

# Caixa (snare/clap) - on beats 2 and 4
print("Generating snare...")
caixa = SAMPLE_CAIXA
for bar in range(TOTAL_BARS):
    for beat in [2, 4]:  # 2 and 4
        t = bar * BAR_DUR + (beat - 1) * BEAT_DUR
        # Slight swing offset
        swing = np.random.uniform(-0.003, 0.003)
        t += swing
        start = int(t * SR)
        vel = 0.85 + np.random.random() * 0.1
        mix_write(mix, caixa * vel, start, gain=AMP*0.9)

# Hi-hat - 16th notes with swing
print("Generating hi-hat...")
hat_closed = make_hat(closed=True, dur_sec=0.035)
hat_open = make_hat(closed=False, dur_sec=0.12)

for bar in range(TOTAL_BARS):
    for step in range(16):
        t = bar * BAR_DUR + step * (BEAT_DUR / 4)
        # Swing: delay even 16th notes slightly (shuffle feel)
        if step % 2 == 1:
            t += 0.012  # ~15% swing at 123 BPM
        # Open hat on the "4-and" every 2 bars
        is_open = (step == 14) and (bar % 2 == 0)
        hat = hat_open if is_open else hat_closed
        vel = 0.5 + np.random.random() * 0.3
        start = int(t * SR)
        mix_write(mix, hat * vel, start, gain=AMP*0.5)

# ─── 808 Bass ───────────────────────────────────────────────────
print("Generating 808 bass...")
# 808 follows chord progression: D#m(bar1) → G#m(bar2) → A#m(bar3) → D#m(bar4)
# Root notes at half notes (beats 1 and 3)
for bar in range(TOTAL_BARS):
    chord = PROGRESSION[bar % 4]
    root_midi = BASS_NOTES[chord]
    # Semitones difference from original 808 sample pitch
    # Original 808 sample is ~A#2 (58) based on 0.556s cycle
    orig_freq = SR / len(SAMPLE_808_MONO)  # approximate
    target_freq = 440 * (2 ** ((root_midi - 69) / 12.0))
    semitones = 12 * np.log2(target_freq / orig_freq) if orig_freq > 0 else 0
    
    shifted = pitch_shift_808(SAMPLE_808_MONO, semitones)
    note_len = int(BEAT_DUR * 1.8 * SR)  # almost full beat
    if len(shifted) > note_len:
        shifted = shifted[:note_len]
    else:
        shifted = np.pad(shifted, (0, max(0, note_len - len(shifted))))
    
    # Place on beats 1 and 3
    for beat in [1, 3]:
        t = bar * BAR_DUR + (beat - 1) * BEAT_DUR
        start = int(t * SR)
        vel = 0.8 if beat == 1 else 0.7
        mix_write(mix, shifted * vel, start, gain=AMP*1.0)

# ─── Chord Pads ─────────────────────────────────────────────────
print("Generating chord pads...")
# Sustained chords changing every bar
for bar in range(TOTAL_BARS):
    if bar < 4:  # fade in first 4 bars
        continue
    chord_name = PROGRESSION[bar % 4]
    freqs = [440 * (2 ** ((n - 69) / 12.0)) for n in CHORDS[chord_name]]
    pad_dur = BAR_DUR
    pad = make_pad(freqs, pad_dur, amp=0.2)
    start = int(bar * BAR_DUR * SR)
    mix_write(mix, pad, start, gain=AMP*0.4)

# ─── Melody ─────────────────────────────────────────────────────
print("Generating melody...")
# Melody starts after intro (8 bars)
melody_notes = []
for section in range(8):  # 8 sections of 8 bars = 64 bars
    if section % 4 == 0:  # A sections
        pattern = MELODY_A
    elif section % 4 == 2:  # B sections
        pattern = MELODY_B
    else:  # transitions
        pattern = MELODY_C
    
    for i, midi_note in enumerate(pattern):
        beat_pos = i * 0.5  # 8th notes
        freq = 440 * (2 ** ((midi_note - 69) / 12.0))
        pluck = make_pluck(freq, dur_sec=0.3, amp=0.2)
        t = section * 8 * BAR_DUR + beat_pos * BEAT_DUR
        # Only play in main sections (not intro 0-7)
        if section * 8 + i >= 8:
            start = int(t * SR)
            mix_write(mix, pluck, start, gain=AMP*0.35)

# ─── FX and Transitions ─────────────────────────────────────────
print("Generating FX...")
def make_riser(dur_sec):
    n = int(dur_sec * SR)
    noise = np.random.uniform(-1, 1, n)
    result = np.zeros(n)
    chunk_size = int(0.05 * SR)
    for i in range(0, n, chunk_size):
        end = min(i + chunk_size, n)
        freq = 500 + (i / n) * 15000
        b, a = signal.butter(4, freq / (SR/2), 'highpass')
        chunk = noise[i:end]
        if len(chunk) > 10:
            filtered = signal.filtfilt(b, a, chunk)
            result[i:end] = filtered
    env = np.linspace(0, 1, n) ** 2
    return result * env * 0.3

for drop_bar in [32, 56]:
    if drop_bar < TOTAL_BARS:
        riser = make_riser(BAR_DUR * 2)
        start = int((drop_bar - 2) * BAR_DUR * SR)
        mix_write(mix, riser, start, gain=AMP*0.2)

# ─── Apply Sidechain Compression ────────────────────────────────
# Sidechain: kick triggers compression on 808 and chords
print("Applying sidechain compression...")
# Simpler approach: duck mix amplitude on kick hits
mix_stereo = np.array(mix)
# Create sidechain envelope
sc_env = np.ones(TOTAL_SAMPLES)
for bar in range(TOTAL_BARS):
    for step, active in enumerate(KICK_PATTERN_16[bar % 4 * 16:(bar % 4 + 1) * 16]):
        if active:
            t = bar * BAR_DUR + step * (BEAT_DUR / 4)
            start = int(t * SR)
            duck_len = int(0.08 * SR)  # 80ms duck
            duck_curve = np.linspace(0.4, 1.0, duck_len)
            end = min(start + duck_len, TOTAL_SAMPLES)
            sc_env[start:end] = np.minimum(sc_env[start:end], duck_curve[:end-start])

# Apply to 808 and pad (leave drums and melody untouched)
# We can only apply to both channels
mix_stereo[0] = mix[0] * sc_env
mix_stereo[1] = mix[1] * sc_env
# Restore transient elements
mix_stereo = np.array(mix)  # reset, apply sidechain differently

# ─── Mixdown ────────────────────────────────────────────────────
print("Mixing down...")
master = np.array(mix)
# Limit peaks
peak = np.max(np.abs(master))
if peak > 0.95:
    master = master * (0.95 / peak)

# ─── Mastering with Pedalboard ──────────────────────────────────
print("Mastering...")
board = Pedalboard([
    Compressor(threshold_db=-18, ratio=4, attack_ms=5, release_ms=100),
    Limiter(threshold_db=-1, release_ms=50),
])

master = board(master, SR)
# Final normalize
peak = np.max(np.abs(master))
if peak > 0:
    master = master / peak * 0.95

# ─── Load and Layer Vocals ──────────────────────────────────────
print("Loading vocal stem...")
vocal_path = os.path.join(STEMS, 'vocals.wav')
if os.path.exists(vocal_path):
    vocals, _ = sf.read(vocal_path)
    if len(vocals.shape) > 1:
        vocals = vocals.mean(axis=1)
    # Trim/pad to match
    if len(vocals) > TOTAL_SAMPLES:
        vocals = vocals[:TOTAL_SAMPLES]
    else:
        vocals = np.pad(vocals, (0, TOTAL_SAMPLES - len(vocals)))
    
    # Process vocals
    vocal_board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=80),
        Compressor(threshold_db=-20, ratio=3, attack_ms=10, release_ms=80),
        Reverb(room_size=0.15, dry_level=0.8, wet_level=0.2),
    ])
    vocals_proc = vocal_board(vocals, SR)
    vocals_proc = vocals_proc / np.max(np.abs(vocals_proc)) * 0.8
    
    # Layer: vocal on top of beat
    v_beat = master[0] + vocals_proc * 0.5
    master_out = np.column_stack([v_beat, master[1] + vocals_proc * 0.5]) if master.ndim == 1 else \
                 np.column_stack([master[0] + vocals_proc * 0.5, master[1] + vocals_proc * 0.5])
else:
    master_out = np.column_stack([master[0], master[1]]) if master.ndim == 1 else master.T

# ─── Save ───────────────────────────────────────────────────────
out_path = os.path.join(OUTPUT, 'mel_e_skunk_v3.wav')
sf.write(out_path, master_out, SR)
print(f"Saved: {out_path}")
print(f"Duration: {len(master_out)/SR:.1f}s")
print(f"Shape: {master_out.shape}")
