"""
grades.py — Load and apply color grade presets.

Each grade is a .txt file in the grades/ directory containing
the ffmpeg filter chain and metadata about when to use it.
"""

import subprocess
import re
from pathlib import Path

GRADES_DIR = Path(__file__).parent.parent / "grades"


def list_grades() -> list[str]:
    """Return names of all available grades (without .txt extension)."""
    return [f.stem for f in sorted(GRADES_DIR.glob("*.txt"))]


def load_grade(name: str) -> dict:
    """
    Load a grade preset by name.

    Returns dict with keys: name, filter_chain, description, notes
    """
    # Match partial name case-insensitively
    matches = [f for f in GRADES_DIR.glob("*.txt") if name.lower() in f.stem.lower()]
    if not matches:
        available = ", ".join(list_grades())
        raise ValueError(f"Grade '{name}' not found. Available: {available}")
    if len(matches) > 1:
        names = ", ".join(f.stem for f in matches)
        raise ValueError(f"Ambiguous grade '{name}'. Matches: {names}")

    grade_file = matches[0]
    content = grade_file.read_text()

    # Parse the filter chain — it's the line after "FFmpeg filter chain:"
    filter_chain = None
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "filter chain:" in line.lower() and i + 1 < len(lines):
            # Next non-empty line is the filter chain
            for j in range(i + 1, len(lines)):
                candidate = lines[j].strip()
                if candidate and not candidate.startswith("#"):
                    filter_chain = candidate
                    break
        if filter_chain:
            break

    if not filter_chain:
        raise ValueError(f"Could not parse filter chain from {grade_file.name}")

    return {
        "name": grade_file.stem,
        "filter_chain": filter_chain,
        "raw": content,
    }


def apply_grade(
    input_path: str,
    output_path: str,
    grade_name: str,
    prores: bool = True,
    dry_run: bool = False,
) -> str:
    """
    Apply a color grade to a video clip.

    Args:
        input_path: Source video file.
        output_path: Output video file.
        grade_name: Name of the grade preset to apply.
        prores: If True, encode as ProRes HQ. Otherwise copy codec.
        dry_run: If True, print the ffmpeg command without running it.

    Returns:
        Path to the output file.
    """
    grade = load_grade(grade_name)
    filter_chain = grade["filter_chain"]

    codec_args = ["-c:v", "prores_ks", "-profile:v", "1", "-c:a", "copy"] if prores else ["-c", "copy"]

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", filter_chain,
        *codec_args,
        output_path,
    ]

    print(f"Applying grade: {grade['name']}")
    if dry_run:
        print("DRY RUN — command:")
        print(" ".join(cmd))
        return output_path

    subprocess.run(cmd, check=True)
    print(f"  → {output_path}")
    return output_path


def apply_grade_batch(
    input_paths: list[str],
    output_dir: str,
    grade_name: str,
    prores: bool = True,
) -> list[str]:
    """Apply the same grade to multiple clips."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for input_path in input_paths:
        stem = Path(input_path).stem
        ext = ".mov" if prores else Path(input_path).suffix
        out = str(output_dir / f"{stem}_graded{ext}")
        apply_grade(input_path, out, grade_name, prores=prores)
        outputs.append(out)
    return outputs
