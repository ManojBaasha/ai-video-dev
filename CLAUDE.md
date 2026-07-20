# ai-video-dev — Claude Code Skill

This repo is a context pack for Claude Code. When someone describes a video editing task,
use the building blocks here to write a custom script for it. Don't figure out ffmpeg from
scratch — it's already solved.

---

## What's here

| Path | What it is |
|---|---|
| `src/grades.py` | Load and apply color grade presets |
| `src/analyze.py` | Send frames to Claude, get grade recommendation |
| `src/extract.py` | Pull preview frames from a clip (start/mid/end) |
| `src/compile.py` | Concatenate clips into one output |
| `src/audio.py` | Add music with auto fade in/out |
| `src/overlay.py` | Text overlays and end cards |
| `grades/*.txt` | 8 color grade presets (ffmpeg filter chains + notes) |
| `docs/ai-guidelines.md` | Hard-won grading lessons from real footage |
| `examples/` | Reference scripts showing common patterns |

---

## Key functions

```python
from src.grades import list_grades, load_grade, apply_grade, apply_grade_batch
from src.analyze import analyze_clip
from src.extract import extract_frames
from src.compile import compile_clips, compile_from_dir, get_clips
from src.audio import add_audio
from src.overlay import add_overlays, add_end_card, TextOverlay
```

### Grading
```python
# List all available grades
names = list_grades()

# Apply a grade (partial name match, case-insensitive)
apply_grade("clip.MOV", "clip_graded.mov", "neon rain")

# Apply same grade to many clips
apply_grade_batch(["a.MOV", "b.MOV"], "output_dir/", "steel blue")
```

### AI analysis
```python
# Extract frames + ask Claude which grade fits best
result = analyze_clip("clip.MOV", auto_apply=True, output_path="clip_graded.mov")
# result keys: grade, confidence, reasoning, notes, output_path
```

### Compile
```python
# From a list
compile_clips(["a.mov", "b.mov", "c.mov"], "final.mov", resolution="1080:1920")

# From a directory (sorted by filename)
compile_from_dir("graded/", "final.mov")
```

### Audio
```python
add_audio("final.mov", "song.mp3", "final_with_audio.mov", fade_in=2.0, fade_out=3.0)
```

### Overlays / end card
```python
add_end_card("final.mov", "output.mov", text="fin.", duration=5.0)

overlays = [TextOverlay(text="Paris", start=2.0, end=6.0)]
add_overlays("clip.mov", "output.mov", overlays)
```

---

## Color grades available

| Grade name | Best for |
|---|---|
| `Neon Rain - Night City` | Wet streets, neon reflections, urban night |
| `Steel Blue - Night City BW` | BW + blue tint, dramatic night scenes |
| `Blue Sky - Daytime Scenic` | Outdoor day, golden hour, coastal |
| `Deep Ocean Blue - Aquarium` | Underwater, pools, aquarium footage |
| `Deep Teal - Ocean Water` | Ocean water, seascapes |
| `Cool Dramatic - Sunset Ocean` | Sunset with cool correction |
| `Purple Punch - DJ Party` | Concert, party, colored lighting |
| `Neon Carnival - Night Fair` | Fair/carnival, festive night scenes |

Grade files are in `grades/*.txt` — each has the ffmpeg filter chain, a description, and
notes on when to use it. The AI analysis command reads them automatically.

---

## Critical grading rules (from real footage testing)

1. **Never use `colortemperature` on golden hour / warm footage** — creates pink/magenta cast.
   Cool warm footage by pulling down the red channel in `curves` instead.

2. **Steel Blue BW technique**: `eq=saturation=0.0` FIRST, then `colorbalance` blue on top.
   Pushing blue before desaturating creates color cast artifacts.

3. **Preserve true blacks when pushing blue**: use curve control points that clamp shadows to 0.

4. **Pink foam / blown highlights**: cap red in highlights with `colorbalance rh=-0.06` and
   a red curve ceiling below 1.0.

5. **Per-clip grading always beats blanket filters** — day vs night, indoor vs outdoor.

See `docs/ai-guidelines.md` for the full reference.

---

## How to write scripts for user requests

The user will describe what they want. Write a Python script that imports from `src/` and
does exactly that. See `examples/` for common patterns.

**Common workflow:**
1. Grade clips (AI analyze or specific grade)
2. Compile graded clips into one file
3. Add music
4. Add end card

**Requirements:**
- `pip install anthropic` (only needed for `analyze_clip`)
- `ffmpeg` with drawtext support (`brew install homebrew-ffmpeg/ffmpeg/ffmpeg` on macOS)
- `ANTHROPIC_API_KEY` env var (only needed for `analyze_clip`)

All video processing is ffmpeg under the hood. No other video libraries.

---

## Contributing findings back

When you solve something new — a grade that works well on footage not covered yet, a gotcha
you hit and fixed, a useful ffmpeg pattern — contribute it back so every future user gets it
for free. See `CONTRIBUTING.md` for exactly how to do this.
