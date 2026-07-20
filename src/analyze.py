"""
analyze.py — AI-powered color grade analysis using Claude.

Extracts preview frames from a clip, sends them to Claude along with
the full grade library, and gets a recommendation with reasoning.
"""

import os
import base64
from pathlib import Path
from typing import Optional

from .extract import extract_frames
from .grades import list_grades, load_grade, apply_grade

# System prompt encoding the lessons learned from real footage testing
SYSTEM_PROMPT = """You are an expert colorist assisting with ffmpeg-based video color grading.

You will be given preview frames (start, middle, end) from a video clip and a library of color grade presets.
Your job is to recommend the single best grade for the clip and explain your reasoning concisely.

CRITICAL LESSONS FROM PRODUCTION USE:
1. Never recommend colortemperature filter on golden hour or warm-toned footage — it creates pink/magenta casts.
   Instead, cap the red channel in curves. The Blue Sky grade handles this correctly.
2. For BW + blue tint (Steel Blue technique): saturation=0.0 FIRST, then colorbalance blue on top.
   This avoids all color cast problems.
3. To preserve true blacks when pushing blue: use curve control points that clamp shadows to 0.
4. Pink foam / white highlights: cap red in highlights with rh and curve endpoint.
5. Per-clip grading is always better than blanket filters — day vs night need different treatment.
6. Warm source footage + cool grade = use curves to pull red channel, not colortemperature.

Your response format:
GRADE: <exact grade name>
CONFIDENCE: <high|medium|low>
REASONING: <2-3 sentences explaining why this grade fits this footage>
NOTES: <any per-clip tweaks to consider, e.g. "reduce saturation from 1.35 to 1.2 for drier surfaces">
"""


def encode_image(image_path: str) -> str:
    """Base64 encode an image for the Claude API."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def analyze_clip(
    video_path: str,
    frames_dir: Optional[str] = None,
    auto_apply: bool = False,
    output_path: Optional[str] = None,
) -> dict:
    """
    Analyze a video clip and get an AI color grade recommendation.

    Args:
        video_path: Path to the video clip.
        frames_dir: Where to save extracted frames. Defaults to temp dir.
        auto_apply: If True, apply the recommended grade without prompting.
        output_path: Where to save graded output. Defaults to <stem>_graded.mov.

    Returns:
        Dict with keys: grade, confidence, reasoning, notes, frame_paths
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package required for analyze command.\n"
            "Install with: pip install anthropic"
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Get your key at https://console.anthropic.com/"
        )

    print(f"Extracting frames from: {Path(video_path).name}")
    frame_paths = extract_frames(video_path, frames_dir)

    # Build grade library context
    grade_names = list_grades()
    grade_summaries = []
    for name in grade_names:
        try:
            grade = load_grade(name)
            # Include first "Best for:" line from the raw text
            best_for = ""
            for line in grade["raw"].splitlines():
                if "best for" in line.lower():
                    best_for = line.strip()
                    break
            grade_summaries.append(f"- {name}: {best_for}")
        except Exception:
            grade_summaries.append(f"- {name}")

    grade_library_text = "Available color grades:\n" + "\n".join(grade_summaries)

    # Build message with frames
    content = []
    frame_labels = ["start (1s in)", "middle", "near-end"]
    for i, frame_path in enumerate(frame_paths):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": encode_image(frame_path),
            }
        })
        content.append({
            "type": "text",
            "text": f"Frame {i+1}: {frame_labels[i]}"
        })

    content.append({
        "type": "text",
        "text": f"\n{grade_library_text}\n\nPlease analyze these frames and recommend the best color grade."
    })

    print("Sending frames to Claude for analysis...")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )

    response_text = response.content[0].text
    print("\n--- AI Recommendation ---")
    print(response_text)
    print("-------------------------\n")

    # Parse response
    result = {
        "raw_response": response_text,
        "frame_paths": frame_paths,
        "grade": None,
        "confidence": None,
        "reasoning": None,
        "notes": None,
    }

    for line in response_text.splitlines():
        if line.startswith("GRADE:"):
            result["grade"] = line.split(":", 1)[1].strip()
        elif line.startswith("CONFIDENCE:"):
            result["confidence"] = line.split(":", 1)[1].strip()
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.split(":", 1)[1].strip()
        elif line.startswith("NOTES:"):
            result["notes"] = line.split(":", 1)[1].strip()

    # Apply grade if requested or prompt user
    if result["grade"]:
        if auto_apply:
            apply_it = True
        else:
            apply_it = input(f"Apply '{result['grade']}'? [Y/n] ").strip().lower() in ("", "y", "yes")

        if apply_it:
            if output_path is None:
                stem = Path(video_path).stem
                output_path = str(Path(video_path).parent / f"{stem}_graded.mov")
            apply_grade(video_path, output_path, result["grade"])
            result["output_path"] = output_path

    return result
