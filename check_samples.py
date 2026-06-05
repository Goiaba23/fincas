import numpy as np, soundfile as sf, os, glob

base = r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2"

# Find actual folder names
for root, dirs, files in os.walk(base):
    for d in dirs:
        pass  # just to populate

# List pontinho directory
pontinho_dir = None
for root, dirs, files in os.walk(base):
    if root.endswith('Pontinho'):
        pontinho_dir = root
        break

if pontinho_dir:
    print("=== PONTINHO SAMPLES ===")
    for f in sorted(os.listdir(pontinho_dir)):
        fpath = os.path.join(pontinho_dir, f)
        if os.path.isfile(fpath) and f.endswith('.wav'):
            y, sr = sf.read(fpath)
            if y.ndim > 1: y = y.mean(axis=1)
            dur = len(y)/sr
            peak = np.max(np.abs(y))
            rms = np.sqrt(np.mean(y**2))
            print(f'  {f:40s}  dur={dur:.3f}s  peak={peak:.2f}  rms={rms:.4f}')
    
    # Check subdirs
    for root, dirs, files in os.walk(pontinho_dir):
        for d in dirs:
            sub = os.path.join(root, d)
            print(f"\n  --- Subdir: {d} ---")
            for f in sorted(os.listdir(sub)):
                fpath = os.path.join(sub, f)
                if f.endswith('.wav'):
                    y, sr = sf.read(fpath)
                    if y.ndim > 1: y = y.mean(axis=1)
                    dur = len(y)/sr
                    print(f'    {f:35s}  dur={dur:.3f}s  peak={np.max(np.abs(y)):.2f}')

# Also check loops from Brazilian Funk
loops_dir = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\Loops"
print("\n=== FIRST 10 LOOPS ===")
for i, f in enumerate(sorted(os.listdir(loops_dir))):
    if f.endswith('.wav'):
        y, sr = sf.read(os.path.join(loops_dir, f))
        if y.ndim > 1: y = y.mean(axis=1)
        dur = len(y)/sr
        print(f'  {f:40s}  dur={dur:.3f}s  peak={np.max(np.abs(y)):.2f}')
    if i >= 10: break

# Check FX
fx_dir = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\FX"
print("\n=== FX SAMPLES ===")
for f in sorted(os.listdir(fx_dir)):
    if f.endswith('.wav'):
        y, sr = sf.read(os.path.join(fx_dir, f))
        if y.ndim > 1: y = y.mean(axis=1)
        dur = len(y)/sr
        peak = np.max(np.abs(y))
        print(f'  {f:35s}  dur={dur:.3f}s  peak={peak:.2f}')

print("\nDone.")
