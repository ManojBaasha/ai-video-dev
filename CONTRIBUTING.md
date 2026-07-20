# Contributing to ai-video-dev

Thanks for contributing. The easiest way to contribute is to add a new color grade.

## Adding a color grade

1. Create a `.txt` file in the `grades/` directory.
2. Name it descriptively: `Mood - Scene Type.txt` (e.g. `Warm Film - Golden Hour.txt`)
3. Follow this format:

```
<Grade Name>
==============
Best for: <describe the type of footage this works best on>

FFmpeg filter chain:
<the full ffmpeg -vf filter string>

Usage example:
ffmpeg -i input.MOV -vf "<filter chain>" -c:v prores_ks -profile:v 1 -c:a copy output.MOV

What it does:
- <explain each filter and what it achieves>

Notes:
- <any caveats, tweaks, or conditions where this works best or worst>
```

4. Open a PR. Include a before/after screenshot if possible.

The `analyze` command will automatically pick up your new grade.

## Code contributions

- Open an issue before starting significant work
- Keep PRs focused — one thing per PR
- Follow the existing code style (ruff for linting)
- Add tests in `tests/` for new functionality

## Key design principles

- **ffmpeg-first**: all video processing goes through ffmpeg. No other video libraries.
- **grades as text**: presets stay as plain `.txt` files — easy to read, diff, and contribute.
- **AI is optional**: the core pipeline should work without an API key. AI is an enhancement.
- **lessons learned**: if you discover a grading gotcha (like the colortemperature issue), document it in the grade file and in `docs/ai-guidelines.md`.

## Reporting bugs

Open an issue with:
- Your ffmpeg version (`ffmpeg -version`)
- The command you ran
- The error output
- Sample footage description (resolution, format, lighting conditions)
