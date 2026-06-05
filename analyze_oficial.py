import numpy as np, soundfile as sf, os, json
from scipy import signal as sig
from scipy.signal import find_peaks

f = os.path.expandvars(r'%TEMP%\opencode\mundo_louco_oficial.wav')
y, sr = sf.read(f)
if y.ndim > 1: y = y.mean(axis=1)
print(f'Duration: {len(y)/sr:.1f}s, SR: {sr}')

# Analyze first 60 seconds for BPM and key
y_seg = y[:int(60*sr)]

# BPM via low frequency envelope autocorrelation
b_low, a_low = sig.butter(4, 120/(sr/2), btype='low')
y_low = sig.filtfilt(b_low, a_low, y_seg)
y_env = np.abs(sig.hilbert(y_low))
y_env_smooth = np.convolve(y_env, np.ones(int(sr*0.05))/int(sr*0.05), mode='same')

# Autocorrelation
ac = np.correlate(y_env_smooth - np.mean(y_env_smooth), y_env_smooth - np.mean(y_env_smooth), mode='full')
ac = ac[len(ac)//2:]
min_lag = int(sr * 60 / 200)
max_lag = int(sr * 60 / 60)
search_ac = ac[min_lag:max_lag]
peaks, props = find_peaks(search_ac, height=np.mean(search_ac)*1.5)

if len(peaks) > 0:
    best = peaks[np.argmax(props['peak_heights'])]
    bpm = 60.0 / ((min_lag + best) / sr)
    print(f'BPM: {bpm:.1f}')

# Chroma key detection (simplified)
n_fft = 2048
S = np.abs(sig.stft(y_seg, fs=sr, nperseg=n_fft, noverlap=1024, boundary=None)[2])
freqs_stft = np.fft.rfftfreq(n_fft, 1/sr)
notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

chroma = np.zeros((12, S.shape[1]))
for i in range(12):
    for octave in range(2, 6):
        cf = 440 * (2 ** ((i + 12*octave - 69) / 12))
        if cf < freqs_stft[0]: continue
        if cf > freqs_stft[-1]: continue
        idx = np.argmin(np.abs(freqs_stft - cf))
        width = max(1, int(cf * 0.08 / (freqs_stft[1]-freqs_stft[0])))
        lo = max(0, idx-width)
        hi = min(len(freqs_stft), idx+width+1)
        w = np.exp(-0.5 * ((freqs_stft[lo:hi] - cf) / (cf*0.08))**2)
        chroma[i] += w @ S[lo:hi]

chroma_mean = np.mean(chroma, axis=1)
chroma_norm = chroma_mean / np.max(chroma_mean)

print('\nChroma profile:')
for i in np.argsort(chroma_norm)[-6:][::-1]:
    print(f'  {notes[i]:3s}: {chroma_norm[i]:.3f}')

# Key detection with Krumhansl-Schmuckler
major_template = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
minor_template = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
mt = major_template / np.sum(major_template)
mnt = minor_template / np.sum(minor_template)
cn = chroma_mean / np.sum(chroma_mean)

best_key = ''
best_corr = -1
for i in range(12):
    cmaj = np.correlate(cn, np.roll(mt, i))[0]
    cmin = np.correlate(cn, np.roll(mnt, i))[0]
    if cmaj > best_corr:
        best_corr = cmaj; best_key = f'{notes[i]} major'
    if cmin > best_corr:
        best_corr = cmin; best_key = f'{notes[i]} minor'
print(f'\nDetected key: {best_key} (corr={best_corr:.3f})')

# 808 analysis
b_low2, a_low2 = sig.butter(4, 150/(sr/2), btype='low')
y_808 = sig.filtfilt(b_low2, a_low2, y_seg)
freqs_808, times_808, Z_808 = sig.stft(y_808, fs=sr, nperseg=4096, noverlap=2048)
Z_808_mag = np.abs(Z_808)

# Find dominant 808 frequency
low_band = freqs_808 < 200
mean_spec = np.mean(Z_808_mag[low_band], axis=1)
if len(mean_spec) > 0:
    dom_idx = np.argmax(mean_spec)
    dom_freq = freqs_808[low_band][dom_idx]
    print(f'\n808 dominant frequency: {dom_freq:.1f} Hz')
    # Note name
    note_num = 12 * np.log2(dom_freq/440) + 69
    note_idx = int(round(note_num)) % 12
    octave = int(round(note_num)) // 12 - 1
    print(f'  Closest note: {notes[note_idx]}{octave} ({dom_freq:.1f}Hz)')

# Find 808 pattern by detecting onsets in low frequency
y_env_low = np.abs(sig.hilbert(y_808))
y_env_low_smooth = np.convolve(y_env_low, np.ones(int(sr*0.05))/int(sr*0.05), mode='same')
peaks_808, props_808 = find_peaks(y_env_low_smooth, height=np.mean(y_env_low_smooth)*2, distance=int(sr*0.15))
peak_times = peaks_808 / sr
if len(peak_times) > 0:
    print(f'\nFirst 20 808 hits (seconds):')
    for pt in peak_times[:20]:
        beat_pos = pt * 179 / 60
        print(f'  {pt:.2f}s (beat {beat_pos:.1f})')

# Spectral centroid (quick)
centroid = np.sum(freqs_stft[:, None] * S, axis=0) / (np.sum(S, axis=0) + 1e-10)
print(f'\nSpectral centroid: {np.mean(centroid):.0f} Hz')
print(f'RMS: {20*np.log10(np.sqrt(np.mean(y**2))):.1f} dBFS')
print(f'Peak: {np.max(np.abs(y)):.3f}')
