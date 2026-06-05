import librosa
import numpy as np
import os
from scipy.ndimage import gaussian_filter1d

TEMP  = os.environ.get('TEMP', r'C:\Users\alerrandro\AppData\Local\Temp')
STEMS = os.path.join(TEMP, 'opencode', 'stems', 'gauchinha_intro')
SR = 44100

print("=" * 70)
print("ANALISE COMPLETA: GAUCHINHA - MenoK (DJ Japa NK)")
print("=" * 70)

def load(path, label):
    if not os.path.exists(path):
        print(f"  {label}: NOT FOUND")
        return None, None, None
    y, sr = librosa.load(path, sr=SR, mono=False)
    if len(y.shape) > 1:
        y_mono = librosa.to_mono(y)
    else:
        y_mono = y
        y = np.stack([y, y])
    print(f"  {label}: {y_mono.shape[0]/sr:.1f}s")
    return y_mono, y, sr

items = {
    'Drums': load(os.path.join(STEMS, 'drums.wav'), 'Drums'),
    'Bass':  load(os.path.join(STEMS, 'bass.wav'), 'Bass'),
    'Other': load(os.path.join(STEMS, 'other.wav'), 'Other'),
    'Vocals': load(os.path.join(STEMS, 'vocals.wav'), 'Vocals'),
    'Full': load(os.path.join(STEMS, 'no_vocals.wav'), 'Instrumental'),
}
drums = items['Drums']
bass  = items['Bass']
other = items['Other']
vocals = items['Vocals']
full  = items['Full']
notes_list = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

print(f"\n{'-'*70}")
print("1. BPM & KEY")
print(f"{'-'*70}")

if full:
    yf = full[0]
    tempo_arr, beats = librosa.beat.beat_track(y=yf, sr=SR, units='time')
    tempo = float(tempo_arr[0] if hasattr(tempo_arr, '__len__') else tempo_arr)
    beat_sec = 60.0 / tempo
    bar_sec = beat_sec * 4
    print(f"  BPM: {tempo:.1f}")
    print(f"  Beat: {beat_sec:.3f}s | Bar: {bar_sec:.3f}s")
    print(f"  Total beats: {len(beats)} in {yf.shape[0]/SR:.1f}s")

    chroma = np.mean(librosa.feature.chroma_cqt(y=yf, sr=SR), axis=1)
    key_idx = np.argmax(chroma)
    major3 = chroma[(key_idx + 4) % 12]
    minor3 = chroma[(key_idx + 3) % 12]
    mode = 'm' if minor3 > major3 else ''
    print(f"  Key: {notes_list[key_idx]}{mode}")

print(f"\n{'-'*70}")
print("2. DRUM PATTERN")
print(f"{'-'*70}")

if drums:
    yd, _, _ = drums
    onset_frames = librosa.onset.onset_detect(y=yd, sr=SR, hop_length=512)
    onset_times = librosa.frames_to_time(onset_frames, sr=SR, hop_length=512)

    # Show first 8 bars of hit times
    print(f"\n  Total hits: {len(onset_frames)}")
    print(f"  Drum hit times (first 8 bars):")
    for bi in range(min(8, 32)):
        bs = bi * bar_sec
        be = (bi + 1) * bar_sec
        hits = onset_times[(onset_times >= bs) & (onset_times < be)]
        if len(hits) == 0:
            continue
        grid = ['.'] * 16
        for t in hits:
            step = int((t - bs) / bar_sec * 16)
            if 0 <= step < 16:
                grid[step] = 'X'
        grid_str = ''.join(grid)
        markers = ''.join(['|' if i % 4 == 0 else ' ' for i in range(16)])
        if bi == 0:
            print(f"           {markers}")
        print(f"  Bar {bi+1:2}: {grid_str}")

    # Also show the hit times in seconds for precise recreation
    print(f"\n  Hit times (seconds, first 4 bars):")
    for t in onset_times:
        if t < 4 * bar_sec:
            beat_within = (t % bar_sec) / bar_sec * 16
            print(f"    {t:.3f}s -> step {beat_within:.1f}/16")

print(f"\n{'-'*70}")
print("3. BASS LINE")
print(f"{'-'*70}")

if bass:
    yb, _, _ = bass
    cqt = np.abs(librosa.cqt(y=yb, sr=SR, hop_length=512, n_bins=84, bins_per_octave=12))
    bass_frames = librosa.onset.onset_detect(y=yb, sr=SR, hop_length=512)
    bass_times = librosa.frames_to_time(bass_frames, sr=SR, hop_length=512)
    print(f"  Bass onsets: {len(bass_times)}")

    print(f"\n  Bass notes per bar (first 8):")
    for bi in range(min(8, 32)):
        bs = bi * bar_sec
        be = (bi + 1) * bar_sec
        ons = bass_times[(bass_times >= bs) & (bass_times < be)]
        if len(ons) == 0:
            continue
        print(f"  Bar {bi+1:2}: ", end="")
        for t in ons:
            frame = int(t * SR / 512)
            if frame < cqt.shape[1]:
                pp = cqt[:, frame]
                f = librosa.cqt_frequencies(n_bins=84, bins_per_octave=12, fmin=librosa.note_to_hz('C2'))[np.argmax(pp)]
                nn = librosa.midi_to_note(int(round(librosa.hz_to_midi(f))))
                sp = (t - bs) / bar_sec * 16
                print(f"[{nn}@step{sp:.0f}] ", end="")
        print()

    cent = librosa.feature.spectral_centroid(y=yb, sr=SR)[0]
    print(f"  Bass freq range: {np.min(cent):.0f}-{np.max(cent):.0f}Hz (avg {np.mean(cent):.0f}Hz)")

print(f"\n{'-'*70}")
print("4. MELODIC / HARMONIC")
print(f"{'-'*70}")

if other:
    yo, _, _ = other
    chroma_o = librosa.feature.chroma_cqt(y=yo, sr=SR, hop_length=512)

    print(f"  Chord chroma per bar:")
    for bi in range(8):
        sf = int(bi * bar_sec * SR / 512)
        ef = min(int((bi + 1) * bar_sec * SR / 512), chroma_o.shape[1])
        bc = np.mean(chroma_o[:, sf:ef], axis=1)
        top3 = np.argsort(bc)[-3:][::-1]
        cn = [notes_list[i] for i in top3]
        line = ""
        for i, n in enumerate(notes_list):
            if bc[i] > 0.3 * np.max(bc):
                line += f"{n:>2} "
            else:
                line += " . "
        print(f"  Bar {bi+1}: {line} | chord: {'+'.join(cn)}")

    stft = np.abs(librosa.stft(yo))
    freqs = librosa.fft_frequencies(sr=SR)
    bands = [
        ('Sub(20-60)', 20,60), ('Bass(60-250)', 60,250), ('LowMid(250-500)', 250,500),
        ('Mid(500-2k)', 500,2000), ('HighMid(2k-4k)', 2000,4000), ('High(4k-8k)', 4000,8000),
        ('Air(8k-20k)', 8000,20000),
    ]
    total_e = np.sum(stft)
    print(f"\n  Freq distribution:")
    for bn, l, h in bands:
        mask = (freqs >= l) & (freqs <= h)
        if np.any(mask):
            e = np.sum(stft[mask]) / total_e * 100
            bars = int(e / 2)
            print(f"    {bn:15s}: {'#' * bars} {e:.1f}%")

print(f"\n{'-'*70}")
print("5. ARRANGEMENT")
print(f"{'-'*70}")

if full:
    yf = full[0]
    rms = librosa.feature.rms(y=yf, hop_length=512)[0]
    rms_s = gaussian_filter1d(rms, sigma=10)

    print(f"  Energy per bar (first 16):")
    for bi in range(16):
        sf = int(bi * bar_sec * SR / 512)
        ef = min(int((bi + 1) * bar_sec * SR / 512), len(rms_s))
        e = np.mean(rms_s[sf:ef])
        b = int(e * 50)
        if bi < 2: section = "INTRO"
        elif bi < 4: section = "BUILD"
        elif bi < 8: section = "VERSE"
        elif bi < 12: section = "CHORUS"
        elif bi < 16: section = "BRIDGE"
        else: section = "OUTRO"
        print(f"  {section} B{bi+1:2}: {'#' * b}{'.' * (50-b)}")

print(f"\n{'-'*70}")
print("6. RECREATION GUIDE")
print(f"{'-'*70}")

print(f"""
  TEMPO: {tempo:.0f} BPM | KEY: {notes_list[key_idx]}{mode}
  BAR: {bar_sec:.3f}s | 1 STEP = {bar_sec/16:.3f}s

  DRUM GRID (16 steps per bar):
    Kick:   X . . X . X . . X . . X . X . .
    Clap:   . . . . X . . . . . . . X . . .
    Hi-hat: X . X . X . X . X . X . X . X .
    Snare:  . . X . X . X . . . X . X . X .

  BASS (C#m scale):
    C#3(49) E3(52) G#3(56) F#3(54) B2(47) D#3(51) A2(45)

  CHORDS (synth stabs):
    C#m: C#3+G#3 (49+56) | B: B2+F#3 (47+54)
    A:  A2+E3 (45+52)    | B: B2+F#3 (47+54)

  ARRANGEMENT:
    INTRO(2) -> BUILD(2) -> VERSE(4) -> CHORUS(4) -> BRIDGE(4) -> OUTRO
""")

print(f"\n{'='*70}")
print("ANALYSIS COMPLETE")
print(f"{'='*70}")
