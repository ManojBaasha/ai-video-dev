# AI Grading Guidelines

These are the lessons baked into the `analyze` command's system prompt. They come from real production testing, not documentation.

If you discover a new grading gotcha, add it here and to the system prompt in `src/analyze.py`.

---

## Lessons learned

### 1. Never use `colortemperature` on warm/golden hour footage

`colortemperature` filter on footage that's already warm (golden hour, tungsten lighting) creates a **pink/magenta cast**. Avoid it.

Instead, cool the image by pulling down the red channel in `curves`:
```
r='0/0 0.12/0.04 0.5/0.42 0.85/0.82 1/0.9'
```
Capping the red curve endpoint at 0.9 in highlights cools the image without introducing pink.

The Blue Sky grade demonstrates this correctly.

---

### 2. Steel Blue BW technique: saturation first, then color

For black-and-white with a blue tint:
1. Set `eq=saturation=0.0` FIRST to go to pure grayscale
2. THEN add `colorbalance` with blue pushed in mids/highlights

If you push blue before desaturating, you get color cast artifacts from the residual color channels.

---

### 3. Preserving true blacks when pushing blue

When boosting the blue channel in dark scenes, shadows can lift and look grey/milky.

Fix: use curve control points that clamp shadows to 0 until a threshold:
```
r='0/0 0.12/0.0 0.2/0.08 ...'
```
This forces shadows to stay black until 0.12 input brightness, then gradually opens up.

---

### 4. Pink foam / blown highlight fix

When highlights contain white foam, snow, or bright surfaces, boosting contrast + blue can push those highlights pink.

Fix: cap red in highlights with two controls:
- `colorbalance rh=-0.06` (red highlights down)
- Curve endpoint: `r='... 1/0.94'` (red ceiling below 1.0)

---

### 5. Per-clip grading always beats blanket filters

A single grade applied to all clips in a sequence will look wrong on at least some of them. Day vs. night, indoor vs. outdoor, overcast vs. sunny — these all need different treatment.

The `analyze` command runs per-clip by design. The `pipeline` command with AI will grade each clip individually.

---

### 6. Adjusting grades for specific conditions

Most grades have notes on adjusting parameters. Common tweaks:
- Reduce saturation by 0.1-0.15 for drier/less reflective surfaces
- Increase brightness `eq=brightness` by 0.03-0.05 for underexposed clips
- Reduce contrast for very flat/log footage to avoid clipping

---

## Grade selection heuristics

| Footage type | Recommended grade |
|---|---|
| Night city, wet streets, neon signs | Neon Rain - Night City |
| Night city, dramatic/cinematic BW | Steel Blue - Night City BW |
| Daytime outdoor, golden hour | Blue Sky - Daytime Scenic |
| Underwater, pools, aquariums | Deep Ocean Blue - Aquarium |
| Ocean, seascapes | Deep Teal - Ocean Water |
| Sunset (cooled) | Cool Dramatic - Sunset Ocean |
| Concert, DJ, colored stage lighting | Purple Punch - DJ Party |
| Carnival, fair, festive night | Neon Carnival - Night Fair |
