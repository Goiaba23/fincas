"""Test adding event directly to sampler's events subtree."""
import pyflp
from pyflp._events import UnicodeEvent
from pyflp.channel import ChannelID, Sampler

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"

project = pyflp.parse(TEMPLATE)

sampler = None
for ch in project.channels:
    if isinstance(ch, Sampler):
        sampler = ch
        break

if sampler:
    print(f"Sampler has SamplePath: {ChannelID.SamplePath in sampler.events.ids}")
    print(f"Sampler events len: {len(sampler.events)}")
    
    # Add SamplePath event directly to sampler's events
    test_path = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\[BRF2] 808 (6).wav"
    path_bytes = test_path.encode('utf-16-le')
    event = UnicodeEvent(ChannelID.SamplePath, path_bytes)
    
    sampler.events.append(event)
    
    print(f"After append:")
    print(f"  Sampler events len: {len(sampler.events)}")
    print(f"  Has SamplePath: {ChannelID.SamplePath in sampler.events.ids}")
    print(f"  sample_path: {sampler.sample_path}")
    
    # Save
    import pyflp
    pyflp.save(project, r"C:\Users\alerrandro\Music\Nova pasta (2)\test_save.flp")
    print(f"\nSaved successfully!")
    
    # Verify by re-parsing
    project2 = pyflp.parse(r"C:\Users\alerrandro\Music\Nova pasta (2)\test_save.flp")
    for ch in project2.channels:
        if isinstance(ch, Sampler):
            print(f"Re-parsed sampler sample_path: {ch.sample_path}")
