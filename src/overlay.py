"""
overlay.py — Add text overlays and end cards to videos.

Requires ffmpeg compiled with freetype/drawtext support.
On macOS: brew install homebrew-ffmpeg/ffmpeg/ffmpeg
"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass, field


def _find_default_font() -> str:
    candidates = [
        "/System/Library/Fonts/Avenir Next.ttc",                                    # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",                          # Linux (Debian/Ubuntu)
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",          # Linux (RHEL/Fedora)
        "C:/Windows/Fonts/arial.ttf",                                               # Windows
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]  # macOS default; ffmpeg will emit a clear error if missing


DEFAULT_FONT = _find_default_font()
DEFAULT_FONT_SIZE = 28
DEFAULT_FONT_COLOR = "white"


@dataclass
class TextOverlay:
    """A single timed text overlay."""
    text: str
    start: float          # seconds
    end: float            # seconds
    font: str = DEFAULT_FONT
    font_size: int = DEFAULT_FONT_SIZE
    color: str = DEFAULT_FONT_COLOR
    x: str = "(w-text_w)/2"   # centered horizontally
    y: str = "h-h/6"          # near bottom


def build_drawtext_filter(overlays: list[TextOverlay]) -> str:
    """Build a chained drawtext filter from a list of TextOverlay objects."""
    filters = []
    for o in overlays:
        f = (
            f"drawtext=fontfile='{o.font}'"
            f":text='{o.text}'"
            f":fontcolor={o.color}"
            f":fontsize={o.font_size}"
            f":x={o.x}"
            f":y={o.y}"
            f":enable='between(t,{o.start},{o.end})'"
        )
        filters.append(f)
    return ",".join(filters)


def add_overlays(
    video_path: str,
    output_path: str,
    overlays: list[TextOverlay],
) -> str:
    """
    Add text overlays to a video.

    Args:
        video_path: Input video.
        output_path: Output video.
        overlays: List of TextOverlay objects.

    Returns:
        Path to output file.
    """
    if not overlays:
        raise ValueError("No overlays provided.")

    filter_str = build_drawtext_filter(overlays)
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", filter_str,
        "-c:v", "prores_ks", "-profile:v", "1",
        "-c:a", "copy",
        output_path,
    ]

    print(f"Adding {len(overlays)} text overlay(s) → {output_path}")
    subprocess.run(cmd, check=True)
    print(f"  → {output_path}")
    return output_path


def add_end_card(
    video_path: str,
    output_path: str,
    text: str = "fin.",
    duration: float = 5.0,
    resolution: str = "1080x1920",
    font: str = DEFAULT_FONT,
    font_size: int = 30,
) -> str:
    """
    Append a black end card with centered text to a video.

    Args:
        video_path: Input video (with or without audio).
        output_path: Output video.
        text: Text to display on end card.
        duration: Duration of end card in seconds.
        resolution: Resolution string, e.g. "1080x1920".
        font: Path to font file.
        font_size: Font size.

    Returns:
        Path to output file.
    """
    # Get video duration for audio padding
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture_output=True, text=True, check=True
    )
    video_duration = float(result.stdout.strip())
    fade_out_start = video_duration - 3

    w, h = resolution.split("x")

    filter_complex = (
        f"color=black:s={w}x{h}:d={duration}[black];"
        f"[black]drawtext=fontfile='{font}'"
        f":text='{text}'"
        f":fontcolor=white"
        f":fontsize={font_size}"
        f":x=(w-text_w)/2:y=(h-text_h)/2[endcard];"
        f"[0:v][endcard]concat=n=2:v=1:a=0[outv];"
        f"[0:a]afade=t=out:st={fade_out_start:.2f}:d=3,apad=pad_dur={duration}[outa]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "prores_ks", "-profile:v", "1",
        "-c:a", "aac", "-b:a", "256k",
        output_path,
    ]

    print(f"Adding end card: '{text}' ({duration}s)")
    subprocess.run(cmd, check=True)
    print(f"  → {output_path}")
    return output_path
