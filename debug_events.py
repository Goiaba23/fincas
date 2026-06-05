"""Debug PyFLP event tree structure."""
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
    print(f"Sampler events tree:")
    print(f"  len(events): {len(sampler.events)}")
    print(f"  events.ids: {sampler.events.ids}")
    print(f"  events.indexes: {sampler.events.indexes}")
    print(f"  sorted indexes: {sorted(sampler.events.indexes)}")
    
    # Print all events
    for i, ev in enumerate(sampler.events):
        print(f"  [{i}] {ev.id}: {ev.value!r}")
    
    # Try inserting directly into the root
    print(f"\nRoot events tree:")
    root = sampler.events.root
    print(f"  len: {len(root)}")
    print(f"  children: {len(root.children)}")
    
    # Method: add event to root at position after last channel event
    test_path = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\[BRF2] 808 (6).wav"
    path_bytes = test_path.encode('utf-16-le')
    event = UnicodeEvent(ChannelID.SamplePath, path_bytes)
    
    # Try adding to the root tree directly
    print(f"\nAdding SamplePath event to root...")
    root.append(event)
    print(f"  Root len now: {len(root)}")
    
    # Does the sampler see it now?
    print(f"  Sampler has SamplePath: {ChannelID.SamplePath in sampler.events.ids}")
    print(f"  Sampler sample_path: {sampler.sample_path}")
