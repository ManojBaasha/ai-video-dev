"""
AI picks the best grade for each clip individually, then applies it.
Each clip gets analyzed separately — day/night/indoor all get the right treatment.

Requires: ANTHROPIC_API_KEY env var, pip install anthropic
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyze import analyze_clip
from src.compile import get_clips

CLIPS_DIR = "clips/"
OUTPUT_DIR = "graded/"

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

clips = get_clips(CLIPS_DIR)
print(f"Analyzing {len(clips)} clips...\n")

results = []
for clip in clips:
    stem = Path(clip).stem
    out = str(Path(OUTPUT_DIR) / f"{stem}_graded.mov")
    result = analyze_clip(clip, auto_apply=True, output_path=out)
    results.append(result)
    print(f"  {stem}: {result.get('grade')} ({result.get('confidence')})\n")

print(f"Done — {len(results)} clips graded in {OUTPUT_DIR}")
