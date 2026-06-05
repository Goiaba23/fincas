"""Generate FLP v5 using root.insert() at correct position."""
import pyflp
import os
import struct
from pyflp._events import UnicodeEvent, U8Event, U16Event, U32Event, I8Event, BoolEvent
from pyflp.channel import ChannelID
from pyflp.plugin import PluginID

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"
OUTPUT = r"C:\Users\alerrandro\Music\Nova pasta (2)\mundo_louco_v5.flp"

samples = {
    "Kick": r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\Kicks\[BRF2] Kick (1).wav",
    "Caixa": r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2\JF No Beat - Pack Relíquia Funk 2\Caixa\JF No Beat - RF2 - Caixa 4.wav",
    "Hi-Hat": r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\Hats\[BRF2] Hat (1).wav",
    "808 Bass": r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808\[BRF2] 808 (6).wav",
}

def make_channel_events(iid, name, sample_path):
    """Create standard sampler channel events."""
    evts = []
    evts.append(U16Event(ChannelID.New, struct.pack('<H', iid)))
    evts.append(U8Event(ChannelID.Type, b'\x00'))
    evts.append(BoolEvent(ChannelID.IsEnabled, b'\x01'))
    evts.append(I8Event(ChannelID.RoutedTo, struct.pack('<b', -1)))
    evts.append(U32Event(ChannelID.GroupNum, struct.pack('<I', 0)))
    evts.append(UnicodeEvent(PluginID.Name, (name + "\0").encode('utf-16-le')))
    if os.path.exists(sample_path):
        sp_data = (sample_path + "\0").encode('utf-16-le')
    else:
        sp_data = "\0".encode('utf-16-le')
    evts.append(UnicodeEvent(ChannelID.SamplePath, sp_data))
    evts.append(U16Event(ChannelID._VolWord, struct.pack('<H', 10000)))
    evts.append(U16Event(ChannelID._PanWord, struct.pack('<H', 6400)))
    evts.append(U16Event(ChannelID.Cutoff, struct.pack('<H', 1024)))
    evts.append(U16Event(ChannelID.StereoDelay, struct.pack('<H', 2048)))
    return evts

# Parse template
project = pyflp.parse(TEMPLATE)
root = project.events

# Rename existing sampler (IID=0) -> Kick
for ch in project.channels:
    if isinstance(ch, pyflp.channel.Sampler):
        ch.name = "Kick"
        if os.path.exists(samples["Kick"]):
            sp = UnicodeEvent(ChannelID.SamplePath, (samples["Kick"] + "\0").encode('utf-16-le'))
            ch.events.append(sp)
            print(f"Set Kick sample, channel has {len(ch.events)} events")
        break

# Insert 3 new channels at position 75 (after existing channel events)
insert_pos = 75
for i, (name, spath) in enumerate(samples.items()):
    if name == "Kick":
        continue
    iid = i  # Caixa=1, Hi-Hat=2, 808 Bass=3
    evts = make_channel_events(iid, name, spath)
    for ev in evts:
        try:
            root.insert(insert_pos, ev)
            insert_pos += 1
        except Exception as ex:
            print(f"ERROR inserting {name} event {ev.id}: {ex}")
            raise
    print(f"Inserted: {name} (IID={iid}) at pos {insert_pos-len(evts)}")

project.tempo = 164
project.title = "Mundo Louco - MC Kelvinho"

pyflp.save(project, OUTPUT)
print(f"\nSaved: {OUTPUT} ({os.path.getsize(OUTPUT)} bytes)")

# Verify
p2 = pyflp.parse(OUTPUT)
print(f"BPM: {p2.tempo}")
print(f"Title: {p2.title}")
print(f"Channels: {len(list(p2.channels))}")
for ch in p2.channels:
    sp = os.path.basename(str(ch.sample_path)) if isinstance(ch, pyflp.channel.Sampler) and ch.sample_path else ""
    print(f"  {ch.name} (IID={ch.iid}) sample={sp}")
