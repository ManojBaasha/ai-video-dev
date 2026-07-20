# Contributing — for Claude Code agents

This guide is written for Claude Code instances, not humans. When you're editing video with
this repo and you discover something new — a grade that works, a pattern, a gotcha — open
a PR so future users get it automatically.

**The rule:** if you had to figure something out that wasn't already in this repo, it belongs here.

---

## What's worth contributing

### 1. A new color grade
You built a filter chain that works well on a specific type of footage not already covered.

### 2. A grading gotcha
You hit a problem with ffmpeg filters on real footage and found the fix. Things like the
`colortemperature` issue documented in `docs/ai-guidelines.md` — add it there.

### 3. A useful script pattern
You wrote a script for an unusual request (trim + grade + overlay + compile in one pass,
batch re-grade with a different grade, extract frames for review, etc.) that others will
likely need. Add it to `examples/`.

---

## How to open a PR

```bash
# 1. Fork + clone (gh CLI)
gh repo fork ManojBaasha/ai-video-dev --clone
cd ai-video-dev

# 2. Create a branch
git checkout -b add/<short-description>

# 3. Make your changes (see format guides below)

# 4. Commit
git add .
git commit -m "add: <what you're adding and why>"

# 5. Push and open PR
git push -u origin HEAD
gh pr create --title "<what you added>" --body "$(cat <<'EOF'
## What this adds
<1-2 sentences>

## Footage tested on
<describe the footage: iPhone MOV, night/day, indoor/outdoor, format, etc.>

## Before / after (optional)
<describe the visual difference if it's a grade>
EOF
)"
```

---

## Adding a new color grade

Create `grades/<Mood> - <Scene Type>.txt` using this exact format:

```
<Grade Name>
============
Best for: <describe the footage this works on>

FFmpeg filter chain:
<the complete -vf filter string on one line>

Usage example:
ffmpeg -i input.MOV -vf "<filter chain>" -c:v prores_ks -profile:v 1 -c:a copy output.MOV

What it does:
- <explain each filter and what it achieves visually>

Notes:
- <caveats: what footage it works best/worst on, which parameters to tweak>
```

**Rules:**
- Filter chain must be on a single line (the parser reads the line after `FFmpeg filter chain:`)
- Name format: `Mood - Scene Type` (e.g. `Warm Film - Golden Hour`, `Teal Orange - Sunrise Beach`)
- Only submit grades you've tested on real footage, not synthetic

The `analyze_clip` function picks up new grades automatically — no code changes needed.

---

## Adding a grading gotcha

Open `docs/ai-guidelines.md` and add a new numbered section:

```markdown
### N. <Short title of the problem>

<What goes wrong and why.>

Fix:
<The correct approach, with the ffmpeg filter or curve values if relevant.>
```

Then add the same rule (condensed to 1-2 lines) to the `CRITICAL LESSONS FROM PRODUCTION USE`
block in `src/analyze.py` — that's what gets sent to Claude in the system prompt.

---

## Adding an example script

Add a `.py` file to `examples/`. It should:
- Have a docstring at the top explaining what it does and when you'd use it
- Have a `# --- CONFIG ---` block with the variables a user would change
- Import only from `src/` (no new dependencies)
- Actually run end-to-end (test it before submitting)

---

## What not to submit

- Grades you haven't tested on real footage
- Scripts that require dependencies not already in `requirements.txt`
- Tweaks to existing grades without footage evidence
- Anything that changes the core `src/` module APIs (open an issue to discuss first)
