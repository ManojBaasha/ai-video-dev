"""
Compile all graded clips into one file and add music.
Clips are sorted by filename — rename them to control order (01_, 02_, etc).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compile import compile_from_dir
from src.audio import add_audio

GRADED_DIR = "graded/"
MUSIC = "song.mp3"
OUTPUT = "final.mov"

FADE_IN = 2.0   # seconds
FADE_OUT = 3.0  # seconds

# Step 1: compile
compiled = "compiled.mov"
compile_from_dir(GRADED_DIR, compiled, resolution="1080:1920")

# Step 2: add music
add_audio(compiled, MUSIC, OUTPUT, fade_in=FADE_IN, fade_out=FADE_OUT)

print(f"\nDone — {OUTPUT}")
