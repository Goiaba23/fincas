"""Test modifying Empty template with PyFLP."""
import pyflp
import pathlib
from pyflp._events import UnicodeEvent, TEXT
from pyflp.channel import ChannelID

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"
OUTPUT = r"C:\Users\alerrandro\Music\Nova pasta (2)\modified.flp"

project = pyflp.parse(TEMPLATE)

# Change BPM to 164
print(f"Original tempo: {project.tempo}")
project.tempo = 164
print(f"New tempo: {project.tempo}")

# Find the sampler channel
sampler = None
for ch in project.channels:
    if isinstance(ch, pyflp.channel.Sampler):
        sampler = ch
        break

if sampler:
    print(f"\nSampler: {sampler}")
    print(f"  sample_path: {sampler.sample_path}")
    
    # Check if SamplePath event exists in the event tree
    has_sample_path = ChannelID.SamplePath in sampler.events.ids
    print(f"  has SamplePath event: {has_sample_path}")
    
    # Try adding a SamplePath event manually
    if not has_sample_path:
        print("  Adding SamplePath event...")
        test_path = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808\[BRF2] 808 (6).wav"
        path_bytes = test_path.encode('utf-16-le')
        from pyflp._events import UnicodeEvent, EventEnum
        
        # SamplePath is TEXT+4 = 196
        sample_path_id = EventEnum._missing_(196) or EventEnum(196)
        print(f"  SamplePath event id resolved: {sample_path_id}")
        
        # Create the event
        event = UnicodeEvent(sample_path_id, path_bytes)
        sampler.events.append(event)
        
        print(f"  SamplePath event added. Checking...")
        print(f"  sample_path now: {sampler.sample_path}")
    
    # Set name
    sampler.name = "808 Bass"
    print(f"  New name: {sampler.name}")

# Save
pyflp.save(project, OUTPUT)
print(f"\nSaved to: {OUTPUT}")
print(f"File size: {pathlib.Path(OUTPUT).stat().st_size} bytes")

# Verify
project2 = pyflp.parse(OUTPUT)
print(f"\nVerified: {project2}")
print(f"  Tempo: {project2.tempo}")
for ch in project2.channels:
    print(f"  {ch!r}")
    if isinstance(ch, pyflp.channel.Sampler) and ch.sample_path:
        print(f"    sample_path: {ch.sample_path}")
