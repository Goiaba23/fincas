"""Analyze FL Studio Empty template with PyFLP."""
import pyflp

TEMPLATE = r"C:\Users\alerrandro\Music\Nova pasta (2)\template.flp"

project = pyflp.parse(TEMPLATE)
print(f"Project: {project}")
print(f"  Format: {project.format}")
print(f"  PPQ: {project.ppq}")
print(f"  Version: {project.version}")
print(f"  Tempo: {project.tempo}")
print(f"  Channels count: {project.channel_count}")
print(f"  Title: {project.title}")

print(f"\n=== Channels ({len(list(project.channels))}) ===")
for ch in project.channels:
    print(f"  {ch!r}")
    print(f"    type: {type(ch).__name__}")
    if hasattr(ch, 'sample_path'):
        sp = ch.sample_path
        if sp:
            print(f"    sample_path: {sp}")
        else:
            print(f"    sample_path: None (can set)")
    if hasattr(ch, 'internal_name'):
        print(f"    internal_name: {ch.internal_name}")
    if hasattr(ch, 'display_name'):
        print(f"    display_name: {ch.display_name}")

print(f"\n=== Patterns ===")
patterns = project.patterns
print(f"  Pattern count: {len(list(patterns))}")
for p in patterns:
    print(f"  {p!r}")

print(f"\n=== Mixer ===")
mx = project.mixer
print(f"  Inserts: {len(list(mx.inserts))}")
for ins in mx.inserts:
    print(f"  {ins!r}")
