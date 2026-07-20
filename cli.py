#!/usr/bin/env python3
"""
aivid — AI-first video editing CLI

Commands:
  analyze     Extract frames and get AI grade recommendation
  grade       Apply a color grade to a clip
  grades      List all available color grades
  compile     Concatenate clips into one output
  audio       Add music with fade in/out
  overlay     Add text overlays
  end-card    Append a black end card with text
  pipeline    Run the full pipeline: grade → compile → audio → end-card
"""

import click
import sys
from pathlib import Path

# Add src to path when running as script
sys.path.insert(0, str(Path(__file__).parent))

from src.grades import list_grades, apply_grade, apply_grade_batch
from src.extract import extract_frames
from src.compile import compile_clips, compile_from_dir, get_clips
from src.audio import add_audio
from src.overlay import add_overlays, add_end_card, TextOverlay


@click.group()
@click.version_option("0.1.0")
def cli():
    """ai-video-dev: AI-first video editing pipeline."""
    pass


@cli.command()
@click.argument("video", type=click.Path(exists=True))
@click.option("--frames-dir", default=None, help="Where to save extracted frames")
@click.option("--auto", is_flag=True, help="Apply the recommended grade without prompting")
@click.option("--output", "-o", default=None, help="Output path for graded clip")
def analyze(video, frames_dir, auto, output):
    """Extract frames and get an AI color grade recommendation."""
    from src.analyze import analyze_clip
    result = analyze_clip(video, frames_dir=frames_dir, auto_apply=auto, output_path=output)
    if result.get("output_path"):
        click.echo(f"\nGraded output: {result['output_path']}")


@cli.command()
@click.argument("video", type=click.Path(exists=True))
@click.option("--grade", "-g", required=True, help="Grade name (partial match ok)")
@click.option("--output", "-o", default=None, help="Output path")
@click.option("--no-prores", is_flag=True, help="Don't encode as ProRes (copy codec)")
@click.option("--dry-run", is_flag=True, help="Print ffmpeg command without running")
def grade(video, grade, output, no_prores, dry_run):
    """Apply a color grade to a video clip."""
    if output is None:
        stem = Path(video).stem
        output = str(Path(video).parent / f"{stem}_graded.mov")
    apply_grade(video, output, grade, prores=not no_prores, dry_run=dry_run)


@cli.command("grades")
def grades_list():
    """List all available color grade presets."""
    grades = list_grades()
    click.echo(f"\n{len(grades)} grades available:\n")
    for name in grades:
        click.echo(f"  • {name}")
    click.echo()


@cli.command()
@click.argument("clips", nargs=-1, type=click.Path(exists=True))
@click.option("--dir", "-d", "clips_dir", default=None, help="Compile all clips from directory")
@click.option("--output", "-o", required=True, help="Output path")
@click.option("--resolution", default="1080:1920", help="WxH resolution (default: 1080:1920 vertical)")
@click.option("--no-prores", is_flag=True)
def compile(clips, clips_dir, output, resolution, no_prores):
    """Concatenate video clips into a single output."""
    if clips_dir:
        compile_from_dir(clips_dir, output, resolution=resolution, prores=not no_prores)
    elif clips:
        compile_clips(list(clips), output, resolution=resolution, prores=not no_prores)
    else:
        raise click.UsageError("Provide clips as arguments or use --dir")


@cli.command()
@click.argument("video", type=click.Path(exists=True))
@click.argument("music", type=click.Path(exists=True))
@click.option("--output", "-o", default=None)
@click.option("--fade-in", default=2.0, type=float)
@click.option("--fade-out", default=3.0, type=float)
@click.option("--offset", default=0.0, type=float, help="Start music at this offset (seconds)")
def audio(video, music, output, fade_in, fade_out, offset):
    """Add music to a video with automatic fade in/out."""
    if output is None:
        stem = Path(video).stem
        output = str(Path(video).parent / f"{stem}_audio.mov")
    add_audio(video, music, output, fade_in=fade_in, fade_out=fade_out, audio_offset=offset)


@cli.command("end-card")
@click.argument("video", type=click.Path(exists=True))
@click.option("--text", default="fin.", help="Text to show on end card")
@click.option("--duration", default=5.0, type=float)
@click.option("--output", "-o", default=None)
def end_card(video, text, duration, output):
    """Append a black end card with text to a video."""
    if output is None:
        stem = Path(video).stem
        output = str(Path(video).parent / f"{stem}_final.mov")
    add_end_card(video, output, text=text, duration=duration)


@cli.command()
@click.argument("clips_dir", type=click.Path(exists=True))
@click.argument("music", type=click.Path(exists=True))
@click.option("--grade", "-g", default=None, help="Grade to apply. If omitted, uses AI analyze.")
@click.option("--output", "-o", default="final.mov")
@click.option("--end-text", default="fin.", help="End card text")
@click.option("--resolution", default="1080:1920")
def pipeline(clips_dir, music, grade, output, end_text, resolution):
    """
    Full pipeline: [grade →] compile → audio → end card.

    If --grade is omitted, runs AI analysis on each clip first.
    """
    import tempfile, os

    clips = get_clips(clips_dir)
    if not clips:
        raise click.UsageError(f"No video clips found in {clips_dir}")

    click.echo(f"\nPipeline: {len(clips)} clips → {output}\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Grade clips
        if grade:
            graded_dir = os.path.join(tmpdir, "graded")
            os.makedirs(graded_dir)
            from src.grades import apply_grade_batch
            graded_clips = apply_grade_batch(clips, graded_dir, grade)
        else:
            click.echo("No grade specified — running AI analysis on each clip...\n")
            from src.analyze import analyze_clip
            graded_clips = []
            graded_dir = os.path.join(tmpdir, "graded")
            os.makedirs(graded_dir)
            for clip in clips:
                stem = Path(clip).stem
                out = os.path.join(graded_dir, f"{stem}_graded.mov")
                analyze_clip(clip, frames_dir=tmpdir, auto_apply=True, output_path=out)
                graded_clips.append(out)

        # Step 2: Compile
        compiled = os.path.join(tmpdir, "compiled.mov")
        compile_clips(graded_clips, compiled, resolution=resolution)

        # Step 3: Audio
        with_audio = os.path.join(tmpdir, "with_audio.mov")
        add_audio(compiled, music, with_audio)

        # Step 4: End card
        add_end_card(with_audio, output, text=end_text)

    click.echo(f"\nDone! Final output: {output}")


if __name__ == "__main__":
    cli()
