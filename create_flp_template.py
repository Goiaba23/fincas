"""Create a minimal FLP template with empty sampler channels, then modify it with PyFLP."""

import struct
import os
import sys

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.flp")

def create_minimal_flp(num_samplers=1):
    """
    Create a minimal FLP file manually by writing bytes.
    
    FLP Binary Format:
    - Header: FLhd (4B) + size=6 (4B LE) + format=0 (2B LE) + num_ch (2B LE) + ppq=96 (2B LE)
    - Data: FLdt (4B) + data_size (4B LE) + events...
    
    Events:
    - Byte events (0-63): 1B id + 1B data
    - Word events (64-127): 1B id + 2B data  
    - DWord events (128-191): 1B id + 4B data
    - Text events (192-207): 1B id + varint(len) + data
    - Data events (208+): 1B id + varint(len) + data
    
    Required minimum events:
    1. FLVersion (TEXT+7=199): "21.0.0"
    2. _Volume (12): 128 (0x80)
    3. For each sampler channel:
       - ChannelID.Type (21): 0 (Sampler)
       - ChannelID.IsEnabled (0): 1
       - PluginID.Color (128): RGBA (4 bytes)
       - ChannelID.New (64): channel ID (2 bytes)
       - PluginID.Name (TEXT+11=203): channel name
    """
    buf = bytearray()
    
    # --- Header ---
    header = struct.pack('<4sIh2H', b'FLhd', 6, 0, num_samplers, 96)
    buf.extend(header)
    
    # --- Data marker (size placeholder) ---
    buf.extend(b'FLdt')
    data_size_pos = len(buf)
    buf.extend(struct.pack('<I', 0))  # placeholder
    
    events_data = bytearray()
    
    # --- Event 1: FLVersion (TEXT+7=199) ---
    version_str = b'21.0.0'
    events_data.extend(bytes([199]))  # id
    # VarInt length
    events_data.extend(_varint(len(version_str)))
    events_data.extend(version_str)
    
    # --- Event 2: _Volume (12) ---
    events_data.extend(bytes([12, 128]))  # id=12, value=128
    
    # --- Event 3: Title (TEXT+2=194) ---
    title = b'Template'
    events_data.extend(bytes([194]))
    events_data.extend(_varint(len(title)))
    events_data.extend(title)
    
    # --- Create sampler channels ---
    for ch_idx in range(num_samplers):
        # ChannelID.New (64) - marks start of a channel
        events_data.extend(struct.pack('<BH', 64, ch_idx))
        
        # ChannelID.Type (21) - 0 = Sampler
        events_data.extend(bytes([21, 0]))
        
        # ChannelID.IsEnabled (0) - 1 = enabled
        events_data.extend(bytes([0, 1]))
        
        # ChannelID.RoutedTo (22) - -1 = Current insert
        events_data.extend(bytes([22, 255]))  # -1 as signed byte
        
        # PluginID.Color (128) - RGBA
        events_data.extend(struct.pack('<B4B', 128, 92, 101, 106, 255))  # granite gray
        
        # ChannelID.Cutoff (WORD+7=71) - default
        events_data.extend(struct.pack('<BH', 71, 1024))
        
        # ChannelID._VolWord (WORD+8=72) - default volume 10000
        events_data.extend(struct.pack('<BH', 72, 10000))
        
        # ChannelID._PanWord (WORD+9=73) - center pan 6400
        events_data.extend(struct.pack('<BH', 73, 6400))
        
        # ChannelID.Preamp (WORD+10=74) - default 0
        events_data.extend(struct.pack('<BH', 74, 0))
        
        # ChannelID.FadeOut (WORD+11=75) - default 0
        events_data.extend(struct.pack('<BH', 75, 0))
        
        # ChannelID.FadeIn (WORD+12=76) - default 0
        events_data.extend(struct.pack('<BH', 76, 0))
        
        # ChannelID.Resonance (WORD+19=83) - default 0
        events_data.extend(struct.pack('<BH', 83, 0))
        
        # ChannelID.StereoDelay (WORD+21=85) - default 2048
        events_data.extend(struct.pack('<BH', 85, 2048))
        
        # ChannelID.Pogo (WORD+22=86) - default 256
        events_data.extend(struct.pack('<BH', 86, 256))
        
        # ChannelID.TimeShift (WORD+25=89) - default 0
        events_data.extend(struct.pack('<BH', 89, 0))
        
        # ChannelID.Swing (WORD+33=97) - default 128 (max)
        events_data.extend(struct.pack('<BH', 97, 128))
        
        # PluginID.Name (TEXT+11=203)
        ch_name = f'Sampler {ch_idx + 1}'.encode('utf-16-le')
        events_data.extend(bytes([203]))
        events_data.extend(_varint(len(ch_name)))
        events_data.extend(ch_name)
        
        # SamplePath (TEXT+4=196) - empty sample
        events_data.extend(bytes([196]))
        events_data.extend(_varint(0))
    
    # --- Write events data ---
    buf.extend(events_data)
    
    # Fix data size
    data_size = len(events_data)
    buf[data_size_pos:data_size_pos+4] = struct.pack('<I', data_size)
    
    return bytes(buf)


def _varint(value):
    """Encode a value as a variable-length integer (same as FL Studio uses)."""
    result = bytearray()
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


if __name__ == "__main__":
    # Create template
    flp_data = create_minimal_flp(num_samplers=4)
    
    with open(TEMPLATE_PATH, "wb") as f:
        f.write(flp_data)
    
    print(f"Created template: {TEMPLATE_PATH}")
    print(f"Size: {len(flp_data)} bytes")
    
    # Verify by parsing with PyFLP
    try:
        import pyflp
        project = pyflp.parse(TEMPLATE_PATH)
        print(f"Parsed OK: {project}")
        print(f"  Format: {project.format}")
        print(f"  PPQ: {project.ppq}")
        print(f"  Channels: {project.channel_count}")
        for ch in project.channels:
            print(f"  - {ch!r}: type={type(ch).__name__}")
            if hasattr(ch, 'sample_path'):
                print(f"    sample_path: {ch.sample_path}")
    except Exception as e:
        print(f"Parse error: {e}")
        import traceback
        traceback.print_exc()
