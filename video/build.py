#!/usr/bin/env python3
"""Renders the intro video: slide frames (headless Chrome) + narration (macOS `say`)
-> out/tokensaver-intro.mp4 (ffmpeg). Needs macOS, Google Chrome and ffmpeg.

    python3 video/build.py

Edit SCENES to change the words or timing, or slides.html to change the visuals.
The mp4 is not committed; upload it to YouTube from video/out/.
"""
import pathlib
import shutil
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
OUT, FRAMES, AUDIO = ROOT / "out", ROOT / "out" / "frames", ROOT / "out" / "audio"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VOICE, RATE = "Samantha", 170
FADE = 0.4      # cross-fade between frames, seconds
LEAD = 0.4      # narration starts this long after the scene appears
TAIL = 1.0      # silence after the narration before the next scene
FPS = 30

# say = what is spoken (letters spaced so the voice spells acronyms);
# caption = what is shown; weights = share of the scene each build-up step stays on screen.
SCENES = [
    dict(steps=2, weights=[0.45, 0.55], min=5,
         say="tokensaver. Fewer tokens, every page.",
         caption="tokensaver — fewer tokens, every page."),
    dict(steps=2, weights=[0.5, 0.5], min=8,
         say="When your coding agent reads a web page, a P D F, or an A P I response, the whole raw thing lands in its context. One Wikipedia article: one hundred eighty-three thousand tokens.",
         caption="When your coding agent reads a web page, a PDF or an API response, the whole raw thing lands in its context."),
    dict(steps=3, weights=[0.2, 0.35, 0.45], min=8,
         say="tokensaver is a local M C P server that turns pages, P D Fs, Office files and Jason into compact text. The same article comes back at nineteen thousand tokens. Or as a two hundred fifty token outline, so your agent reads only the section it needs.",
         caption="A local MCP server that turns pages, PDFs, Office files and JSON into compact text."),
    dict(steps=3, weights=[0.3, 0.35, 0.35], min=8,
         say="These are measured numbers, on real sources. A Wikipedia article, eighty-nine percent smaller, or ninety-nine point nine as an outline. A repository page, ninety-eight. A GitHub A P I response, ninety-nine and a half. And a log file, ninety-seven and a half.",
         caption="Reproducible: go test ./e2e/ -v"),
    dict(steps=2, weights=[0.5, 0.5], min=8,
         say="It runs on your machine, as one Go binary. No A P I keys. It never calls an L L M. And nothing leaves your computer, except the U R Ls you ask for.",
         caption="One Go binary. No API keys. Nothing leaves your machine except the URLs you ask for."),
    dict(steps=3, weights=[0.4, 0.3, 0.3], min=8,
         say="Install it with Homebrew or Docker, add it to Claude Code with one command, and then just ask your agent to read something with tokensaver.",
         caption="Install, connect, ask."),
    dict(steps=1, weights=[1.0], min=5,
         say="tokensaver is open source. Find it on GitHub.",
         caption="Open source · MIT · github.com/use-tokensaver/tokensaver"),
]


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout)


def main():
    for tool in ("ffmpeg", "ffprobe", "say"):
        if not shutil.which(tool):
            sys.exit(f"missing {tool}")
    if not pathlib.Path(CHROME).exists():
        sys.exit(f"missing {CHROME}")
    shutil.rmtree(OUT, ignore_errors=True)
    FRAMES.mkdir(parents=True)
    AUDIO.mkdir(parents=True)

    clips = []  # (png, seconds)
    scene_audio = []  # (wav, scene seconds)
    for n, sc in enumerate(SCENES, 1):
        aiff, wav = AUDIO / f"s{n}.aiff", AUDIO / f"s{n}.wav"
        run(["say", "-v", VOICE, "-r", str(RATE), "-o", str(aiff), sc["say"]])
        run(["ffmpeg", "-y", "-i", str(aiff), "-ar", "44100", "-ac", "2", str(wav)])
        total = max(sc["min"], LEAD + duration(wav) + TAIL)
        scene_audio.append((wav, total))
        for step in range(1, sc["steps"] + 1):
            png = FRAMES / f"s{n}_{step}.png"
            url = (ROOT / "slides.html").as_uri() + f"?scene={n}&step={step}&caption=" + urllib.parse.quote(sc["caption"])
            run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                 "--window-size=1920,1080", "--virtual-time-budget=10000", f"--screenshot={png}", url])
            clips.append((png, total * sc["weights"][step - 1]))
        print(f"scene {n}: {total:.1f}s")

    # Frames cross-fade into each other. Every clip but the last is FADE longer, so the
    # fades overlap the extra tail and the finished video is exactly sum(seconds) long.
    cmd = ["ffmpeg", "-y"]
    for i, (png, secs) in enumerate(clips):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{secs + (FADE if i < len(clips) - 1 else 0):.3f}", "-i", str(png)]
    for wav, _ in scene_audio:
        cmd += ["-i", str(wav)]
    graph, last, cum = [], "0:v", 0.0
    for i in range(1, len(clips)):
        cum += clips[i - 1][1]
        graph.append(f"[{last}][{i}:v]xfade=transition=fade:duration={FADE}:offset={cum:.3f}[v{i}]")
        last = f"v{i}"
    parts = []
    for i, (_, total) in enumerate(scene_audio):
        parts.append(f"[{len(clips) + i}:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad=whole_dur={total:.3f}[a{i}]")
    graph += parts
    graph.append("".join(f"[a{i}]" for i in range(len(scene_audio))) + f"concat=n={len(scene_audio)}:v=0:a=1[aout]")
    cmd += ["-filter_complex", ";".join(graph), "-map", f"[{last}]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT / "tokensaver-intro.mp4")]
    run(cmd)
    print(f"done: {OUT / 'tokensaver-intro.mp4'} ({duration(OUT / 'tokensaver-intro.mp4'):.1f}s)")


if __name__ == "__main__":
    main()
