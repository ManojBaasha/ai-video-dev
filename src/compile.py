"""
compile.py — Concatenate video clips into a single ProRes output.

All clips are scaled to a target resolution before concatenation.
Defaults to 1080x1920 (vertical/portrait).
"""

import subprocess
import tempfile
import os
from pathlib import Path


DEFAULT_RESOLUTION = "1080:1920"


def get_clips(clips_dir: str, extensions: tuple = (".mov", ".mp4", ".MOV", ".MP4")) -> list[str]:
    """Get all video clips from a directory, sorted by filename."""
    clips_dir = Path(clips_dir)
    clips = []
    for ext in extensions:
        clips.extend(clips_dir.glob(f"*{ext}"))
    return sorted(str(c) for c in clips)


def compile_clips(
    clips: list[str],
    output_path: str,
    resolution: str = DEFAULT_RESOLUTION,
    prores: bool = True,
) -> str:
    """
    Concatenate a list of clips into a single output file.

    Args:
        clips: List of input video file paths (in order).
        output_path: Path for the compiled output.
        resolution: Target WxH, e.g. "1080:1920" for vertical.
        prores: If True, encode output as ProRes HQ.

    Returns:
        Path to the output file.
    """
    if not clips:
        raise ValueError("No clips provided to compile.")

    width, height = resolution.split(":")
    scale_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    )

    # Write concat list to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        concat_file = f.name
        for clip in clips:
            f.write(f"file '{clip}'\n")

    codec_args = ["-c:v", "prores_ks", "-profile:v", "1", "-an"] if prores else ["-c", "copy"]

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-vf", scale_filter,
            *codec_args,
            output_path,
        ]
        print(f"Compiling {len(clips)} clips → {output_path}")
        subprocess.run(cmd, check=True)
        print(f"  Done: {output_path}")
    finally:
        os.unlink(concat_file)

    return output_path


def compile_from_dir(
    clips_dir: str,
    output_path: str,
    resolution: str = DEFAULT_RESOLUTION,
    prores: bool = True,
) -> str:
    """Compile all clips from a directory (sorted by filename)."""
    clips = get_clips(clips_dir)
    if not clips:
        raise ValueError(f"No video clips found in {clips_dir}")
    print(f"Found {len(clips)} clips in {clips_dir}")
    return compile_clips(clips, output_path, resolution=resolution, prores=prores)
