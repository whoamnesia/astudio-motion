#!/usr/bin/env python3
"""astudio-motion lint - scan source for motion craft bugs, AI-slop motion tells and outdated APIs.

Usage:
  motion_lint.py <paths...> [--mode ui|marketing|video] [--allow rule,rule] [--json]
  Inline exception for a deliberate case: put `motion-lint-allow <rule> (reason)` in a comment on the same line.

Modes: ui (product UI - strictest on duration/bounce/stagger, text appears instantly), marketing (showcase sites:
full choreography - text and every block reveal, so stagger/text rules are off; checks reveal smoothness and that
the LCP element is not hidden), video (HTML rendered to video: loops/infinite banned, reduced-motion not required).
Covers CSS/SCSS, JS/TS/JSX/TSX, Vue, Svelte, Astro, HTML. It finds what can be measured in source;
the feel still needs eyes on scripts/motion.cjs strips. Exit 1 when any FAIL. Python 3.8+, stdlib only.
"""
import argparse, json, re, sys
from pathlib import Path

EXT = {".css", ".scss", ".less", ".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".html", ".htm"}
SKIP = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", ".astudio", "vendor"}

# (id, severity, regex, message, modes)
RULES = [
    ("transition-all", "FAIL", r"transition(?:-property)?\s*:\s*all\b|\btransition-all\b|transition:\s*['\"]all", "transition: all - name the exact properties (transform, opacity)", "all"),
    ("scale-zero", "FAIL", r"scale\(\s*0\s*\)|\bscale-0\b|\bscale\s*:\s*0\s*[,}]", "entrance from scale(0) - nothing appears from nothing; start at 0.9-0.97 + opacity 0", "ui marketing"),
    ("ease-in-ui", "WARN", r"transition[^;{}\n]*\bease-in\b(?!-out)|animation[^;{}\n]*\bease-in\b(?!-out)|ease:\s*['\"](?:power\d|expo|circ|sine|quad|cubic)\.in['\"]", "ease-in on UI delays the moment the user watches - use a strong ease-out", "ui marketing"),
    ("layout-props", "WARN", r"transition[^;{}\n]*\b(?:width|height|top|left|right|bottom|margin|padding)\b|(?:gsap\.(?:to|from|fromTo)|animate)\([^)]*\b(?:width|height|top|left|margin|padding)\s*:", "animating layout properties - use transform/scale/clip-path (height is tolerated only for accordions)", "all"),
    ("pulse-loop", "WARN", r"\banimate-pulse\b|\banimate-ping\b|@keyframes\s+[\w-]*(?:pulse|glow|breath|throb)", "pulsing/glowing loop - the top AI-slop motion tell; use a static treatment unless it is a real live indicator", "ui marketing video"),
    ("bounce-ui", "WARN", r"\banimate-bounce\b|bounce\.out|elastic\.out|bounce\s*:\s*0\.[4-9]|cubic-bezier\([^)]*,\s*1\.[4-9]\d*\s*,", "bounce/elastic on interface motion - reserve for rare playful moments; utility UI never bounces", "ui"),
    ("bounce-video", "WARN", r"bounce\.out|elastic\.out\(\s*1\s*,\s*0\.[0-3]", "bounce/elastic in a film reads cheap - use back.out(1.4-1.7) or a spring with damping >= 0.7", "video"),
    ("blur-heavy", "WARN", r"blur\(\s*(?:2[1-9]|[3-9]\d|\d{3,})px\s*\)", "animated blur over 20px is expensive (Safari) and smears - 2-12px is enough", "all"),
    ("will-change-global", "WARN", r"\*\s*\{[^}]*will-change|will-change\s*:\s*(?:transform|opacity)[^;]*;[^}]*\}\s*\.[\w-]+\s*\*", "will-change on many elements - apply only to what is about to animate, then remove", "all"),
    ("setstate-per-frame", "WARN", r"(?:requestAnimationFrame|useFrame|onPointerMove|addEventListener\(\s*['\"](?:scroll|pointermove|mousemove)['\"])[\s\S]{0,160}\bset(?!Property|Attribute|Timeout|Interval|PointerCapture)[A-Z]\w*\(", "React state set per frame / per pointer event - write to ref.current.style or a motion value", "all"),
    ("scroll-listener", "WARN", r"addEventListener\(\s*['\"]scroll['\"]", "scroll listener driving animation - use ScrollTrigger, IntersectionObserver or animation-timeline", "ui marketing"),
    ("infinite-loop-video", "FAIL", r"repeat\s*:\s*-1|animation[^;{}\n]*\binfinite\b|Math\.random\(\)|Date\.now\(\)", "non-deterministic or infinite motion in a rendered film - everything must be a function of timeline time (seeded random, finite repeats)", "video"),
    ("marquee-no-pause", "WARN", r"\b(?:marquee|ticker)[^{}]*\{[^}]*infinite", "auto-moving content > 5s needs a pause control (WCAG 2.2.2) and must pause under reduced motion", "ui marketing"),
    ("keyframes-toast", "WARN", r"\.(?:toast|snackbar)[\w-]*\s*\{[^}]*animation\s*:", "keyframes on a toast - rapid triggers restart from zero; use transitions that retarget", "ui marketing"),
    ("gsap-markers", "WARN", r"markers\s*:\s*true", "ScrollTrigger markers left on", "all"),
    ("gsap-scrub-toggle", "FAIL", r"scrollTrigger\s*:\s*\{[^}]*scrub[^}]*toggleActions|scrollTrigger\s*:\s*\{[^}]*toggleActions[^}]*scrub", "scrub and toggleActions on the same ScrollTrigger - pick one (scrub wins)", "all"),
    ("gsap-child-scrolltrigger", "FAIL", r"(?:timeline|tl)\s*\(\s*\)\s*\.(?:to|from|fromTo)\([^;]*scrollTrigger", "ScrollTrigger on a child tween of a timeline - put it on the timeline itself", "all"),
    ("gsap-club-token", "WARN", r"npm\.greensock\.com|gsap-auth-token|@gsap/shockingly", "outdated GSAP Club registry - every plugin is in the public 'gsap' package now", "all"),
    ("three-clock", "WARN", r"new\s+THREE\.Clock\(|new\s+Clock\(\)|getElapsedTime\(\)", "THREE.Clock is deprecated (r183) - THREE.Timer: timer.connect(document); timer.update(); timer.getElapsed()", "all"),
    ("three-pcfsoft", "WARN", r"PCFSoftShadowMap", "PCFSoftShadowMap deprecated (r182) - PCFShadowMap is already soft", "all"),
    ("three-examples-path", "WARN", r"three/examples/jsm/", "use 'three/addons/...' - the examples/jsm path breaks under import maps", "all"),
    ("three-rgbe", "WARN", r"RGBELoader", "RGBELoader renamed HDRLoader (r180), import from three/addons/loaders/HDRLoader.js", "all"),
    ("three-encoding", "FAIL", r"outputEncoding|sRGBEncoding|LinearEncoding", "removed API - renderer.outputColorSpace = THREE.SRGBColorSpace; texture.colorSpace", "all"),
    ("three-legacy-build", "FAIL", r"three(?:\.min)?\.js['\"]\s*>|build/three\.min\.js", "build/three(.min).js was removed (r161) - load the ES module via import map/bundler", "all"),
    ("r3f-fixed-step", "WARN", r"useFrame\(\s*\(\s*\)\s*=>[^}]*(?:\+=|-=)\s*0?\.\d+", "fixed per-frame increment - multiply by delta so speed is the same at 60/120Hz", "all"),
    ("webgpu-init", "WARN", r"new\s+(?:THREE\.)?WebGPURenderer\((?![\s\S]{0,600}(?:await\s+\w+\.init\(|setAnimationLoop))", "WebGPURenderer needs await renderer.init() (or setAnimationLoop) before render, plus a WebGL fallback", "all"),
    ("lottie-web", "INFO", r"from\s+['\"]lottie-web['\"]|require\(['\"]lottie-web['\"]\)", "lottie-web is legacy - prefer @lottiefiles/dotlottie-web (canvas+WASM, .lottie)", "all"),
    ("framer-motion-pkg", "INFO", r"from\s+['\"]framer-motion['\"]", "framer-motion is now 'motion' (import { motion } from 'motion/react')", "all"),
]


def files(paths):
    for p in map(Path, paths):
        if p.is_file() and p.suffix.lower() in EXT:
            yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in EXT and not any(part in SKIP for part in f.parts):
                    yield f


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def scan(path, mode, allow):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    out = []
    for rid, sev, rx, msg, modes in RULES:
        if rid in allow or (modes != "all" and mode not in modes.split()):
            continue
        for m in re.finditer(rx, text, re.I if rid not in ("three-clock",) else 0):
            ln = line_of(text, m.start())
            line = text.splitlines()[ln - 1] if text else ""
            if re.search(r"motion-lint-allow\b[^\n]*\b" + re.escape(rid) + r"\b", line):   # inline: // motion-lint-allow ease-in-ui (reason)
                continue
            src = line.strip()[:140]
            out.append({"file": str(path), "line": ln, "rule": rid, "sev": sev, "msg": msg, "src": src})
            if len(out) > 400:
                break
    return out


def project_checks(paths, mode, allow, texts):
    out = []
    joined = "\n".join(texts.values())
    animates = re.search(r"@keyframes|transition\s*:|\bgsap\.|motion\.|animate\(|\.animate\(|useSpring|withSpring|AnimatePresence|ScrollTrigger|animation-timeline", joined)
    if mode != "video" and animates and "reduced-motion" not in allow:
        if not re.search(r"prefers-reduced-motion|useReducedMotion|reducedMotion|matchMedia\([^)]*reduce|ReduceMotion|motion-reduce:", joined):
            out.append({"file": "(project)", "line": 0, "rule": "no-reduced-motion", "sev": "FAIL",
                        "msg": "motion with no prefers-reduced-motion path anywhere - tier it: remove travel/parallax, keep fades and state colour", "src": ""})
    if re.search(r"ScrollTrigger", joined) and not re.search(r"registerPlugin\([^)]*ScrollTrigger", joined) and "gsap-register" not in allow:
        out.append({"file": "(project)", "line": 0, "rule": "gsap-register", "sev": "FAIL", "msg": "ScrollTrigger used but gsap.registerPlugin(ScrollTrigger) not found", "src": ""})
    if mode != "video":
        hov = len(re.findall(r"hover:scale-1\d\d|:hover\s*\{[^}]*transform\s*:\s*scale\(1\.0\d", joined))
        if hov >= 3 and "hover-scale-everywhere" not in allow:
            out.append({"file": "(project)", "line": 0, "rule": "hover-scale-everywhere", "sev": "WARN", "msg": f"{hov} components share a hover scale - AI-slop tell; keep it for one deliberate element", "src": ""})
        gated = re.search(r"\(\s*hover\s*:\s*hover\s*\)", joined)
        if re.search(r":hover\s*\{[^}]*transform", joined) and not gated and "hover-ungated" not in allow:
            out.append({"file": "(project)", "line": 0, "rule": "hover-ungated", "sev": "WARN", "msg": "hover transforms not gated by @media (hover:hover) and (pointer:fine) - touch fires false hovers", "src": ""})
        # elements that share one generic entrance: bare data-reveal/data-animate attributes or fade-up presets
        # (typed reveals such as data-reveal="heading" / "image" are a reveal grammar, not slop)
        fades = len(re.findall(r"fade-?in-?up|fadeInUp|whileInView=\{\{\s*opacity:\s*1,\s*y:\s*0|data-(?:reveal|animate|aos)(?:=[\"'](?:|fade|fade-up|up|reveal|in)[\"'])?(?=[\s>/])", joined, re.I))
        if fades >= 4 and "uniform-fade-up" not in allow:
            out.append({"file": "(project)", "line": 0, "rule": "uniform-fade-up", "sev": "WARN", "msg": f"{fades} uses of the same fade-and-rise - uniform entrance slop; vary by content or drop most of them", "src": ""})
        stag = len(re.findall(r"staggerChildren|stagger\s*:", joined))
        if mode == "ui" and stag >= 2 and "stagger-spam" not in allow:
            out.append({"file": "(project)", "line": 0, "rule": "stagger-spam", "sev": "WARN", "msg": f"{stag} staggered entrances - one staggered moment per view", "src": ""})
        heads = len(re.findall(r"<(?:motion\.)?(?:h[1-3]|p|nav)\b[^>]*(?:initial=|whileInView=|data-animate|class=\"[^\"]*(?:reveal|fade))", joined))
        if mode == "ui" and heads >= 3 and "motion-on-static-text" not in allow:
            out.append({"file": "(project)", "line": 0, "rule": "motion-on-static-text", "sev": "WARN", "msg": f"{heads} text/nav elements animate on mount - reading content should appear instantly", "src": ""})
    if mode == "marketing":
        short = re.findall(r"scrollTrigger[^;]{0,400}?duration\s*:\s*0?\.[0-5]\d*\b|duration\s*:\s*0?\.[0-5]\d*\b[^;]{0,400}?scrollTrigger", joined)
        if short and "short-reveal" not in allow:
            out.append({"file": "(project)", "line": 0, "rule": "short-reveal", "sev": "WARN", "msg": f"{len(short)} scroll reveal(s) under 0.6s - on a showcase site reveals read abrupt; 0.9-1.4s on expo.out/power4.out (reference/site-motion.md)", "src": ""})
        hidden = re.findall(r"hero[^\n]{0,120}(?:img|photo|media|picture|image)[^\n]{0,160}(?:autoAlpha|opacity)\s*:\s*0(?![.\d])|hero[^\n]{0,160}inset\(\s*(?:100%|0(?:%|px)?\s+0(?:%|px)?\s+100%|100%\s+0)", joined, re.I)
        if hidden and "lcp-hidden" not in allow:
            out.append({"file": "(project)", "line": 0, "rule": "lcp-hidden", "sev": "WARN", "msg": "hero media starts fully hidden (opacity 0 / clip inset 100%) - the LCP image must paint on the first frame: start it visible with a partial clip (inset 8-14%) and scale 1.12-1.2 -> 1", "src": hidden[0][:120]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--mode", choices=["ui", "marketing", "video"], default="marketing")
    ap.add_argument("--allow", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    allow = {x.strip() for x in a.allow.split(",") if x.strip()}
    res, texts = [], {}
    for f in files(a.paths):
        res += scan(f, a.mode, allow)
        try:
            texts[str(f)] = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
    res += project_checks(a.paths, a.mode, allow, texts)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for r in res:
            loc = f"{r['file']}:{r['line']}" if r["line"] else r["file"]
            print(f"{r['sev']:4} {loc}  [{r['rule']}] {r['msg']}" + (f"\n       {r['src']}" if r["src"] else ""))
        fails = sum(r["sev"] == "FAIL" for r in res)
        print(f"\n{len(res)} findings, FAIL={fails} ({len(texts)} files, mode {a.mode})" if res else f"motion lint: no findings ({len(texts)} files, mode {a.mode})")
    sys.exit(1 if any(r["sev"] == "FAIL" for r in res) else 0)


if __name__ == "__main__":
    main()
