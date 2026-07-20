"""
extract.py — Extract preview frames from a video clip for AI analysis.

Extracts 3 frames: start (1s in), middle, and near-end.
Output PNGs are used by the analyze command to get grade recommendations.
"""

import subprocess
import os
from pathlib import Path


def get_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())


def extract_frames(video_path: str, output_dir: str = None) -> list[str]:
    """
    Extract 3 preview frames from a video clip.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory to save frames. Defaults to same dir as video.

    Returns:
        List of paths to extracted PNG files [start, mid, end].
    """
    video_path = str(video_path)
    input_path = Path(video_path)

    if output_dir is None:
        output_dir = input_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem
    duration = get_duration(video_path)

    timestamps = {
        "start": 1.0,
        "mid": duration / 2,
        "end": max(duration - 2, duration * 0.9),
    }

    frame_paths = []
    for label, ts in timestamps.items():
        ts = min(ts, duration - 0.1)
        out_file = str(output_dir / f"{stem}_{label}.png")
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", video_path,
                "-frames:v", "1",
                "-q:v", "2",
                out_file
            ],
            capture_output=True, check=True
        )
        frame_paths.append(out_file)
        print(f"  Extracted {label} frame → {out_file}")

    return frame_paths


def extract_frames_batch(video_paths: list[str], output_dir: str = None) -> dict:
    """Extract frames from multiple clips. Returns {video_path: [frame_paths]}."""
    results = {}
    for video_path in video_paths:
        print(f"\nExtracting frames: {Path(video_path).name}")
        results[video_path] = extract_frames(video_path, output_dir)
    return results
