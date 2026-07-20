# Setup Guide

## 1. Install ffmpeg with drawtext support

The default Homebrew ffmpeg does not include freetype/drawtext. For text overlays and subtitles, you need the extended build:

```bash
brew uninstall ffmpeg
brew tap homebrew-ffmpeg/ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg
```

Verify drawtext is available:
```bash
ffmpeg -filters | grep drawtext
```

If you don't need text overlays, the standard `brew install ffmpeg` works for everything else.

---

## 2. Install ai-video-dev

```bash
git clone https://github.com/manojelango/ai-video-dev
cd ai-video-dev
pip install -e .
```

For AI features (the `analyze` command):
```bash
pip install -e ".[ai]"
```

---

## 3. Set up your API key (for analyze command)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Add to your `~/.zshrc` or `~/.bash_profile` to persist it.

Get a key at [console.anthropic.com](https://console.anthropic.com/).

---

## 4. Verify the install

```bash
aivid --version
aivid grades
```

---

## Footage requirements

The pipeline is optimized for:
- **Vertical ProRes** (1080x1920 or 4K vertical)
- iPhone MOV files work directly
- Other formats (MP4, HEIC video) also supported

For best quality, convert to ProRes before grading:
```bash
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 1 -c:a copy output.mov
```

---

## Finding ProRes files on macOS

```bash
mdfind "kMDItemCodecs == '*ProRes*'"
```

Check if a file is vertical:
```bash
mdls -name kMDItemPixelWidth -name kMDItemPixelHeight file.MOV
```
