import numpy as np, soundfile as sf, os, json

def analyze_pitch(wav_path):
    """Find fundamental frequency of a sample"""
    try:
        y, sr = sf.read(wav_path)
        if y.ndim > 1: y = y.mean(axis=1)
        y = y / (np.max(np.abs(y)) + 1e-10)
        
        # Use first 0.5s for analysis
        y_seg = y[:int(min(0.5*sr, len(y)))]
        
        # Autocorrelation pitch detection
        n = len(y_seg)
        if n < 100: return None, None
        
        # Hann window
        window = np.hanning(n)
        y_w = y_seg * window
        
        # FFT
        fft = np.abs(np.fft.rfft(y_w))
        freqs = np.fft.rfftfreq(n, 1/sr)
        
        # Find peak between 20-200Hz
        low_idx = np.where((freqs > 20) & (freqs < 200))[0]
        if len(low_idx) == 0: return None, None
        
        peak_idx = low_idx[np.argmax(fft[low_idx])]
        pitch = freqs[peak_idx]
        
        # Spectral centroid
        centroid = np.sum(freqs * fft) / (np.sum(fft) + 1e-10)
        
        # Duration
        env = np.abs(y)
        env_smooth = np.convolve(env, np.ones(int(sr*0.01))/int(sr*0.01), mode='same')
        threshold = np.max(env_smooth) * 0.1
        above = np.where(env_smooth > threshold)[0]
        duration_s = (above[-1] - above[0]) / sr if len(above) > 1 else len(y)/sr
        
        return float(pitch), {
            'duration_s': float(duration_s),
            'centroid_hz': float(centroid),
            'rms': float(np.sqrt(np.mean(y**2))),
            'peak': float(np.max(np.abs(y)))
        }
    except Exception as e:
        return None, None

# Analyze 808s from Brazilian Funk Vol 2
print("=== ANALYZING 808 SAMPLES ===")
results = []
directory = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808"
for fname in sorted(os.listdir(directory)):
    if fname.endswith('.wav'):
        fpath = os.path.join(directory, fname)
        pitch, meta = analyze_pitch(fpath)
        if pitch:
            note_name = ''
            notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
            note_idx = int(round(12 * np.log2(pitch/440) + 69)) % 12
            octave = int(round(12 * np.log2(pitch/440) + 69)) // 12 - 1
            note_name = f'{notes[note_idx]}{octave} ({pitch:.1f}Hz)'
            results.append({'file': fname, 'pitch_hz': pitch, 'note': note_name, 'dur_s': meta['duration_s'], 'rms': meta['rms']})
            print(f"  {fname:25s} >> {note_name:15s}  dur={meta['duration_s']:.2f}s  rms={meta['rms']:.4f}")

print(f"\n=== TOP 808 CLOSE TO 46Hz (F#) ===")
results.sort(key=lambda x: abs(x['pitch_hz'] - 46.2))
for r in results[:5]:
            print(f"  {r['file']:25s} >> {r['note']:15s}  diff={abs(r['pitch_hz']-46.2):.1f}Hz")

# Also analyze caixa from Reliquia
print("\n=== ANALYZING CAIXA SAMPLES ===")
caixa_results = []
caixa_dir = r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2\JF No Beat - Pack Relíquia Funk 2\Caixa"
for fname in sorted(os.listdir(caixa_dir)):
    if fname.endswith('.wav'):
        fpath = os.path.join(caixa_dir, fname)
        pitch, meta = analyze_pitch(fpath)
        if pitch:
            caixa_results.append({'file': fname, 'pitch_hz': pitch, 'dur_s': meta['duration_s'], 'centroid': meta['centroid_hz'], 'rms': meta['rms']})
            print(f"  {fname:35s} >> pitch={pitch:.0f}Hz  centroid={meta['centroid_hz']:.0f}Hz  dur={meta['duration_s']:.2f}s")

print("\nDone.")
