"""ai-video-dev — AI-first video editing pipeline."""

from .extract import extract_frames, extract_frames_batch
from .grades import list_grades, load_grade, apply_grade, apply_grade_batch
from .compile import compile_clips, compile_from_dir
from .audio import add_audio
from .overlay import add_overlays, add_end_card, TextOverlay

__all__ = [
    "extract_frames",
    "extract_frames_batch",
    "list_grades",
    "load_grade",
    "apply_grade",
    "apply_grade_batch",
    "compile_clips",
    "compile_from_dir",
    "add_audio",
    "add_overlays",
    "add_end_card",
    "TextOverlay",
]
