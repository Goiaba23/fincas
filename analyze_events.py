"""Try approach: build FLP from scratch by modifying in-memory data."""
import pyflp
import os

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"
OUTPUT = r"C:\Users\alerrandro\Music\Nova pasta (2)\mundo_louco_v5.flp"

KICK = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\Kicks\[BRF2] Kick (1).wav"
CAIXA = r"C:\Users\alerrandro\Music\Drum Kits\Pack Reliquia Funk 2\JF No Beat - Pack Relíquia Funk 2\Caixa\JF No Beat - RF2 - Caixa 4.wav"
HAT = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\Hats\[BRF2] Hat (1).wav"
SAMPLE_808 = r"C:\Users\alerrandro\Music\Drum Kits\Brazilian Funk Vol 2\Brazilian Funk Drum Kit Vol 2 @travabeats\808\[BRF2] 808 (6).wav"

# Parse template
project = pyflp.parse(TEMPLATE)
root = project.events

# Iterate and count
root_events = list(root)
print(f"Total root events: {len(root_events)}")

# Find where project events end (before first New) and where channels end (before mixer)
first_new = None
mixer_start = None
for i, ev in enumerate(root_events):
    if first_new is None and ev.id == pyflp.channel.ChannelID.New:
        first_new = i
    if first_new is not None and mixer_start is None:
        # Check if this is a non-channel event
        etype = type(ev.id)
        if 'Mixer' in etype.__name__ or 'Insert' in etype.__name__ or 'Slot' in etype.__name__:
            mixer_start = i
            break
            
print(f"Project events: 0 to {first_new - 1}")
print(f"Channel 0 events: {first_new} to {mixer_start - 1}")
print(f"Channel 0 has {mixer_start - first_new} events")

# Strategy: 
# 1. Remove all channel events (first_new to mixer_start-1)
# 2. Add 4 new channels (each with ~7-10 events)
# 3. Insert at position first_new

channel_events = root_events[first_new:mixer_start]
non_channel_events = root_events[mixer_start:]

print(f"\nChannel events count: {len(channel_events)}")
for i, ev in enumerate(channel_events[:5]):
    print(f"  {i}: {ev.id}")
print(f"  ... ({len(channel_events)-5} more)")

print(f"\nPost-channel events count: {len(non_channel_events)}")
for i, ev in enumerate(non_channel_events[:5]):
    print(f"  {i}: {ev.id}")
