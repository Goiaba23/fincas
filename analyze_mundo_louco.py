import numpy as np, soundfile as sf, os, json
from scipy import signal as sig

f = os.path.expandvars(r'%TEMP%\opencode\mundo_louco.wav')
y, sr = sf.read(f)
if y.ndim > 1: y = y.mean(axis=1)
print(f'Sample rate: {sr}, Duration: {len(y)/sr:.1f}s, Max: {np.max(np.abs(y)):.3f}')

beat_s = 60.0/179.0
print(f'Beat duration: {beat_s:.3f}s, Bar: {beat_s*4:.3f}s')

# STFT analysis
freqs, times, Zxx = sig.stft(y[:int(32*beat_s*4*sr)], fs=sr, nperseg=4096, noverlap=2048)
Zxx_mag = np.abs(Zxx)

# Dominant low frequency
low_mask = freqs < 200
low_energy = np.mean(Zxx_mag[low_mask], axis=1)
dominant_low_freq = freqs[low_mask][np.argmax(low_energy)]
print(f'Dominant low freq: {dominant_low_freq:.1f} Hz')

# Spectral centroid
magnitudes = Zxx_mag
total_mag = np.sum(magnitudes, axis=0)
centroid = np.sum(freqs[:, None] * magnitudes, axis=0) / (np.sum(magnitudes, axis=0) + 1e-10)
print(f'Avg spectral centroid: {np.mean(centroid):.0f} Hz')

# Low freq envelope for 808 detection
b, a = sig.butter(4, 150/(sr/2), btype='low')
y_low = sig.filtfilt(b, a, y)
y_env = np.abs(sig.hilbert(y_low))
envelope_resampled = sig.resample(y_env, int(len(y_env) / sr * 179 / 4))

from scipy.signal import find_peaks
peaks, props = find_peaks(envelope_resampled, height=np.mean(envelope_resampled)*1.8, distance=2)
print(f'808 hits detected: {len(peaks)}')
print(f'First 30 hit positions (quarter-beats): {peaks[:30].tolist()}')

# Analyze 808 pitch - get pitch of first few hits
for pi in range(min(5, len(peaks))):
    p = peaks[pi]
    if p > 0 and p < len(envelope_resampled) - 1:
        hit_time = p * 4 / 179  # convert quarter-beats to seconds
        hit_center = int(hit_time * sr)
        hit_window = slice(max(0, hit_center), min(len(y), hit_center + int(0.3 * sr)))
        hit_data = y_low[hit_window] * np.hanning(min(len(y), hit_center + int(0.3 * sr)) - max(0, hit_center))
        if len(hit_data) > 100:
            hit_fft = np.abs(np.fft.rfft(hit_data * np.hanning(len(hit_data))))
            hit_freqs = np.fft.rfftfreq(len(hit_data), 1/sr)
            low_idx = np.where((hit_freqs > 20) & (hit_freqs < 200))[0]
            if len(low_idx) > 0:
                peak_idx = low_idx[np.argmax(hit_fft[low_idx])]
                print(f'  808 hit {pi} at {hit_time:.2f}s: ~{hit_freqs[peak_idx]:.1f}Hz')

# Mid-band for caixa (150-400Hz)
b_mid, a_mid = sig.butter(4, [150/(sr/2), 400/(sr/2)], btype='band')
y_mid = sig.filtfilt(b_mid, a_mid, y)
y_mid_env = np.abs(y_mid)
y_mid_smooth = np.convolve(y_mid_env, np.ones(int(sr*0.05))/int(sr*0.05), mode='same')
peaks_mid, _ = find_peaks(y_mid_smooth, height=np.mean(y_mid_smooth)*3, distance=int(sr*0.15))
peak_beats = peaks_mid / sr * 179
print(f'\nCaixa hits detected: {len(peaks_mid)}')
print(f'First 20 caixa beat positions: {[round(b,1) for b in peak_beats[:20]]}')

# High band for hats (4kHz+)
b_h, a_h = sig.butter(4, 4000/(sr/2), btype='high')
y_hats = sig.filtfilt(b_h, a_h, y)
y_hats_env = np.abs(y_hats)
y_hats_smooth = np.convolve(y_hats_env, np.ones(int(sr*0.02))/int(sr*0.02), mode='same')
peaks_h, _ = find_peaks(y_hats_smooth, height=np.mean(y_hats_smooth)*4, distance=int(sr*0.03))
peak_hat_beats = peaks_h / sr * 179
print(f'\nHi-hat hits detected: {len(peaks_h)}')
print(f'First 30 hi-hat positions (beats): {[round(b,2) for b in peak_hat_beats[:30]]}')

print('\nAnalysis complete.')
