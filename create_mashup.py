"""
Create a mashup of 2Pac - Hit 'Em Up (Am, 95 BPM) + Kanye West - Can't Tell Me Nothing (Cm/Fm, 80 BPM)
Blend key: Cm (5A), target BPM: 95

Strategy:
1. Load both tracks with librosa
2. Separate Can't Tell Me Nothing into vocals/no-vocals using demucs
3. Time-stretch Can't Tell Me Nothing instrumental from 80 to 95 BPM
4. Pitch-shift Hit 'Em Up from Am to Cm (+3 semitones) 
5. Create arrangement: intro with Kanye chords, drop with Hit 'Em Up bassline + drums
6. Mix and export
"""

import librosa
import soundfile as sf
import numpy as np
import os
import tempfile

TEMP = os.environ.get('TEMP') + '\\opencode\\audio'
OUTPUT = os.environ.get('TEMP') + '\\opencode\\output'
os.makedirs(OUTPUT, exist_ok=True)

HIT_EM_UP = os.path.join(TEMP, 'hit_em_up.wav')
CANT_TELL = os.path.join(TEMP, 'cant_tell.wav')

SR = 44100  # target sample rate

print("Loading audio files...")
hit, sr_hit = librosa.load(HIT_EM_UP, sr=SR, mono=False)
cant, sr_cant = librosa.load(CANT_TELL, sr=SR, mono=False)

print(f"Hit 'Em Up: {hit.shape[1]/SR:.1f}s, shape={hit.shape}")
print(f"Can't Tell: {cant.shape[1]/SR:.1f}s, shape={cant.shape}")

# --- STEP 1: Demucs separation on Can't Tell Me Nothing ---
# We use demucs Python API to avoid CLI issues
print("\n--- Demucs: separating Can't Tell Me Nothing ---")
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torch

model = get_model('htdemucs')
model.eval()
# Use CPU if no CUDA
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
print(f"Using device: {device}")

# Load with librosa and convert to tensor format demucs expects
# demucs expects (batch, channels, time) float32 tensor
wav_cant_t = torch.from_numpy(cant).float().unsqueeze(0)  # (1, 2, T)
if device == 'cuda':
    wav_cant_t = wav_cant_t.cuda()

print("Running demucs (this will take a while)...")
with torch.no_grad():
    sources = apply_model(model, wav_cant_t, device=device, shifts=1, split=True, overlap=0.25, progress=True)

# sources shape: (1, 4, 2, T) - batch, sources (drums,bass,other,vocals), channels, time
sources_np = sources[0].cpu().numpy()  # (4, 2, T)
print(f"Sources shape: {sources_np.shape}")

# Index: 0=drums, 1=bass, 2=other, 3=vocals
drums = sources_np[0]  # (2, T)
bass = sources_np[1]   # (2, T)
other = sources_np[2]  # (2, T) - this has the synth pads, melodies etc.
vocals = sources_np[3] # (2, T)

# Save individual stems for reference
sf.write(os.path.join(OUTPUT, 'cant_tell_vocals.wav'), vocals.T, SR)
sf.write(os.path.join(OUTPUT, 'cant_tell_drums.wav'), drums.T, SR)
sf.write(os.path.join(OUTPUT, 'cant_tell_bass.wav'), bass.T, SR)
sf.write(os.path.join(OUTPUT, 'cant_tell_other.wav'), other.T, SR)
print("Saved demucs stems to output directory")

# Create instrumental = drums + bass + other
cant_instrumental = drums + bass + other
sf.write(os.path.join(OUTPUT, 'cant_tell_instrumental.wav'), cant_instrumental.T, SR)

# Also create just "other" + drums for the backbone (leave out bass - we'll use Hit 'Em Up's)
cant_backbone = other + drums
sf.write(os.path.join(OUTPUT, 'cant_tell_backbone.wav'), cant_backbone.T, SR)

print("\n--- Stem separation complete! ---")

# --- STEP 2: Time-stretch Can't Tell Me Nothing from 80 to 95 BPM ---
print("\n--- Time-stretching Can't Tell Me Nothing (80 -> 95 BPM) ---")
stretch_ratio = 95.0 / 80.0

# Stretch both stereo channels using librosa phase vocoder
cant_stretched_channels = []
for ch in range(2):
    print(f"  Stretching channel {ch}...")
    cant_stretched_channels.append(librosa.effects.time_stretch(cant_instrumental[ch], rate=stretch_ratio))
cant_stretched = np.array(cant_stretched_channels)

cant_tell_original_len = cant_instrumental.shape[1]
cant_stretched_len = cant_stretched.shape[1]
print(f"  Original length: {cant_tell_original_len/SR:.1f}s")
print(f"  Stretched length: {cant_stretched_len/SR:.1f}s")

sf.write(os.path.join(OUTPUT, 'cant_tell_stretched.wav'), cant_stretched.T, SR)

# --- STEP 3: Pitch-shift Hit 'Em Up from Am to Cm (+3 semitones) ---
print("\n--- Pitch-shifting Hit 'Em Up (Am -> Cm, +3 semitones) ---")
hit_pitched = np.zeros_like(hit)
for ch in range(2):
    print(f"  Shifting channel {ch}...")
    hit_pitched[ch] = librosa.effects.pitch_shift(hit[ch], sr=SR, n_steps=3)

sf.write(os.path.join(OUTPUT, 'hit_em_up_pitched.wav'), hit_pitched.T, SR)

# --- STEP 4: Create the mashup arrangement ---
print("\n--- Creating mashup arrangement ---")

# Use Can't Tell Me Nothing instrumental as the backbone
# Layer Hit 'Em Up elements on top

# Take the first section of Can't Tell Me Nothing (let's say first 30 secs stretched)
# and arrange as: intro (Kanye only) -> drop (both) -> section B -> outtro

# Duration: let's make a ~2 minute mashup
MASHUP_DURATION_SEC = 60  # 1 minute for now

def get_section(audio, start_sec, end_sec, sr=SR):
    """Extract section from stereo audio array (2, T)"""
    start_sample = int(start_sec * sr)
    end_sample = int(end_sec * sr)
    if start_sample >= audio.shape[1]:
        start_sample = 0
    if end_sample > audio.shape[1]:
        end_sample = audio.shape[1]
    return audio[:, start_sample:end_sample]

# Arrangement (in seconds at 95 BPM, each bar = 60/95*4 = 2.526s)
BAR = 60/95*4  # 4/4 time

# Section A: Intro - Can't Tell Me Nothing backbone only (8 bars)
# Section B: Drop - add Hit 'Em Up elements (16 bars)
# Section C: Breakdown (8 bars)
# Section D: Final drop (16 bars)

mashup_parts = []

# Intro (8 bars = ~20s) - just Kanye instrumental
intro_dur = 8 * BAR
intro = get_section(cant_stretched, 0, intro_dur)
intro = intro * 0.7  # lower volume for intro
mashup_parts.append(intro)

# Drop (16 bars = ~40s) - Kanye + elements from Hit 'Em Up
drop_dur = 16 * BAR
kanye_drop = get_section(cant_stretched, intro_dur, intro_dur + drop_dur)
hit_drop = get_section(hit_pitched, intro_dur, intro_dur + drop_dur)

# Mix: 70% Kanye, 50% Hit 'Em Up
drop_mix = kanye_drop * 0.7 + hit_drop * 0.5
mashup_parts.append(drop_mix)

# Concatenate all parts
mashup = np.concatenate(mashup_parts, axis=1)

# Normalize to prevent clipping
max_val = np.max(np.abs(mashup))
if max_val > 0.95:
    mashup = mashup / max_val * 0.95

# Export
output_path = os.path.join(OUTPUT, 'mashup_hit_em_cant_tell.wav')
sf.write(output_path, mashup.T, SR)
print(f"\n Mashup saved to: {output_path}")
print(f"   Duration: {mashup.shape[1]/SR:.1f}s")
print(f"   Format: {SR}Hz, stereo 16-bit WAV")

# Also save sections separately
sf.write(os.path.join(OUTPUT, 'section_intro.wav'), intro.T, SR)
sf.write(os.path.join(OUTPUT, 'section_drop.wav'), drop_mix.T, SR)

print("\nDone! Open", output_path, "in your audio player or import into FL Studio.")
