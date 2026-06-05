"""Clean test: create new channel with sample path, verify at every step."""
import pyflp
import struct
from pyflp._events import UnicodeEvent, AsciiEvent, U8Event, U16Event, U32Event, I8Event, BoolEvent
from pyflp.channel import ChannelID
from pyflp.plugin import PluginID
from pyflp.project import ProjectID

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"
OUTPUT = r"C:\Users\alerrandro\Music\Nova pasta (2)\test3.flp"

project = pyflp.parse(TEMPLATE)
root = project.events
orig_count = len(root)
print(f"Root events before: {orig_count}")

# Create events for ONE new channel
iid = 7
ch_name = "808 Bass"
sample_path = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808\[BRF2] 808 (6).wav"

events_to_add = []
events_to_add.append(U16Event(ChannelID.New, struct.pack('<H', iid)))
events_to_add.append(U8Event(ChannelID.Type, b'\x00'))
events_to_add.append(BoolEvent(ChannelID.IsEnabled, b'\x01'))
events_to_add.append(I8Event(ChannelID.RoutedTo, struct.pack('<b', -1)))
events_to_add.append(U32Event(ChannelID.GroupNum, struct.pack('<i', 0)))
events_to_add.append(UnicodeEvent(PluginID.Name, (ch_name + "\0").encode('utf-16-le')))
# SamplePath - use UnicodeEvent
events_to_add.append(UnicodeEvent(ChannelID.SamplePath, (sample_path + "\0").encode('utf-16-le')))
events_to_add.append(U16Event(ChannelID._VolWord, struct.pack('<H', 10000)))
events_to_add.append(U16Event(ChannelID._PanWord, struct.pack('<H', 6400)))
events_to_add.append(U16Event(ChannelID.Cutoff, struct.pack('<H', 1024)))
events_to_add.append(U16Event(ChannelID.StereoDelay, struct.pack('<H', 2048)))

print(f"Created {len(events_to_add)} events for channel")

# Add each event to root
for ev in events_to_add:
    root.append(ev)

print(f"Root events after: {len(root)}")

# Verify the SamplePath is in root
sample_events = [e for e in root if e.id == ChannelID.SamplePath]
print(f"SamplePath events in root: {len(sample_events)}")

# Check if our event is at the end
last_events = list(root)[-15:]
print("\nLast events in root:")
for ev in last_events:
    print(f"  {ev.id}: {ev.value!r}")

# Save
project.channel_count = 2
pyflp.save(project, OUTPUT)
print(f"\nSaved to {OUTPUT}")

# Re-parse
project2 = pyflp.parse(OUTPUT)
print(f"\nRe-parsed root events: {len(project2.events)}")
sample_events2 = [e for e in project2.events if e.id == ChannelID.SamplePath]
print(f"SamplePath events in re-parsed: {len(sample_events2)}")
for ev in sample_events2:
    print(f"  {ev!r}")

print(f"\nChannels:")
for ch in project2.channels:
    print(f"  {ch!r}")
    if hasattr(ch, 'sample_path'):
        print(f"    sample_path: {ch.sample_path}")
