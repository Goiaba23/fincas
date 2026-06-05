# Brazilian Funk Production Guide — FL Studio Technical Reference

> Synthesized from Produsso, Cantivy, Sample Focus, FL Studio Full, and industry sources.

---

## 1. BPM and Key Selection

### BPM by Subgenre

| Style | BPM Range | Typical BPM | Notes |
|---|---|---|---|
| Funk 150 BPM (Mandelão) | 140–160 | **150** | Batidão pesado, tamborzão. Bailes BH/SP |
| Baile Funk / Tamborzão | 120–150 | **130–132** | Classic Rio baile funk, syncopated kick |
| Funk Melody | 95–110 | **100–105** | MC Livinho style, sung melodies |
| Funk Consciente | 130–150 | **132–140** | Same beat, social lyrics |
| Brega Funk | 130–150 | **135** | Recife/PE influence |
| Trap Funk | 140–160 (felt in half-time) | **70–80 (half-time)** | 808-heavy, trap hi-hats |
| Brazilian Phonk | 130–150 | **140** | Merges funk + Memphis rap + lo-fi |

### Common Keys

| Scale | Typical Songs | Feel |
|---|---|---|
| **Am** (A minor) | MC Kevinho "Olha a Explosão" (~130 BPM) | Most common funk key |
| **Dm** (D minor) | MC Fioti "Bum Bum Tam Tam" (~128 BPM) | Dark, heavy |
| **Em** (E minor) | Common melody/key choice | Versatile |
| **C** (C major) | Less dark, more pop | Brighter |
| **G** (G major) | Melody-friendly | Open sound |

### FL Studio Setup

```
BPM: 150 (mandelão) or 130 (melody)
Time Signature: 4/4
Buffer Size: 512 samples
Mixer Tracks: Kick, Snare/Clap, Hi-Hat, Tamborzão, 808, Voz, Melody
```

---

## 2. Drum Programming

### Kick Pattern (Tamborzão Syncopation)

The defining element of funk is the **syncopated kick** (tamborzão rhythm).

**Basic pattern at 130–150 BPM (16th-note grid in Piano Roll):**
```
Beat:     1   .   .   .   2   .   .   .   3   .   .   .   4   .   .   .
Kick:     X   .   X   .   .   .   X   .   X   .   X   .   .   .   .   X
         [1]      [1e]           [2&]    [3]      [3e]           [4&]
```

**Classic "Tamborzão" pattern:**
- Beat 1: Kick
- Beat 1 (e): Kick (off-beat)
- Between 2-3: Accented kick
- Beat 3: Kick
- Beat 3 (e): Kick
- Beat 4 (&): Kick
- Vary and create syncopas to give the groove

**Programming approach:**
1. Set BPM to 132 (baile) or 150 (mandelão)
2. Kick on **1, 1e, 2&, 3, 3e, 4&** (as above)
3. Experiment: move hits a few ticks forward/backward for swing
4. **Velocity variation**: 80-100% on main beats, 50-70% on ghost notes

### Snare / Clap

| Element | Position | Sound Character |
|---|---|---|
| Clap | **Beats 2 and 4** | Dry, short snap |
| Snare | Layer with clap for body | Short reverb (~0.3s) |
| Rimshot | Optional accent | Occasional fill |

**Clap processing:**
- EQ: HPF ~200Hz, slight boost at 1-2kHz for snap
- Reverb: Short room, decay ~0.3s, mix 15-25%
- Compression: Fast attack (1-5ms), ratio 4:1, 2-4dB reduction

### Hi-Hat Patterns

**Standard (16th notes):**
```
Beat:     1   e   &   a   2   e   &   a   3   e   &   a   4   e   &   a
Hi-Hat:   X   X   X   X   X   X   X   X   X   X   X   X   X   X   X   X
```

**With swing/variation:**
- Closed hi-hat on every 16th note
- **Velocity variation**: 60-80% on ghost 16ths, 90-100% on downbeats
- Every 2nd or 4th bar: open hi-hat on the "a" of beat 4
- **Off-beat accents**: Accent the "e" and "a" of each beat
- **Panning**: Slight L/R variation per hit (±15%)

**Brazilian Phonk hi-hat variation:**
- Apply **bit-crushing** for lo-fi grit
- Add reverb to select hits
- Vary velocities for human feel (60-100%)
- Add tambourine or agogo bell hits with swing, pan for stereo depth

### Percussion (Optional Brazilian Elements)

| Element | Role |
|---|---|
| Tambourine | 8th or 16th notes, panned |
| Agogo bells | Accented hits, call-and-response |
| Sirene (siren sample) | Signature baile funk element |
| Handclap stack | Layer 2-3 claps for thickness |

### FL Studio Drum Workflow Tips

- Use **Channel Rack** + Step Sequencer for quick pattern building
- Route each drum to its own **Mixer Track** for individual processing
- For complex patterns, use **Piano Roll** (right-click pattern → Piano Roll)
- **Swing knob** on Step Sequencer: add 5-15% for groove
- Use **FPC** (Fruity Drum Pad) for finger-drumming patterns
- **Fruity Slicer** or **SliceX** to chop drum loops and rearrange

---

## 3. 808 Bass Programming

### Sound Design in FL Studio

**Using 3x Osc:**
```
Osc 1: Pure sine wave, octave C1-C2
Osc 2: Slight detune or sine, +12 cents (optional, use sparingly)
Osc 3: Off (or subtle sub-layer)
```

**Using FLEX:**
- Select 808 presets
- Manipulate ADSR for note length

### ADSR Envelope

| Parameter | Funk 150 (Mandelão) | Trap Funk | Funk Melody |
|---|---|---|---|
| Attack | 1-5ms (fast, punchy) | 5-10ms | 5-10ms |
| Decay | 50-100ms (short) | 200-400ms | 150-300ms |
| Sustain | Low | Medium | Medium |
| Release | 50-100ms (tight) | 200-500ms | 150-300ms |

### Distortion / Saturation

- **Fruity Fast Dist**: Light drive, mix 20-40%
- **Blood Overdrive**: Subtle warmth
- **Soft Clipping**: Adds harmonics for presence on small speakers
- **Tube Saturation**: Warmth without mud

### 808 Note Choices & Patterns

- Root note follows harmony (Am → A1 or A2, Dm → D1/D2, Em → E1/E2)
- **Funk 150**: Short, dry 808 with ghost notes between kick hits
- **Trap funk**: Long sustain with pitch glides (portamento)
- **Basic pattern**: A - E - A - G (in key of Am) for groove
- **Sync with kick**: 808 usually plays same rhythm or complementary pattern
- **Octave jumps**: Drop to lower octave on final beat of phrase for impact

### Sidechain Compression (Essential)

```
Kick triggers sidechain on 808
Threshold: -18 to -24dB
Ratio: 4:1 to 6:1
Attack: 1-5ms (fast)
Release: 50-120ms (matches kick decay)
Gain reduction: 2-6dB
```

**FL Studio sidechain setup:**
1. Route kick mixer track to sidechain input on 808 mixer track
2. Insert **Fruity Limiter** on 808 track (compression mode)
3. Click the sidechain arrow, select kick track
4. Adjust threshold/ratio/release
5. Alternative: **Gross Beat** for rhythmic pumping effect

### Monomized Low End

- 808 must be **MONO** below ~120Hz
- Use **Fruity Stereo Shaper** or **Maximus** to mono the low band
- EQ: HPF 808 at ~30Hz, LPF at ~200Hz for sub area

---

## 4. Harmony and Melody

### Common Chord Progressions

| Progression | Key | Feel |
|---|---|---|
| Am – F – C – G (i-VI-III-VII) | Am | Classic pop/funk |
| Em – C – G – D (i-VI-III-VII) | Em | Dark, driving |
| Dm – Bb – F – C (i-VI-III-VII) | Dm | Melancholic |
| C – G – Am – F (I-V-vi-IV) | C | Brighter, melody-friendly |

### Melody Guidelines

- **Funk melody**: Sung hooks, simple repeating phrases
- **Funk 150 / Mandelão**: Often no melody — just beat + MC vocals
- **Synth lead**: Short notes, minor scale, octave-based
- **Piano**: Block chords, simple voicings
- **Pads**: Electric piano or warm synth pad for harmonic filler
- **Brazilian Phonk**: Pitch-shifted samples, guitar/berimbau layers

### FL Studio Tools for Melody

- **Fruity Slicer**: Chop and rearrange sample loops
- **Pitcher**: Pitch-shift samples to match key
- **Edison**: Time-stretch and pitch manipulation
- **Gross Beat**: Stutter/glitch effects on melodic elements
- Piano Roll: Scale highlighting (right-click → helpers → scale highlights)

---

## 5. Vocal Processing

### Signal Chain Order

```
1. Autotune (FIRST)
2. EQ (subtractive)
3. Compression
4. De-esser
5. EQ (additive/boost)
6. Reverb
7. Delay
8. Saturation (optional)
```

### Autotune Configuration

| Style | Retune Speed | Plugin Recommendations |
|---|---|---|
| Funk 150 (MC) | **5-10ms** (aggressive, almost robotic) | Auto-Tune Pro, Waves Tune RT |
| Trap Funk | **8-15ms** (present but musical) | Auto-Tune Pro, MAutoPitch |
| Trap Melódico | **15-25ms** (subtle) | Auto-Tune Pro |
| Funk Melody | **10-20ms** (balanced) | Waves Tune RT, MAutoPitch |

**Scale / Key Selection**: Set to song key (Am, Em, Dm)
**Humanize**: 20-40% for naturalness
**Flex / Formant**: Keep at 100% (or adjust for "chipmunk" effect)

**Free/Cheap Autotune Options for FL Studio:**
| Plugin | Price | Quality |
|---|---|---|
| Auto-Tune Pro | $399 / $24.99/mo | ⭐⭐⭐⭐⭐ |
| Waves Tune Real-Time | ~$50-250 (sales) | ⭐⭐⭐⭐ |
| Pitcher (FL Studio built-in) | Free | ⭐⭐⭐ |
| MAutoPitch (Melda) | Free | ⭐⭐⭐ |
| GSnap | Free | ⭐⭐⭐ |

### Vocal EQ (Funk-specific)

| Frequency | Action | Reason |
|---|---|---|
| 20-80Hz | **High-pass filter** | Remove rumble |
| 100Hz | **High-pass (24dB/oct)** | Clear out sub, let tamborzão breathe |
| 250Hz | **Cut -3dB** (wide Q ~1.0) | Remove muddiness |
| 4-5kHz | **Boost +3dB** (bell, Q ~1.5) | Presence, cut through beat |
| 8-10kHz | **Gentle shelf +1-2dB** | Air/brilliance |
| 10-20kHz | **High shelf or shelf cut** if sibilant | Control air |

**Plugin**: Fruity Parametric EQ 2 (free, built-in), FabFilter Pro-Q 3

### Vocal Compression

| Parameter | Setting |
|---|---|
| Ratio | 3:1 to 5:1 |
| Attack | 10-30ms |
| Release | 40-80ms |
| Threshold | -18 to -24dB |
| Gain reduction | 4-6dB |
| Makeup gain | 2-4dB |

- **Heavy compression** is characteristic — voice must sit ON TOP of everything
- Consider **parallel compression** (dry + heavily compressed blend)
- **CLAdius** or **RVox** for quick results

### De-essing

- **Fruity Limiter** with sidechain (listen for sibilance) or dedicated de-esser
- Frequency range: 5-8kHz
- Reduction: 3-6dB on sibilant consonants

### Reverb & Delay

| Effect | Setting |
|---|---|
| Reverb type | Short room or plate |
| Decay | 0.4-0.8s (short, vocal stays forward) |
| Pre-delay | 10-20ms |
| Mix | 15-25% |
| Delay type | 1/4 or 1/8 note ping-pong |
| Feedback | 20-30% |
| Delay mix | 10-20% (only on phrases, not constant) |

### Ad-libs

- **"Uh!", "Vai!", "Tá?", "É o bonde!"** etc.
- **Pan**: Wide L/R (50-80%)
- **Volume**: 3-6dB quieter than lead
- **Reverb**: More than lead (30-50% wet)
- **Delay**: Ping-pong 1/8 notes, 2-3 repeats

---

## 6. Mixing Chain

### Kick / Tamborzão Mixing

| Parameter | Setting |
|---|---|
| EQ | Band-pass 40-100Hz, cut above 200Hz |
| Output | **MONO** |
| Compression | Attack 10-20ms, Release 60-120ms, Ratio 3:1 |
| Volume | **Dominant** — loudest element after vocal |
| Saturation | Light tape or tube for harmonics |

### Clap / Snare Mixing

| Parameter | Setting |
|---|---|
| EQ | HPF ~200Hz, boost 1-2kHz for snap |
| Reverb | Short room, decay 0.3s, mix 15-20% |
| Compression | Attack 1-5ms, Ratio 4:1, 2-4dB reduction |
| Volume | Medium-high |

### Hi-Hat Mixing

| Parameter | Setting |
|---|---|
| EQ | HPF ~300Hz, gentle cut 2-4kHz if harsh |
| Volume | Low-medium (background) |
| Pan | Slight L/R variation per hit (±15%) |
| Stereo spread | Narrow to mono |

### 808 / Bass Mixing

| Parameter | Setting |
|---|---|
| EQ | HPF ~30Hz, LPF ~200Hz |
| Mono | Below 120Hz (use Stereo Shaper/Maximus) |
| Sidechain | Threshold -18 to -24dB, Ratio 4:1, Release 50-120ms |
| Volume | High (foundation of track) |
| Distortion | Fast Dist / soft clip, mix 20-40% |

### Volume Balance Reference

| Element | Relative Level |
|---|---|
| Vocal (MC) | **0dB (reference)** |
| Tamborzão / Kick | -3 to -6dB |
| 808 | -3 to -6dB |
| Snare / Clap | -6 to -9dB |
| Hi-Hat | -12 to -18dB |
| Melody / Pads | -10 to -18dB |
| Percussion | -12 to -20dB |

### Panning Guide

| Element | Pan Position |
|---|---|
| Kick, 808, Vocal | **Center (mono)** |
| Clap | Center or slight (L5-R5) |
| Hi-Hats | Alternating L/R ±15% |
| Percussion | L20-R50 for stereo depth |
| Ad-libs | L50-R80 (wide) |
| Melody layers | L20-R30 |

### Bus Processing

**Drum Bus:**
- Light glue compression: Ratio 2:1, Attack 10ms, Release 50ms, 1-2dB reduction
- **Fruity Compressor** or **The Glue**

**Master Bus (before mastering):**
- Subtle saturation (console emulation)
- Light EQ (HPF 20Hz, slight high shelf)
- **Master limiter off** — leave for mastering stage

---

## 7. Mastering

### Master Chain

```
1. HPF at 20-25Hz (subsonic cleanup)
2. Multiband compression (Maximus / Ozone / C4)
3. EQ (final shaping)
4. Clipper (optional, for loudness)
5. Limiter
```

### Multiband Settings (Maximus)

| Band | Frequency | Compression | Ratio |
|---|---|---|---|
| Low | 20-120Hz | Light | 2:1 |
| Mid | 120Hz-5kHz | Medium | 3:1 |
| High | 5kHz-20kHz | Light | 1.5:1 |

### Limiter Settings

| Parameter | Value |
|---|---|
| Ceiling | **-0.3dB** to **-1.0dB** (for streaming) |
| Gain (reduction on peaks) | Up to **6-8dB** gain reduction (depends on style) |
| Attack | 5-10ms |
| Release | 50-100ms |
| Lookahead | 1-3ms |

### Loudness Targets

| Platform | Integrated LUFS | True Peak |
|---|---|---|
| Spotify | -14 LUFS | -1.0dB TP |
| YouTube | -14 LUFS | -1.0dB TP |
| Apple Music | -16 LUFS | -1.0dB TP |
| **Funk club/mixtape** | **-8 to -10 LUFS** (loud) | -0.3dB TP |
| **Streaming master** | **-10 to -12 LUFS** | -1.0dB TP |

### FL Studio Mastering Tools

| Plugin | Purpose |
|---|---|
| **Maximus** | Multiband compression, limiting, loudness |
| **Fruity Limiter** | Final limiting (ceiling, gain staging) |
| **Fruity Parametric EQ 2** | Final EQ shaping |
| **Fruity Compressor** | Glue compression |
| **Waves L2/L3** | Alternative limiting |
| **iZotope Ozone** | Full mastering suite (if available) |
| **FabFilter Pro-L 2** | Precision limiting |

### Master Reference

- **Glue compression**: Gentle, ratio 1.5:1 to 2:1, 1-2dB reduction
- **Final limiter**: Ceiling -0.3dB, push gain until 3-6dB reduction on peaks
- **Loudness**: Target -10 LUFS for competitive funk
- **A/B compare** against reference tracks (MC Kevin, MC Fioti, etc.)

---

## 8. FL Studio Templates and Workflow Tips

### Project Template Structure

```
Master Channel
├── Mixer 1: Kick / Tamborzão
├── Mixer 2: Snare / Clap
├── Mixer 3: Hi-Hat
├── Mixer 4: 808 Bass
├── Mixer 5: Percussion
├── Mixer 6: Melody / Pads
├── Mixer 7: Lead Vocal
├── Mixer 8: Vocal Ad-libs (L)
├── Mixer 9: Vocal Ad-libs (R)
├── Mixer 10: Reverb Send
└── Mixer 11: Delay Send
```

### Color Coding Convention

| Color | Element |
|---|---|
| Yellow | Kick drums |
| Green | Snares / Claps |
| Blue | Hi-hats / Cymbals |
| Red | 808 / Bass |
| Orange | Melody / Synth |
| Purple | Vocals |
| Gray | FX / Sends |

### FL Studio Shortcuts for Faster Workflow

| Shortcut | Action |
|---|---|
| **F5** | Toggle Playlist |
| **F6** | Toggle Step Sequencer |
| **F7** | Toggle Piano Roll |
| **F9** | Toggle Mixer |
| **Ctrl+L** | Link selected channel to mixer |
| **Ctrl+Shift+C** | Clone pattern |
| **Alt+↓** | Move selected notes down 1 semitone |
| **Alt+↑** | Move selected notes up 1 semitone |
| **Shift+click (volume)** | Fine volume adjustment |
| **Ctrl+click (Step Seq)** | Select/deselect all steps |
| **Ctrl+B** | Brush tool in Piano Roll (quick note drawing) |
| **Alt+T** | Graph editor toggle |
| **Ctrl+E** | Open sample in Edison (from Channel Rack) |
| **Ctrl+Shift+E** | Export MP3/WAV |

### Essential FL Studio Plugins for Funk

| Plugin | Use |
|---|---|
| **3x Osc** | 808 bass (sine wave sub) |
| **FLEX** | 808 presets, pads, keys |
| **Fruity Parametric EQ 2** | All EQ tasks |
| **Fruity Limiter** | Compression, sidechain, final limiting |
| **Fruity Compressor** | Bus/drum compression |
| **Maximus** | Mastering multiband |
| **Gross Beat** | Sidechain pumping, stutter effects |
| **Pitcher** | Autotune (free option), pitch shifting |
| **Fruity Fast Dist** | Bass distortion |
| **Blood Overdrive** | Saturation |
| **Fruity Reverb 2** | Reverb |
| **Fruity Delay 3** | Ping-pong delay |
| **Fruity Slicer / SliceX** | Sample chopping |
| **Fruity Stereo Shaper** | Mono low-end, stereo widening |
| **Edison** | Recording, editing, pitch/time manipulation |

### Recommended Drum Kits & Sample Sources

| Source | Notes |
|---|---|
| **Emite Beats - Funk Consciente Drum Kit** (free) | Google Drive link in FL Studio Full article |
| **GAiOLA** Packs | Funk 150 BPM specific |
| **AudioPlug** | 2,500+ Brazilian funk samples |
| **Splice** | Search "baile funk", "funk carioca", "tamborzão" |
| **Sample Focus** | Phonk drum loops, phonk melodies |
| **YouTube** | "Kit de pontos funk grátis" |
| **Produsso** | Professional stems for study |

### Workflow Checklist (30-Minute Beat Challenge)

| Time | Task |
|---|---|
| 0-5 min | Set BPM (150 or 130), create mixer template, load drum sounds |
| 5-15 min | Program kick (syncopated tamborzao), clap on 2&4, hi-hat 16ths with velocity |
| 15-20 min | Add 808 sub-bass on root note, sidechain to kick |
| 20-25 min | Create melody/pad loop (optional) — minor scale, 4-bar loop |
| 25-30 min | Record/generate vocal hook — autotune, eq, compression |
| After | Mix balance, add ad-libs, export reference |

### Arrangement Template

```
Intro (8 bars)      – Beat only, no 808 or minimal elements
Verse 1 (16 bars)   – Full beat + vocal
Pre-chorus (8 bars) – Buildup (hi-hat roll, filter sweep)
Chorus (16 bars)    – Full energy, all elements
Verse 2 (16 bars)   – Drop some elements, bring back
Chorus (16 bars)    – Full again
Bridge (8 bars)     – Breakdown, percussion only
Final Chorus (16 bars) – Maximum energy
Outro (8 bars)      – Fade out, cut elements
```

---

## Quick Reference Cheat Sheet

### Funk Vocal EQ Cheat Sheet
```
HPF at 100Hz
Cut -3dB at 250Hz (mud)
Boost +3dB at 4-5kHz (presence)
Gentle shelf +1-2dB at 10kHz (air)
```

### Autotune Speed Cheat Sheet
```
Funk 150 MC:  5-10ms (robotic)
Trap Funk:    8-15ms (present)
Funk Melody:  10-20ms (balanced)
```

### Sidechain Cheat Sheet
```
Kick → 808:
  Threshold: -18 to -24dB
  Ratio: 4:1 to 6:1
  Release: 50-120ms
  Gain reduction: 2-6dB
```

### Compression Cheat Sheet
```
Kick:    Attack 10-20ms, Release 60-120ms, Ratio 3:1
Snare:   Attack 1-5ms,    Release 40-80ms,    Ratio 4:1
Vocal:   Attack 10-30ms,  Release 40-80ms,    Ratio 3:1 to 5:1
Master:  Attack 5-10ms,   Release 50-100ms,   Ratio 1.5:1 to 2:1
```

### Mastering Cheat Sheet
```
Ceiling: -0.3dB to -1.0dB (streaming = -1.0dB)
Gain reduction on peaks: 3-6dB
Target LUFS: -10 to -12 LUFS (streaming competitive)
```
