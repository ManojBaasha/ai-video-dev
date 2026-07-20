"""
audio.py — Add music to a video with automatic fade in/out.
"""

import subprocess
from pathlib import Path


def add_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    fade_in: float = 2.0,
    fade_out: float = 3.0,
    audio_offset: float = 0.0,
) -> str:
    """
    Add a music track to a video with fade in and fade out.

    Args:
        video_path: Input video (no audio needed).
        audio_path: Music file (mp3, aac, wav, etc.)
        output_path: Output video path.
        fade_in: Fade-in duration in seconds.
        fade_out: Fade-out duration in seconds.
        audio_offset: Start music at this offset in the audio file (seconds).

    Returns:
        Path to the output file.
    """
    # Get video duration
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        capture_output=True, text=True, check=True
    )
    duration = float(result.stdout.strip())
    fade_out_start = duration - fade_out

    filter_complex = (
        f"[1:a]atrim={audio_offset}:{audio_offset + duration},"
        f"afade=t=in:st=0:d={fade_in},"
        f"afade=t=out:st={fade_out_start:.2f}:d={fade_out}[a]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "256k",
        output_path,
    ]

    print(f"Adding audio: {Path(audio_path).name}")
    print(f"  Fade in: {fade_in}s | Fade out: {fade_out}s (at {fade_out_start:.1f}s)")
    subprocess.run(cmd, check=True)
    print(f"  → {output_path}")
    return output_path
