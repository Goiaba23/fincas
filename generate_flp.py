"""Generate the complete Mundo Louco FLP project."""
import pyflp
import struct
import os
from pyflp._events import UnicodeEvent, U8Event, U16Event, U32Event, I8Event, BoolEvent
from pyflp.channel import ChannelID
from pyflp.plugin import PluginID
from pyflp.project import ProjectID

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"
OUTPUT = r"C:\Users\alerrandro\Music\Nova pasta (2)\mundo_louco_v4.flp"

# Sample paths
KICK = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\Kicks\[BRF2] Kick (1).wav"
CAIXA = r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2\JF No Beat - Pack Relíquia Funk 2\Caixa\JF No Beat - RF2 - Caixa 4.wav"
HAT = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\Hats\[BRF2] Hat (1).wav"
SAMPLE_808 = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808\[BRF2] 808 (6).wav"

# BPM
BPM = 164

def build_minimal_channel_events(iid, name, sample_path=None, color=None):
    """Build minimal events needed for a Sampler channel."""
    events = []
    
    # 1. ChannelID.New (marks start of channel)
    events.append(U16Event(ChannelID.New, struct.pack('<H', iid)))
    
    # 2. ChannelID.Type (0 = Sampler)
    events.append(U8Event(ChannelID.Type, b'\x00'))
    
    # 3. ChannelID.IsEnabled
    events.append(BoolEvent(ChannelID.IsEnabled, b'\x01'))
    
    # 4. ChannelID.RoutedTo (-1 = current insert)
    events.append(I8Event(ChannelID.RoutedTo, struct.pack('<b', -1)))
    
    # 5. ChannelID.GroupNum (needed by parser)
    events.append(U32Event(ChannelID.GroupNum, struct.pack('<i', 0)))
    
    # 6. PluginID.Name
    events.append(UnicodeEvent(PluginID.Name, (name + "\0").encode('utf-16-le')))
    
    # 7. Sample path
    if sample_path and os.path.exists(sample_path):
        events.append(UnicodeEvent(ChannelID.SamplePath, (sample_path + "\0").encode('utf-16-le')))
    else:
        # Empty SamplePath for channels that don't need a sample loaded yet
        events.append(UnicodeEvent(ChannelID.SamplePath, "\0".encode('utf-16-le')))
    
    # 8. Volume (10000 = default)
    events.append(U16Event(ChannelID._VolWord, struct.pack('<H', 10000)))
    
    # 9. Pan (6400 = center)
    events.append(U16Event(ChannelID._PanWord, struct.pack('<H', 6400)))
    
    # 10. Cutoff (1024 = max)
    events.append(U16Event(ChannelID.Cutoff, struct.pack('<H', 1024)))
    
    # 11. StereoDelay (2048 = default)
    events.append(U16Event(ChannelID.StereoDelay, struct.pack('<H', 2048)))
    
    return events


def main():
    # Parse template
    project = pyflp.parse(TEMPLATE)
    root = project.events
    
    # Set BPM
    project.tempo = BPM
    project.title = "Mundo Louco - MC Kelvinho"
    
    # Modify the existing sampler (IID 0) to be the Kick
    for ch in project.channels:
        if isinstance(ch, pyflp.channel.Sampler) and hasattr(ch, 'sample_path'):
            ch.name = "Kick"
            # Add SamplePath event to existing channel's tree
            if os.path.exists(KICK):
                sp_event = UnicodeEvent(ChannelID.SamplePath, (KICK + "\0").encode('utf-16-le'))
                ch.events.append(sp_event)
                print(f"Set Kick sample path")
            break
    
    # Add new channels
    channels = [
        # (iid, name, sample_path)
        (1, "Caixa", CAIXA),
        (2, "Hi-Hat", HAT),
        (3, "808 Bass", SAMPLE_808),
    ]
    
    for iid, name, sample_path in channels:
        events = build_minimal_channel_events(iid, name, sample_path)
        for ev in events:
            root.append(ev)
        print(f"Added channel: {name} (IID={iid})")
    
    # Update channel count
    project.channel_count = 1 + len(channels)
    
    # Save
    pyflp.save(project, OUTPUT)
    
    flp_size = os.path.getsize(OUTPUT)
    print(f"\nSaved to: {OUTPUT}")
    print(f"Size: {flp_size:,} bytes")
    
    # Verify
    project2 = pyflp.parse(OUTPUT)
    print(f"\n=== Verification ===")
    print(f"BPM: {project2.tempo}")
    print(f"Title: {project2.title}")
    print(f"Channels: {len(list(project2.channels))}")
    
    for ch in project2.channels:
        sp = "(none)"
        if isinstance(ch, pyflp.channel.Sampler) and ch.sample_path:
            sp = os.path.basename(str(ch.sample_path))
        print(f"  {ch.name}: IID={ch.iid}, type={type(ch).__name__}, sample={sp}")
    
    print(f"\nDone! Open {OUTPUT} in FL Studio.")
    print("Samples are referenced by absolute path - they should load automatically.")
    print(f"\nNext: Use FL Studio MCP to:")
    print(f"  1. Set step sequencer patterns (drums)")
    print(f"  2. Program 808 bassline notes")
    print(f"  3. Arrange the song in the playlist")


if __name__ == "__main__":
    main()
