"""Create multiple sampler channels by duplicating existing channel events."""
import pyflp
import struct
from pyflp._events import (
    EventEnum, EventTree, IndexedEvent,
    UnicodeEvent, AsciiEvent, U8Event, U16Event, U32Event, I8Event, BoolEvent,
    StructEventBase
)
from pyflp.channel import ChannelID, Sampler
from pyflp.plugin import PluginID

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"
OUTPUT = r"C:\Users\alerrandro\Music\Nova pasta (2)\mundo_louco_project.flp"

project = pyflp.parse(TEMPLATE)
print(f"Project: {project}")
print(f"Initial channels: {project.channel_count}")

# Get the first (and only) sampler
sampler = None
for ch in project.channels:
    if isinstance(ch, Sampler):
        sampler = ch
        break

if not sampler:
    print("ERROR: No sampler found!")
    exit(1)

print(f"Sampler: {sampler}")
print(f"  events count: {len(sampler.events)}")

# Collect all events from the sampler (sorted by root index)
sampler_events = list(sampler.events)
print(f"  sampler events: {len(sampler_events)}")

# Serialize each event to bytes and back to understand what's needed
# Let's instead create new events for each channel from scratch
# using the existing events as templates

def duplicate_channel_events(source_events, new_iid, new_name, sample_path=None):
    """Duplicate channel events with a new IID and name."""
    new_events = []
    for event in source_events:
        eid = event.id
        
        if eid == ChannelID.New:
            # Create new IID event
            data = struct.pack('<H', new_iid)
            new_events.append(U16Event(ChannelID.New, data))
        elif eid == PluginID.Name:
            # Set new name
            name_bytes = new_name.encode('utf-16-le') + b'\0'
            new_events.append(UnicodeEvent(PluginID.Name, name_bytes))
        elif eid == ChannelID.SamplePath:
            if sample_path:
                path_bytes = sample_path.encode('utf-16-le') + b'\0'
                new_events.append(UnicodeEvent(ChannelID.SamplePath, path_bytes))
            # Skip if no sample path (don't add empty SamplePath)
        else:
            # Copy other events as-is (same struct data)
            event_data = bytes(event)[1:]  # skip ID byte (but variable length for text)
            # Actually bytes(event) gives full serialized: id + (varint_len + data for text, or raw data for small)
            raw = bytes(event)
            id_byte = raw[0]
            if eid < 64:  # 1-byte data
                new_events.append(type(event)(eid, raw[1:2]))
            elif eid < 128:  # 2-byte data
                new_events.append(type(event)(eid, raw[1:3]))
            elif eid < 192:  # 4-byte data
                new_events.append(type(event)(eid, raw[1:5]))
            elif eid < 208:  # TEXT event - skip varint
                # Parse varint length
                rest = raw[1:]
                # VarInt encoded length
                length = 0
                shift = 0
                pos = 0
                while pos < len(rest):
                    byte = rest[pos]
                    length |= (byte & 0x7F) << shift
                    shift += 7
                    pos += 1
                    if not (byte & 0x80):
                        break
                data = rest[pos:pos+length]
                new_events.append(type(event)(eid, data))
            else:  # DATA event - skip varint
                rest = raw[1:]
                length = 0
                shift = 0
                pos = 0
                while pos < len(rest):
                    byte = rest[pos]
                    length |= (byte & 0x7F) << shift
                    shift += 7
                    pos += 1
                    if not (byte & 0x80):
                        break
                data = rest[pos:pos+length]
                new_events.append(type(event)(eid, data))
    
    return new_events


# Define the 4 channels we need
channels_to_create = [
    {"name": "Kick", "iid": 1, "sample_path": r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808\[BRF2] 808 (6).wav"},
    {"name": "Caixa", "iid": 2, "sample_path": r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2\JF No Beat - Pack Relíquia Funk 2\Caixa\JF No Beat - RF2 - Caixa 4.wav"},
    {"name": "Hi-Hat", "iid": 3, "sample_path": None},
    {"name": "808 Bass", "iid": 4, "sample_path": r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808\[BRF2] 808 (6).wav"},
]

# Actually, let me take an even simpler approach.
# Instead of trying to reconstruct all events, let me:
# 1. Serialize the entire root EventTree to bytes
# 2. Find the first ChannelID.New in the bytes  
# 3. Copy ALL events from there to the end (the complete first channel)
# 4. Paste copies with modified IIDs
#
# Let me use the low-level approach of building events one by one.

print("\n=== Testing event creation ===")

# Test 1: Create a simple U16Event for ChannelID.New
test_new = U16Event(ChannelID.New, struct.pack('<H', 5))
print(f"New event: id={test_new.id}, value={test_new.value}")
raw = bytes(test_new)
print(f"  raw bytes: {raw.hex()}")

# Test 2: Create a PluginID.Name UnicodeEvent
test_name = UnicodeEvent(PluginID.Name, "Test Channel\0".encode('utf-16-le'))
print(f"Name event: id={test_name.id}, value={test_name.value!r}")
raw = bytes(test_name)
print(f"  raw bytes: {raw.hex()}")

# Test 3: Create ChannelID.Type
test_type = U8Event(ChannelID.Type, b'\x00')
print(f"Type event: id={test_type.id}, value={test_type.value}")

# Test 4: Create ChannelID.IsEnabled (BoolEvent)
test_enabled = BoolEvent(ChannelID.IsEnabled, b'\x01')
print(f"IsEnabled: id={test_enabled.id}, value={test_enabled.value}")

# Test 5: ChannelID.RoutedTo
test_routed = I8Event(ChannelID.RoutedTo, struct.pack('<b', -1))
print(f"RoutedTo: id={test_routed.id}, value={test_routed.value}")

# Test 6: SamplePath UnicodeEvent
test_path_text = r"C:\test\sample.wav"
test_path = UnicodeEvent(ChannelID.SamplePath, (test_path_text + "\0").encode('utf-16-le'))
print(f"SamplePath: id={test_path.id}, value={test_path.value!r}")

# Now let's try building a complete channel
print("\n=== Building new channel ===")

def build_minimal_channel_events(iid, name, sample_path=None):
    """Build minimal events needed for a Sampler channel."""
    events = []
    
    # 1. ChannelID.New (marks start of channel)
    events.append(U16Event(ChannelID.New, struct.pack('<H', iid)))
    
    # 2. ChannelID.Type
    events.append(U8Event(ChannelID.Type, b'\x00'))  # 0 = Sampler
    
    # 3. ChannelID.IsEnabled
    events.append(BoolEvent(ChannelID.IsEnabled, b'\x01'))
    
    # 4. ChannelID.RoutedTo  
    events.append(I8Event(ChannelID.RoutedTo, struct.pack('<b', -1)))
    
    # 5. ChannelID.GroupNum - needed by parser
    events.append(U32Event(ChannelID.GroupNum, struct.pack('<i', 0)))
    
    # 6. PluginID.Name
    events.append(UnicodeEvent(PluginID.Name, (name + "\0").encode('utf-16-le')))
    
    # 7. ChannelID.SamplePath (if provided)
    if sample_path:
        events.append(UnicodeEvent(ChannelID.SamplePath, (sample_path + "\0").encode('utf-16-le')))
    
    # 8. ChannelID._VolWord (WORD+8=72) - volume 10000
    events.append(U16Event(ChannelID._VolWord, struct.pack('<H', 10000)))
    
    # 9. ChannelID._PanWord (WORD+9=73) - pan center 6400
    events.append(U16Event(ChannelID._PanWord, struct.pack('<H', 6400)))
    
    # 10. ChannelID.Cutoff (WORD+7=71) - 1024
    events.append(U16Event(ChannelID.Cutoff, struct.pack('<H', 1024)))
    
    # 11. ChannelID.StereoDelay (WORD+21=85) - 2048
    events.append(U16Event(ChannelID.StereoDelay, struct.pack('<H', 2048)))
    
    return events

# Build one channel and try adding it
iid = 5
new_events = build_minimal_channel_events(iid, "Test 808")
print(f"Built {len(new_events)} events for channel {iid}")

# Add to root EventTree
root = project.events
print(f"Root events before: {len(root)}")

for ev in new_events:
    root.append(ev)

print(f"Root events after: {len(root)}")

# Update channel count
project.channel_count = len(list(project.channels)) + 1
print(f"Channel count: {project.channel_count}")

# Save
pyflp.save(project, OUTPUT)
print(f"\nSaved to: {OUTPUT}")

# Verify
try:
    project2 = pyflp.parse(OUTPUT)
    print(f"\nRe-parsed: {project2}")
    print(f"Channels count: {len(list(project2.channels))}")
    for ch in project2.channels:
        print(f"  {ch!r}")
        if isinstance(ch, Sampler):
            print(f"    sample_path: {ch.sample_path}")
except Exception as e:
    print(f"Parse error: {e}")
    import traceback
    traceback.print_exc()
