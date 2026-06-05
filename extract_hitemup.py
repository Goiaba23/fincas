"""Extract Hit 'Em Up MIDI patterns and generate mashup notes for FL Studio"""
import sys, json
sys.path.insert(0, r'C:\Users\alerrandro\Music\Nova pasta (2)\fl-studio-mcp')

import mido

mid_path = r'C:\Users\alerrandro\AppData\Local\Temp\opencode\midi_files\2PAC_-_Hit_em_up.mid'
mid = mido.MidiFile(mid_path)
tpb = mid.ticks_per_beat

# Extract bass notes (Track 1)
bass_notes = []
tick_time = 0
for msg in mid.tracks[1]:
    tick_time += msg.time
    if msg.type == 'note_on' and msg.velocity > 0:
        beat = tick_time / tpb
        bass_notes.append({'midi': msg.note, 'time': beat})

# Get the pattern structure - first 4 bars (16 beats) as the loop
loop_start = 4.0
loop_end = 20.0

bass_loop = [n for n in bass_notes if loop_start <= n['time'] < loop_end]
min_time = bass_loop[0]['time'] if bass_loop else 0

# Normalize to start at beat 0 and create notes for 4 bars
hit_em_up_bass = []
for n in bass_loop:
    t = n['time'] - min_time
    hit_em_up_bass.append({'midi': n['midi'], 'time': round(t, 3)})

# Print the bass pattern
print("=== Hit 'Em Up Original Bassline (1 bar loop) ===")
for n in hit_em_up_bass:
    print(f"  Beat {n['time']:.2f}: MIDI {n['midi']} ({n['midi']-12}C)")

# Now create a transposed version in C minor
# Hit 'Em Up is in A minor: root = 33 (A1)
# We want C minor: root = 36 (C2)
# Transpose up 3 semitones: +3

def transpose_midi(note, semitones):
    return note + semitones

print("\n=== Transposed Bassline (A min to C min) ===")
c_min_bass = []
for n in hit_em_up_bass:
    new_note = transpose_midi(n['midi'], 3)  # A1=33 -> C2=36
    c_min_bass.append({'midi': new_note, 'time': n['time']})
    print(f"  Beat {n['time']:.2f}: MIDI {new_note} ({new_note-12}C)")

# Now create the Kanye Can't Tell Me Nothing chord progression in C minor
# Progression: Cm -> Eb -> Fm -> Eb -> Bb -> Cm (over 4 bars + 4 bars)
# For synth pad: play chord on each downbeat

print("\n=== Can't Tell Me Nothing - Chord Stabs (C minor) ===")

# C minor (Cm): C3+Eb3+G3 = 48+51+55
# Eb major (Eb): Eb3+G3+Bb3 = 51+55+58
# F minor (Fm): F3+Ab3+C4 = 53+56+60
# Bb major (Bb): Bb3+D4+F4 = 58+62+65

chords_cmin = {
    'Cm':  [48, 51, 55],
    'Eb':  [51, 55, 58],
    'Fm':  [53, 56, 60],
    'Bb':  [58, 62, 65],
}

progression_4bars = ['Cm', 'Eb', 'Fm', 'Fm', 'Eb', 'Bb', 'Cm', 'Cm']
kanye_chords = []

for i, chord in enumerate(progression_4bars):
    t = i * 2.0  # Each chord = 2 beats (half note)
    for note in chords_cmin[chord]:
        kanye_chords.append({'midi': note, 'time': t, 'duration': 1.8})
        print(f"  Beat {t:.1f}: {chord} - MIDI {note} ({note-12}C)")

# Output as JSON for the FL Studio MCP
print("\n=== Output ===")

# Create notes array for FL Studio bass (4 bar loop)
fl_bass_notes = []
for n in c_min_bass:
    fl_bass_notes.append({
        'midi': n['midi'],
        'time': n['time'],
        'duration': 0.25,
        'velocity': 0.85
    })

print("Bass notes (first 10):")
for n in fl_bass_notes[:10]:
    print(json.dumps(n))

print("\nChord notes (first 10):")
for n in kanye_chords[:10]:
    print(json.dumps(n))

# Write to JSON files for reference
with open(r'C:\Users\alerrandro\Music\Nova pasta (2)\bass_notes.json', 'w') as f:
    json.dump(fl_bass_notes, f, indent=2)

with open(r'C:\Users\alerrandro\Music\Nova pasta (2)\chord_notes.json', 'w') as f:
    json.dump(kanye_chords, f, indent=2)

print("\nSaved to bass_notes.json and chord_notes.json")
