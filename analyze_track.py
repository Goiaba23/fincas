import os, soundfile as sf, numpy as np
from scipy import signal

f = os.path.expandvars(r'%TEMP%\opencode\mundo_louco.wav')
data, sr = sf.read(f)
dur = len(data)/sr
mono = data.mean(axis=1)

# Simple BPM via onset strength
target_sr = 200
step = sr // target_sr
mono_lo = mono[:len(mono) - (len(mono) % step)].reshape(-1, step).mean(axis=1)
onset = np.abs(np.diff(mono_lo))**2
onset = np.concatenate([[0], onset])
if len(onset) > 7:
    onset = signal.savgol_filter(onset, 7, 2)

corr = np.correlate(onset - np.mean(onset), onset - np.mean(onset), mode='same')
mid = len(corr)//2
min_lag = int(target_sr * 60 / 180)
max_lag = int(target_sr * 60 / 80)
search = corr[mid+min_lag:mid+max_lag]
peaks = signal.find_peaks(search, height=np.std(search)*1.5)[0]
bpm = 60.0 / ((peaks[0]+min_lag) / target_sr) if len(peaks) > 0 else 0
print(f'BPM: {bpm:.1f}')
print(f'Dur: {dur:.0f}s | Peak: {np.max(np.abs(data)):.2f} | RMS: {20*np.log10(np.sqrt(np.mean(data**2))):.1f}dBFS')

# Key detection
spec = np.abs(np.fft.rfft(mono))
freqs = np.fft.rfftfreq(len(mono), 1/sr)
midi = 69 + 12 * np.log2(freqs / 440)
valid = (midi >= 24) & (midi <= 84)
chroma = np.zeros(12)
for m, s in zip(midi[valid], spec[valid]):
    chroma[int(round(m)) % 12] += s
keys = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
top3 = np.argsort(chroma)[-3:][::-1]
print(f'Key (chroma peak): {keys[np.argmax(chroma)]}')
print(f'Top 3: {[f"{keys[i]}={chroma[i]/np.sum(chroma)*100:.0f}%" for i in top3]}')

# Spectral analysis (average energy in bands)
spec_avg = np.mean(spec[freqs > 30])
sub = np.mean(spec[(freqs >= 30) & (freqs <= 100)])
low = np.mean(spec[(freqs > 100) & (freqs <= 500)])
mid = np.mean(spec[(freqs > 500) & (freqs <= 2000)])
high = np.mean(spec[(freqs > 2000) & (freqs <= 10000)])
print(f'Spectral: Sub={sub:.0f} | Low={low:.0f} | Mid={mid:.0f} | High={high:.0f}')
print(f'File: {os.path.getsize(f)/1024/1024:.1f}MB')
