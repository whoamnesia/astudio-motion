#!/usr/bin/env python3
"""astudio-motion Blender runner - find Blender, run bpy scripts headless, render, contact-sheet.

Usage:
  blender_run.py info
      Locate Blender (env BLENDER, PATH, standard install folders) and report version, engines, GPU devices.
  blender_run.py run <script.py> [--blend in.blend] [--timeout 1800] [-- script args...]
      Run a bpy script in background mode (blender -b --factory-startup --python-exit-code 1). Lines the script
      prints as  @@JSON@@{...}  are collected and printed as the result; everything else is summarised.
  blender_run.py render <file.blend> [--frames 1-120 | --frame 60] [--engine EEVEE|CYCLES|WORKBENCH]
                        [--out renders/frame_####] [--format PNG] [--samples 64] [--res 1920x1080] [--percent 100]
      Render frames from a .blend (EEVEE/Workbench for previews, Cycles for finals).
  blender_run.py sheet <frames_dir> [--out sheet.png] [--cols 4] [--every N]
      Contact sheet from rendered frames (needs Pillow) - open it and judge before delivering.
  blender_run.py encode <frames_dir> --fps 30 --out film.mp4   (ffmpeg)

Blender 5.2 LTS is the target (works with 4.2+; 5.x API changes: see skills/blender/references/bpy-5x.md).
If Blender is not installed: say so, deliver the .py scene script for the user to run, and offer the install
(blender.org/download, or the Blender MCP server for a live session). Python 3.8+, stdlib (+ Pillow for sheet).
"""
import glob, json, os, platform, re, shutil, subprocess, sys, tempfile
from pathlib import Path

CANDIDATES = [
    "/Applications/Blender.app/Contents/MacOS/Blender",
    os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender"),
    "/usr/bin/blender", "/usr/local/bin/blender", "/snap/bin/blender", "/opt/blender/blender",
    *glob.glob("/opt/blender*/blender"), *glob.glob(os.path.expanduser("~/blender*/blender")),
    *glob.glob(r"C:\Program Files\Blender Foundation\Blender*\blender.exe"),
]


def find_blender():
    env = os.environ.get("BLENDER")
    if env and Path(env).exists():
        return env
    w = shutil.which("blender")
    if w:
        return w
    for c in CANDIDATES:
        if c and Path(c).exists():
            return c
    return None


def need():
    b = find_blender()
    if not b:
        print("Blender not found. Install Blender 5.2 LTS from https://www.blender.org/download/ "
              "(or set BLENDER=/path/to/blender). For a live session use the Blender MCP server "
              "(github.com/ahujasid/blender-mcp). Meanwhile deliver the bpy script for the user to run.")
        sys.exit(2)
    return b


INFO_PY = r'''
import bpy, json, sys
prefs = bpy.context.preferences
devs = []
try:
    cp = prefs.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            cp.compute_device_type = t; cp.get_devices()
            devs += [f"{t}:{d.name}" for d in cp.devices if d.type != "CPU"]
        except Exception: pass
except Exception: pass
enum = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
print("@@JSON@@" + json.dumps({"version": bpy.app.version_string, "engines": [e.identifier for e in enum] or ["BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH"],
      "gpu": devs, "python": sys.version.split()[0]}))
'''


def run_blender(args, timeout=1800):
    b = need()
    cmd = [b, "-b", "--factory-startup", "--python-exit-code", "1"] + args
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = p.stdout + p.stderr
    js = [json.loads(l.split("@@JSON@@", 1)[1]) for l in out.splitlines() if "@@JSON@@" in l]
    errs = [l for l in out.splitlines() if re.search(r"Error|Traceback|Exception", l)][:15]
    return p.returncode, js, errs, out


def cmd_info(a):
    b = find_blender()
    if not b:
        need()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(INFO_PY)
    rc, js, errs, out = run_blender(["-P", f.name], 300)
    print(json.dumps({"binary": b, **(js[0] if js else {"error": errs or out[-500:]})}, indent=2))


def cmd_run(a, extra):
    args = ([a["blend"]] if a.get("blend") else []) + ["-P", a["script"], "--"] + extra
    rc, js, errs, out = run_blender(args, int(a.get("timeout", 1800)))
    for j in js:
        print(json.dumps(j, ensure_ascii=False))
    if rc != 0 or errs:
        print("exit", rc)
        print("\n".join(errs) or out[-1500:])
    sys.exit(rc)


def cmd_render(a):
    blend = a["file"]; out = a.get("out", "renders/frame_####"); Path(out).parent.mkdir(parents=True, exist_ok=True)
    eng = a.get("engine", "EEVEE").upper()
    eng = {"EEVEE": "BLENDER_EEVEE", "CYCLES": "CYCLES", "WORKBENCH": "BLENDER_WORKBENCH"}.get(eng, eng)
    setup = ["import bpy", "s=bpy.context.scene", f"s.render.engine='{eng}'"]
    if a.get("res"):
        w, h = a["res"].lower().split("x"); setup += [f"s.render.resolution_x={int(w)}", f"s.render.resolution_y={int(h)}"]
    setup.append(f"s.render.resolution_percentage={int(a.get('percent', 100))}")
    if a.get("samples"):
        setup.append(f"exec(\"try:\\n s.cycles.samples={int(a['samples'])}\\nexcept Exception: pass\\ntry:\\n s.eevee.taa_render_samples={int(a['samples'])}\\nexcept Exception: pass\")")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("\n".join(setup) + "\n")
    args = [blend, "-P", f.name, "-o", str(Path(out).resolve()), "-F", a.get("format", "PNG")]
    if a.get("frame"):
        args += ["-f", str(a["frame"])]
    else:
        fr = a.get("frames", "")
        if fr:
            s, e = fr.split("-"); args += ["-s", s, "-e", e]
        args += ["-a"]
    rc, js, errs, outp = run_blender(args, int(a.get("timeout", 7200)))
    n = len(re.findall(r"Saved: ", outp))
    print(f"render exit {rc}: {n} frame(s) saved to {Path(out).parent}/")
    if rc != 0:
        print("\n".join(errs) or outp[-1500:])
    print("Next: blender_run.py sheet", Path(out).parent, "- open the sheet and judge silhouette, light, motion arcs.")
    sys.exit(rc)


def cmd_sheet(a):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Pillow missing: pip install pillow (or use: ffmpeg -i frame_%04d.png -vf 'scale=480:-1,tile=4x3' sheet.png)"); sys.exit(2)
    fs = sorted(glob.glob(os.path.join(a["dir"], "*.png")) + glob.glob(os.path.join(a["dir"], "*.jpg")))
    every = int(a.get("every", 0)) or max(1, len(fs) // 12)
    fs = fs[::every][:24]
    if not fs:
        print("no frames in", a["dir"]); sys.exit(1)
    cols = int(a.get("cols", 4)); ims = [Image.open(f).convert("RGB") for f in fs]
    w = 480; h = int(ims[0].height * w / ims[0].width); rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 28) + 8), (22, 24, 29)); d = ImageDraw.Draw(sheet)
    for i, (im, f) in enumerate(zip(ims, fs)):
        x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 28)
        sheet.paste(im.resize((w, h)), (x, y)); d.text((x, y + h + 6), Path(f).name, fill=(200, 204, 211))
    out = a.get("out", os.path.join(a["dir"], "sheet.png")); sheet.save(out); print("sheet:", out)


def cmd_encode(a):
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found"); sys.exit(2)
    fs = sorted(glob.glob(os.path.join(a["dir"], "*.png")))
    if not fs:
        print("no PNG frames"); sys.exit(1)
    lst = Path(tempfile.mkstemp(suffix=".txt")[1]); fps = float(a.get("fps", 30))
    lst.write_text("".join(f"file '{Path(f).resolve()}'\nduration {1 / fps}\n" for f in fs))
    out = a.get("out", "film.mp4")
    r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), "-movflags", "+faststart", out], capture_output=True, text=True)
    print(("encoded: " + out) if r.returncode == 0 else r.stderr[-800:])


def parse(argv):
    a, extra, pos = {}, [], []
    if "--" in argv:
        i = argv.index("--"); argv, extra = argv[:i], argv[i + 1:]
    it = iter(range(len(argv))); skip = False
    for i in range(len(argv)):
        if skip:
            skip = False; continue
        x = argv[i]
        if x.startswith("--"):
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                a[x[2:]] = argv[i + 1]; skip = True
            else:
                a[x[2:]] = True
        else:
            pos.append(x)
    return pos, a, extra


def main():
    pos, a, extra = parse(sys.argv[1:])
    if not pos:
        print(__doc__); return
    c = pos[0]
    if c == "info":
        cmd_info(a)
    elif c == "run":
        a["script"] = pos[1]; cmd_run(a, extra)
    elif c == "render":
        a["file"] = pos[1]; cmd_render(a)
    elif c == "sheet":
        a["dir"] = pos[1]; cmd_sheet(a)
    elif c == "encode":
        a["dir"] = pos[1]; cmd_encode(a)
    else:
        print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main()
