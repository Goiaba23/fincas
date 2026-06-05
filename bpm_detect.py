import numpy as np, soundfile as sf, os
from scipy import signal as sig
from scipy.signal import find_peaks

f = os.path.expandvars(r'%TEMP%\opencode\mundo_louco_oficial.wav')
y, sr = sf.read(f)
if y.ndim > 1: y = y.mean(axis=1)

b, a = sig.butter(4, [100/(sr/2), 200/(sr/2)], btype='band')
y_bp = sig.filtfilt(b, a, y[:int(15*sr)])
env = np.abs(y_bp)
env_smooth = np.convolve(env, np.ones(int(sr*0.03))/int(sr*0.03), mode='same')

peaks, props = find_peaks(env_smooth, height=np.mean(env_smooth)*2.5, distance=int(sr*0.1))
intervals = np.diff(peaks) / sr * 60
intervals = intervals[(intervals > 60) & (intervals < 200)]

bins = np.arange(60, 201, 1)
if len(intervals) > 5:
    h, _ = np.histogram(intervals, bins)
    bpm_vals = bins[:-1]
    top = bpm_vals[np.argsort(h)[-5:][::-1]]
    print('Top BPM (from onset intervals):')
    for b in top:
        print(f'  {b} BPM ({h[b-60]} hits)')

# Half-time
for factor, name in [(0.5, 'half'), (2, 'double')]:
    iv = intervals * factor
    iv = iv[(iv > 60) & (iv < 200)]
    if len(iv) > 5:
        h, _ = np.histogram(iv, bins)
        top = bpm_vals[np.argsort(h)[-3:][::-1]]
        print(f'Top BPM ({name}):')
        for b in top:
            print(f'  {b} BPM ({h[b-60]} hits)')

# Print first 50 peak intervals
print('\nFirst 50 intervals (BPM):')
for i, iv in enumerate(intervals[:50]):
    print(f'  {iv:.0f}', end='')
    if (i+1) % 10 == 0: print()
print()
