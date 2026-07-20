# ai-video-dev

> AI-first video editing pipeline powered by ffmpeg + Claude. Extract frames, get AI color grade recommendations, compile, mix audio — all from the CLI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ffmpeg](https://img.shields.io/badge/ffmpeg-required-green.svg)](https://ffmpeg.org/)

---

## The idea

Most video editing tools make you figure everything out yourself — color grades, ffmpeg filter chains, compile settings. This project packages a battle-tested workflow where Claude looks at your footage frames and recommends the right grade, applies it, compiles your clips, and mixes your audio. All from one CLI.

Built from real production use. The color grade presets and workflow patterns in this repo come from dozens of rounds of iterative testing on real footage.

---

## Install

```bash
git clone https://github.com/manojelango/ai-video-dev
cd ai-video-dev
pip install -e .
```

**Requirements:**
- Python 3.10+
- ffmpeg (with drawtext support — see [docs/setup.md](docs/setup.md))
- Anthropic API key (for `analyze` command only)

```bash
# macOS — ffmpeg with drawtext support
brew uninstall ffmpeg
brew tap homebrew-ffmpeg/ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg
```

---

## Quick start

```bash
# Analyze a clip — Claude picks the best grade and explains why
aivid analyze clip.MOV

# Apply a specific grade
aivid grade clip.MOV --grade "Neon Rain - Night City"

# Compile multiple graded clips into one output
aivid compile clips/ --output final.mov

# Add music with auto fade in/out
aivid audio final.mov song.mp3 --output final_with_audio.mov

# Full pipeline in one command
aivid pipeline clips/ song.mp3 --output final.mov
```

---

## Color grade library

8 battle-tested grades included. Each is a plain `.txt` file with the ffmpeg filter chain and notes on what it does and when to use it.

| Grade | Best for |
|-------|----------|
| Neon Rain - Night City | Wet streets, neon reflections, urban night |
| Steel Blue - Night City BW | BW + blue tint, dramatic night scenes |
| Blue Sky - Daytime Scenic | Outdoor day, golden hour, coastal |
| Deep Ocean Blue - Aquarium | Underwater, pools, aquarium footage |
| Deep Teal - Ocean Water | Ocean water, seascapes |
| Cool Dramatic - Sunset Ocean | Sunset with cool correction |
| Purple Punch - DJ Party | Concert, party, colored lighting |
| Neon Carnival - Night Fair | Fair/carnival, festive night scenes |

[→ Browse all grades](grades/)

**Add your own:** copy any `.txt` file in `grades/`, rename it, swap the filter chain. The `analyze` command will automatically pick it up.

---

## How the analyze command works

```
aivid analyze clip.MOV
```

1. Extracts 3 frames (start, middle, end) as PNGs
2. Sends frames to Claude with your grade library
3. Claude recommends the best grade with reasoning
4. You confirm (or override)
5. Grade applied, output saved

The AI's decision-making is guided by lessons learned from real footage — things like why you should never use `colortemperature` on golden hour footage, or how to do Steel Blue without color casts. See [docs/ai-guidelines.md](docs/ai-guidelines.md).

---

## Contributing

Grades are the easiest way to contribute — see [CONTRIBUTING.md](CONTRIBUTING.md).

For code contributions, open an issue first to discuss.

---

## License

MIT
