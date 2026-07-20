"""
Grade every clip in a folder with a specific grade.

Usage:
    python examples/grade_all_clips.py clips/ "neon rain" --output graded/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.grades import apply_grade_batch
from src.compile import get_clips

CLIPS_DIR = "clips/"
GRADE = "Neon Rain - Night City"
OUTPUT_DIR = "graded/"

clips = get_clips(CLIPS_DIR)
print(f"Found {len(clips)} clips")

apply_grade_batch(clips, OUTPUT_DIR, GRADE)
print(f"\nDone — graded clips in {OUTPUT_DIR}")
