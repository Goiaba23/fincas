"""Test: generate minimal FLP with ONLY BPM change, no new channels."""
import pyflp
import os

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"
OUTPUT = r"C:\Users\alerrandro\Music\Nova pasta (2)\test_bpm_only.flp"

project = pyflp.parse(TEMPLATE)
project.tempo = 164
project.title = "Test BPM Only"

pyflp.save(project, OUTPUT)
print(f"Saved: {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)")
print(f"BPM: {project.tempo}")

# Verify
p2 = pyflp.parse(OUTPUT)
print(f"Re-parsed BPM: {p2.tempo}")
print(f"Channels: {len(list(p2.channels))}")
for ch in p2.channels:
    print(f"  {ch.name}")
