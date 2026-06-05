import numpy as np, soundfile as sf, os, json
from scipy import signal as sig
from scipy.signal import find_peaks
import warnings; warnings.filterwarnings('ignore')

f = os.path.expandvars(r'%TEMP%\opencode\mundo_louco_oficial.wav')
y, sr = sf.read(f)
if y.ndim > 1: y = y.mean(axis=1)
print(f'Duration: {len(y)/sr:.1f}s, SR: {sr}')

# ================================================
# BPM DETECTION - use multiple methods
# ================================================
print('\n=== BPM DETECTION ===')

# Method 1: Onset detection curve autocorrelation
# Use high-frequency content for onset detection
b_onset, a_onset = sig.butter(4, 2000/(sr/2), btype='high')
y_h = sig.filtfilt(b_onset, a_onset, y)
onset_env = np.abs(sig.hilbert(y_h))
onset_env = np.convolve(onset_env, np.ones(int(sr*0.02))/int(sr*0.02), mode='same')

# Downsample for faster computation
ds_factor = 100
onset_ds = onset_env[::ds_factor]
onset_ac = np.correlate(onset_ds-np.mean(onset_ds), onset_ds-np.mean(onset_ds), mode='full')
onset_ac = onset_ac[len(onset_ac)//2:]

# Search for BPM between 60-200
for bpm_test in range(60, 201):
    lag = int((60.0/bpm_test) * sr / ds_factor)
    if lag < len(onset_ac):
        onset_ac[lag]  # touch to compute

# Find peaks in autocorrelation
peaks_ac, props_ac = find_peaks(onset_ac, height=np.mean(onset_ac)*2, distance=5)
bpm_candidates = []
for p in peaks_ac:
    lag_s = p * ds_factor / sr
    bpm = 60.0 / lag_s
    if 60 <= bpm <= 200:
        bpm_candidates.append((bpm, onset_ac[p]))

print('Top BPM candidates (onset autocorrelation):')
for bpm, val in sorted(bpm_candidates, key=lambda x: -x[1])[:5]:
    print(f'  {bpm:.1f} BPM (corr={val:.2f})')

# Method 2: Manual beat tapping from kick drum energy
b_kick, a_kick = sig.butter(4, [80/(sr/2), 120/(sr/2)], btype='band')
y_kick = sig.filtfilt(b_kick, a_kick, y[:int(30*sr)])
y_kick_env = np.abs(y_kick)
y_kick_env = np.convolve(y_kick_env, np.ones(int(sr*0.03))/int(sr*0.03), mode='same')

kick_peaks, _ = find_peaks(y_kick_env, height=np.mean(y_kick_env)*3, distance=int(sr*0.15))
if len(kick_peaks) > 5:
    intervals = np.diff(kick_peaks) / sr
    mean_interval = np.median(intervals)
    bpm_kick = 60.0 / mean_interval
    print(f'\nKick BPM: {bpm_kick:.1f} (median of {len(kick_peaks)} kicks)')
    print(f'  Half: {bpm_kick/2:.1f}, Double: {bpm_kick*2:.1f}')
    
    # Show the last few intervals to see if it's consistent
    print(f'  Last 10 intervals (BPM): {[f"{60.0/i:.0f}" for i in intervals[-10:]]}')

# Method 3: Snare on 2&4 detection (150-300Hz)
b_snare, a_snare = sig.butter(4, [150/(sr/2), 400/(sr/2)], btype='band')
y_snare = sig.filtfilt(b_snare, a_snare, y[:int(30*sr)])
y_snare_env = np.abs(y_snare)
y_snare_env = np.convolve(y_snare_env, np.ones(int(sr*0.03))/int(sr*0.03), mode='same')

snare_peaks, _ = find_peaks(y_snare_env, height=np.mean(y_snare_env)*3, distance=int(sr*0.15))
if len(snare_peaks) > 3:
    snare_intervals = np.diff(snare_peaks) / sr
    print(f'\nSnare peaks: {len(snare_peaks)} detected')
    print(f'  First 10 peak times: {[f"{p/sr:.2f}" for p in snare_peaks[:10]]}')
    # Snare should be on 2 and 4 - check the pattern
    beat_times_s = snare_peaks / sr
    print(f'  Times to nearest beat (assuming BPM=X):')

# ================================================
# KEY DETECTION via chroma
# ================================================
print('\n=== KEY DETECTION ===')
seg = y[:int(30*sr)]
S = np.abs(sig.stft(seg, fs=sr, nperseg=2048, noverlap=1024, boundary=None)[2])
fr = np.fft.rfftfreq(2048, 1/sr)
notes_c = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

chroma = np.zeros(12)
for i in range(12):
    for oc in range(2, 6):
        cf = 440 * (2**((i + 12*oc - 69)/12))
        if cf < fr[0] or cf > fr[-1]: continue
        idx = np.argmin(np.abs(fr - cf))
        w = max(1, int(cf*0.06/(fr[1]-fr[0])))
        lo = max(0, idx-w); hi = min(len(fr), idx+w+1)
        weights = np.exp(-0.5*((fr[lo:hi]-cf)/(cf*0.06))**2)
        chroma[i] += np.sum(weights[:, None] * S[lo:hi], axis=0).mean()

cn = chroma / np.max(chroma)
print('Chroma (relative):')
for i in np.argsort(cn)[-8:][::-1]:
    print(f'  {notes_c[i]}: {cn[i]:.3f}')

# Key correlation
mt = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
mnt = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
mt = mt/np.sum(mt); mnt=mnt/np.sum(mnt)
cc = chroma/np.sum(chroma)

print('\nKey candidates:')
keys = []
for i in range(12):
    cv_maj = np.corrcoef(cc, np.roll(mt, i))[0,1]
    cv_min = np.corrcoef(cc, np.roll(mnt, i))[0,1]
    if cv_maj > 0.3: keys.append((f'{notes_c[i]} major', cv_maj))
    if cv_min > 0.3: keys.append((f'{notes_c[i]} minor', cv_min))
for k, v in sorted(keys, key=lambda x: -x[1])[:5]:
    print(f'  {k}: corr={v:.3f}')

# ================================================
# 808 ANALYSIS - exact root and pattern
# ================================================
print('\n=== 808 ANALYSIS ===')

# Low pass filter to isolate 808
b_808, a_808 = sig.butter(4, 120/(sr/2), btype='low')
y_low = sig.filtfilt(b_808, a_808, y)

# STFT of low frequencies
f_low, t_low, Z_low = sig.stft(y_low[:int(60*sr)], fs=sr, nperseg=4096, noverlap=3072)
Z_low_mag = abs(Z_low)

# Find fundamental frequency
# Average spectrum over time
avg_spec = np.mean(Z_low_mag, axis=1)
low_band = f_low < 150
if np.any(low_band):
    fund_idx = np.argmax(avg_spec[low_band])
    fund_freq = f_low[low_band][fund_idx]
    print(f'808 fundamental: {fund_freq:.1f} Hz')
    nn = 12*np.log2(fund_freq/440)+69
    ni = int(round(nn))%12
    oc = int(round(nn))//12-1
    print(f'  Note: {notes_c[ni]}{oc}')

# 808 onset detection from low frequency envelope
env_808 = np.abs(sig.hilbert(y_low))
env_808_smooth = np.convolve(env_808, np.ones(int(sr*0.04))/int(sr*0.04), mode='same')
peaks_808, props_808 = find_peaks(env_808_smooth[:int(30*sr)], 
                                   height=np.mean(env_808_smooth)*2.5, 
                                   distance=int(sr*0.15))

print(f'\n808 hits in first 30s: {len(peaks_808)}')
if len(peaks_808) > 0:
    peak_times = peaks_808 / sr
    print('First 30 808 hit times (seconds):')
    for pt in peak_times[:30]:
        print(f'  {pt:.3f}s')
    
    # Find the time intervals between hits
    intervals_808 = np.diff(peak_times)
    print(f'\nIntervals: min={np.min(intervals_808):.3f}s, max={np.max(intervals_808):.3f}s, med={np.median(intervals_808):.3f}s')
    
    # Map hits to a bar grid
    # If BPM is X, one beat = 60/X seconds
    # Let's try different BPMs and see which gives the cleanest grid
    for try_bpm in [82, 130, 150, 164, 170, 175]:
        beat_s = 60.0 / try_bpm
        grid_positions = peak_times / beat_s
        grid_errors = [abs(g - round(g)) for g in grid_positions]
        mean_err = np.mean(grid_errors)
        print(f'  BPM {try_bpm}: mean grid error={mean_err:.3f} beats')

# ================================================
# DRUM PATTERN ANALYSIS
# ================================================
print('\n=== DRUM PATTERN ===')

# Bandpass for caixa (snare range 150-400Hz)
b_cx, a_cx = sig.butter(4, [150/(sr/2), 400/(sr/2)], btype='band')
y_cx = sig.filtfilt(b_cx, a_cx, y[:int(30*sr)])
env_cx = np.abs(y_cx)
env_cx = np.convolve(env_cx, np.ones(int(sr*0.03))/int(sr*0.03), mode='same')

# Hi-hats (5kHz+)
b_hh, a_hh = sig.butter(4, 5000/(sr/2), btype='high')
y_hh = sig.filtfilt(b_hh, a_hh, y[:int(10*sr)])
env_hh = np.abs(y_hh)
env_hh = np.convolve(env_hh, np.ones(int(sr*0.01))/int(sr*0.01), mode='same')

print(f'Caixa hit positions (first 20):')
peaks_cx, _ = find_peaks(env_cx, height=np.mean(env_cx)*3, distance=int(sr*0.15))
for p in peaks_cx[:20]:
    print(f'  {p/sr:.3f}s')

print(f'\nHi-hat hit positions (first 20):')
peaks_hh, _ = find_peaks(env_hh, height=np.mean(env_hh)*4, distance=int(sr*0.02))
for p in peaks_hh[:20]:
    print(f'  {p/sr:.4f}s')

print('\n=== ANALYSIS COMPLETE ===')
