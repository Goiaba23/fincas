import sys
sys.path.insert(0, r'C:\Users\alerrandro\Music\Nova pasta (2)\fl-studio-mcp')

import mido

mid_path = r'C:\Users\alerrandro\AppData\Local\Temp\opencode\midi_files\2PAC_-_Hit_em_up.mid'
mid = mido.MidiFile(mid_path)

print("Ticks per beat:", mid.ticks_per_beat)
print("Tracks:", len(mid.tracks))

for i, track in enumerate(mid.tracks):
    name = track.name if track.name else "unnamed"
    print(f'\nTrack {i}: "{name}" ({len(track)} msgs)')
    
    notes_on = []
    tick_time = 0
    for msg in track:
        tick_time += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            beat = tick_time / mid.ticks_per_beat
            notes_on.append((beat, msg.note))
    
    if notes_on:
        notes = [n[1] for n in notes_on]
        print("  Note range:", min(notes), "-", max(notes))
        print("  Unique notes:", sorted(set(notes)))
        print("  Total note-on events:", len(notes_on))
        print("  First 30:", notes_on[:30])
    else:
        print("  No note_on events found")

print('\nDone')
