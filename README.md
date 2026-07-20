# ai-video-dev

> A Claude Code context pack for ffmpeg-based video editing. Color grading, compilation, audio mixing, overlays — all pre-solved so you can just describe what you want.

---

## How to use this

1. Clone the repo into your project (or open it directly in Claude Code)
2. Tell Claude what you want: *"grade all clips in this folder with the neon rain look and compile them"*
3. Claude writes a script using the building blocks here and runs it

You never write the same ffmpeg command twice. The hard parts — filter chains, audio fades, ProRes encoding, concat lists — are already figured out.

---

## What's included

**8 battle-tested color grades** in `grades/` — each a plain `.txt` file with the ffmpeg
filter chain and notes on what footage it works best on:

| Grade | Best for |
|---|---|
| Neon Rain - Night City | Wet streets, neon reflections, urban night |
| Steel Blue - Night City BW | BW + blue tint, dramatic night scenes |
| Blue Sky - Daytime Scenic | Outdoor day, golden hour, coastal |
| Deep Ocean Blue - Aquarium | Underwater, pools, aquarium footage |
| Deep Teal - Ocean Water | Ocean water, seascapes |
| Cool Dramatic - Sunset Ocean | Sunset with cool correction |
| Purple Punch - DJ Party | Concert, party, colored lighting |
| Neon Carnival - Night Fair | Fair/carnival, festive night scenes |

**Python building blocks** in `src/`:
- `grades.py` — load and apply color grades
- `analyze.py` — AI-powered grade recommendations (sends frames to Claude)
- `extract.py` — pull preview frames from a clip
- `compile.py` — concatenate clips into one output
- `audio.py` — add music with auto fade in/out
- `overlay.py` — text overlays and end cards

**Example scripts** in `examples/` — real patterns to reference or run directly.

**AI guidelines** in `docs/ai-guidelines.md` — lessons learned from real footage testing
(things like why you should never use `colortemperature` on golden hour footage).

---

## Setup

```bash
# ffmpeg with drawtext support (macOS)
brew uninstall ffmpeg
brew tap homebrew-ffmpeg/ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg

# Python deps
pip install anthropic   # only needed for AI grade analysis
```

Set your API key if you want AI analysis:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Example scripts

See `examples/` for ready-to-run scripts. Common patterns:

```python
# Grade all clips in a folder
from src.grades import apply_grade_batch, list_grades
apply_grade_batch(clips, "graded/", "neon rain")

# AI picks the best grade per clip
from src.analyze import analyze_clip
analyze_clip("clip.MOV", auto_apply=True, output_path="clip_graded.mov")

# Compile + add music
from src.compile import compile_from_dir
from src.audio import add_audio
compile_from_dir("graded/", "compiled.mov")
add_audio("compiled.mov", "song.mp3", "final.mov")
```

---

## Adding your own grades

Copy any `.txt` file in `grades/`, rename it, swap the filter chain. The AI analysis
picks it up automatically. Format:

```
Grade Name
==========
Best for: <describe the footage>

FFmpeg filter chain:
<the full -vf filter string>

What it does:
- <explain each filter>

Notes:
- <caveats and tweaks>
```

---

## Contributing

When you're editing with this repo and Claude figures out something new — a grade, a gotcha,
a useful pattern — have Claude open a PR and share it. The guide is written for Claude Code
agents, not humans: see [CONTRIBUTING.md](CONTRIBUTING.md).

The more people use this, the better it gets for everyone.

---

## License

MIT
