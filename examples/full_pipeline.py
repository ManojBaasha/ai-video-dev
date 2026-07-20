"""
Full pipeline: AI grade each clip → compile → add music → end card.
Edit the CONFIG block at the top for your project.
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyze import analyze_clip
from src.compile import compile_clips, get_clips
from src.audio import add_audio
from src.overlay import add_end_card

# --- CONFIG ---
CLIPS_DIR = "clips/"
MUSIC = "song.mp3"
OUTPUT = "final.mov"
END_TEXT = "fin."
END_DURATION = 5.0
RESOLUTION = "1080:1920"
# --------------

clips = get_clips(CLIPS_DIR)
if not clips:
    print(f"No clips found in {CLIPS_DIR}")
    sys.exit(1)

print(f"Pipeline: {len(clips)} clips → {OUTPUT}\n")

with tempfile.TemporaryDirectory() as tmp:
    graded_dir = Path(tmp) / "graded"
    graded_dir.mkdir()

    # Step 1: AI grade each clip
    graded = []
    for clip in clips:
        stem = Path(clip).stem
        out = str(graded_dir / f"{stem}_graded.mov")
        analyze_clip(clip, frames_dir=tmp, auto_apply=True, output_path=out)
        graded.append(out)

    # Step 2: compile
    compiled = str(Path(tmp) / "compiled.mov")
    compile_clips(graded, compiled, resolution=RESOLUTION)

    # Step 3: music
    with_audio = str(Path(tmp) / "with_audio.mov")
    add_audio(compiled, MUSIC, with_audio)

    # Step 4: end card
    add_end_card(with_audio, OUTPUT, text=END_TEXT, duration=END_DURATION)

print(f"\nDone — {OUTPUT}")
