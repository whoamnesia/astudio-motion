#!/usr/bin/env python3
"""astudio-motion easing - springs, curves and motion tokens.

Usage:
  easing.py spring [--bounce 0.2 --duration 0.5] | [--damping 0.8 --response 0.45] | [--stiffness 170 --damping-c 26 --mass 1]
      Closed-form damped spring -> CSS linear() easing + the real settle duration, GSAP/Motion/SwiftUI/Compose
      equivalents and an ASCII plot. (Apple/Motion style: bounce 0 = critically damped, 0.15 snappy, 0.3 bouncy.)
  easing.py bezier 0.16 1 0.3 1 [--name expo-out]
      Plot a cubic-bezier and print its overshoot and the time to reach 90% / 99% of the travel.
  easing.py compare ui-out expo-out cubic-in-out
      Side-by-side progress table of named curves (from data/easings.csv) at 0..100% time.
  easing.py tokens [--out design-tokens] [--prefix motion]
      Write the astudio motion token set: motion.tokens.json (W3C DTCG 2025.10: duration, cubicBezier,
      transition composites), motion.css (CSS custom properties + reduced-motion overrides) and
      motion.tailwind.css (Tailwind v4 @theme --ease-*/--duration-* variables).
Python 3.8+, standard library only.
"""
import argparse, csv, json, math, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


# ---------- springs ----------
def spring_curve(zeta, omega, settle=0.001, max_t=10.0, step=1 / 240):
    """Unit step response of a damped harmonic oscillator; returns (times, values, settle_time)."""
    ts, xs = [], []
    t = 0.0
    last_out = 0.0
    while t <= max_t:
        if zeta < 1:
            wd = omega * math.sqrt(1 - zeta * zeta)
            x = 1 - math.exp(-zeta * omega * t) * (math.cos(wd * t) + zeta * omega / wd * math.sin(wd * t))
        elif zeta == 1:
            x = 1 - math.exp(-omega * t) * (1 + omega * t)
        else:
            r1 = -omega * (zeta - math.sqrt(zeta * zeta - 1)); r2 = -omega * (zeta + math.sqrt(zeta * zeta - 1))
            x = 1 - (r2 * math.exp(r1 * t) - r1 * math.exp(r2 * t)) / (r2 - r1)
        ts.append(t); xs.append(x)
        if abs(x - 1) > settle:
            last_out = t
        elif t - last_out > 0.1:
            break
        t += step
    return ts, xs, last_out


def css_linear(ts, xs, total, points=40):
    """Sample the curve into a CSS linear() function with percentage stops at local extrema + even samples."""
    keep = set(round(i * (len(ts) - 1) / points) for i in range(points + 1))
    for i in range(1, len(xs) - 1):
        if (xs[i] - xs[i - 1]) * (xs[i + 1] - xs[i]) < 0:
            keep.add(i)
    out = []
    for i in sorted(keep):
        if ts[i] > total:
            continue
        out.append(f"{xs[i]:.4f} {ts[i] / total * 100:.1f}%")
    out.append("1 100%")
    return "linear(" + ", ".join(out) + ")"


def plot(f, w=56, h=14, label=""):
    vals = [f(i / (w - 1)) for i in range(w)]
    lo, hi = min(0.0, min(vals)), max(1.0, max(vals))
    rows = []
    for r in range(h, -1, -1):
        y = lo + (hi - lo) * r / h
        line = "".join("█" if abs(v - y) <= (hi - lo) / (2 * h) else ("·" if abs(y - 1) < (hi - lo) / (2 * h) or abs(y) < (hi - lo) / (2 * h) else " ") for v in vals)
        rows.append(f"{y:5.2f} |{line}")
    rows.append("      +" + "-" * w + "> time" + (f"   {label}" if label else ""))
    return "\n".join(rows)


def cmd_spring(a):
    if a.stiffness:
        k, c, m = a.stiffness, a.damping_c or 10.0, a.mass
        omega = math.sqrt(k / m); zeta = c / (2 * math.sqrt(k * m)); response = 2 * math.pi / omega
    elif a.damping is not None:
        zeta = a.damping; response = a.response; omega = 2 * math.pi / response
    else:
        zeta = 1 - max(0.0, min(0.99, a.bounce)); response = a.duration; omega = 2 * math.pi / response
    ts, xs, settle = spring_curve(zeta, omega)
    total = max(settle, 0.05)
    overshoot = max(0.0, max(xs) - 1)
    lin = css_linear(ts, xs, total)
    k = omega ** 2; c = 2 * zeta * omega
    print(f"spring: damping ratio {zeta:.3f} · response {response:.3f}s · stiffness {k:.1f} · damping {c:.2f} (mass 1)")
    print(f"settles (±0.1%) after {total * 1000:.0f}ms · overshoot {overshoot * 100:.1f}%")
    feel = "no bounce (critically/over-damped)" if zeta >= 1 else "premium settle" if zeta >= 0.75 else "snappy" if zeta >= 0.6 else "playful" if zeta >= 0.4 else "cartoon"
    print(f"feel: {feel}\n")
    print(plot(lambda p: xs[min(len(xs) - 1, int(p * total / (ts[1] - ts[0])))], label=f"{total * 1000:.0f}ms"))
    print("\nCSS:")
    print(f"  --ease-spring: {lin};")
    print(f"  transition: transform {total * 1000:.0f}ms var(--ease-spring);")
    print("Motion (motion.dev):  { type: 'spring', visualDuration: %.2f, bounce: %.2f }" % (response, max(0.0, 1 - zeta)))
    print("Motion (physics):     { type: 'spring', stiffness: %.0f, damping: %.1f, mass: 1 }" % (k, c))
    print("SwiftUI:              .spring(duration: %.2f, bounce: %.2f)" % (response, max(0.0, 1 - zeta)))
    print("Compose:              spring(dampingRatio = %.2ff, stiffness = %.0ff)" % (zeta, k))
    print("Reanimated 4:         withSpring(v, { duration: %d, dampingRatio: %.2f })" % (round(response * 1000), zeta))
    print("GSAP (approx):        %s" % ("expo.out" if zeta >= 1 else "elastic.out(1, %.2f)" % max(0.2, min(1.0, zeta * 0.75)) if zeta < 0.6 else "back.out(%.1f)" % (1 + overshoot * 10)))


def bez(x1, y1, x2, y2):
    def sample(t, a, b):
        return 3 * a * t * (1 - t) ** 2 + 3 * b * t * t * (1 - t) + t ** 3
    def solve(x):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if sample(mid, x1, x2) < x: lo = mid
            else: hi = mid
        return sample((lo + hi) / 2, y1, y2)
    return solve


def cmd_bezier(a):
    f = bez(*a.p)
    vals = [f(i / 400) for i in range(401)]
    t90 = next(i for i, v in enumerate(vals) if v >= 0.9) / 400
    t99 = next(i for i, v in enumerate(vals) if v >= 0.99) / 400
    print(f"cubic-bezier({', '.join(str(x) for x in a.p)})" + (f"  [{a.name}]" if a.name else ""))
    print(f"reaches 90% of travel at {t90 * 100:.0f}% of the duration, 99% at {t99 * 100:.0f}% · overshoot {max(0, max(vals) - 1) * 100:.1f}% · undershoot {max(0, -min(vals)) * 100:.1f}%\n")
    print(plot(f))
    if t90 < 0.35:
        print("\nreads as: fast start, long tail (ease-out family) - good for arrivals")
    elif t90 > 0.75:
        print("\nreads as: slow start (ease-in family) - only for exits that accelerate away, never UI entrances")


def easings():
    with open(DATA / "easings.csv", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def parse_css(s):
    m = re.match(r"cubic-bezier\(([^)]+)\)", s.strip())
    return [float(x) for x in m.group(1).split(",")] if m else None


def cmd_compare(a):
    rows = {r["Name"].split(" ")[0]: r for r in easings()}
    fs = []
    for n in a.names:
        r = rows.get(n) or next((v for k, v in rows.items() if k.startswith(n)), None)
        p = r and parse_css(r["CSS"])
        if not p:
            print(f"skip {n}: not a cubic-bezier in data/easings.csv"); continue
        fs.append((n, bez(*p)))
    print("time  " + "".join(f"{n[:12]:>13}" for n, _ in fs))
    for i in range(0, 11):
        t = i / 10
        print(f"{t * 100:4.0f}% " + "".join(f"{f(t) * 100:12.0f}%" for _, f in fs))


TOKENS = {
    "duration": {"instant": 0, "micro": 100, "fast": 150, "base": 200, "moderate": 300, "slow": 450, "deliberate": 600, "scenic": 900},
    "ease": {
        "out": [0.23, 1, 0.32, 1], "in-out": [0.77, 0, 0.175, 1], "drawer": [0.32, 0.72, 0, 1], "expo-out": [0.16, 1, 0.3, 1],
        "quart-out": [0.25, 1, 0.5, 1], "cubic-in-out": [0.65, 0, 0.35, 1], "in": [0.32, 0, 0.67, 0], "back-out": [0.34, 1.56, 0.64, 1],
        "standard": [0.2, 0, 0, 1],
    },
    "transition": {
        "press": ("fast", "out"), "hover": ("fast", "standard"), "popover": ("base", "out"), "modal": ("moderate", "out"),
        "drawer": ("slow", "drawer"), "move": ("moderate", "in-out"), "reveal": ("deliberate", "expo-out"), "page": ("slow", "cubic-in-out"),
    },
    "stagger": {"list": 50, "words": 90, "letters": 33},
}


def cmd_tokens(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); p = a.prefix
    dt = {p: {"duration": {}, "ease": {}, "transition": {}, "stagger": {}}}
    for k, v in TOKENS["duration"].items():
        dt[p]["duration"][k] = {"$type": "duration", "$value": {"value": v, "unit": "ms"}}
    for k, v in TOKENS["ease"].items():
        dt[p]["ease"][k] = {"$type": "cubicBezier", "$value": v}
    for k, (d, e) in TOKENS["transition"].items():
        dt[p]["transition"][k] = {"$type": "transition", "$value": {"duration": f"{{{p}.duration.{d}}}", "delay": {"value": 0, "unit": "ms"}, "timingFunction": f"{{{p}.ease.{e}}}"}}
    for k, v in TOKENS["stagger"].items():
        dt[p]["stagger"][k] = {"$type": "duration", "$value": {"value": v, "unit": "ms"}}
    (out / "motion.tokens.json").write_text(json.dumps(dt, indent=2))
    css = [":root {"]
    css += [f"  --{p}-duration-{k}: {v}ms;" for k, v in TOKENS["duration"].items()]
    css += [f"  --{p}-ease-{k}: cubic-bezier({', '.join(str(x) for x in v)});" for k, v in TOKENS["ease"].items()]
    css += [f"  --{p}-{k}: var(--{p}-duration-{d}) var(--{p}-ease-{e});" for k, (d, e) in TOKENS["transition"].items()]
    css += [f"  --{p}-stagger-{k}: {v}ms;" for k, v in TOKENS["stagger"].items()]
    css += ["}", "", "/* Reduced motion: keep fades and colour, drop travel. Components read these, never hard-code. */",
            "@media (prefers-reduced-motion: reduce) {", "  :root {",
            f"    --{p}-duration-slow: var(--{p}-duration-fast);", f"    --{p}-duration-deliberate: var(--{p}-duration-base);",
            f"    --{p}-duration-scenic: var(--{p}-duration-base);", f"    --{p}-travel: 0px;", "  }", "}",
            "", f":root {{ --{p}-travel: 16px; }}  /* distance for rise/slide entrances */"]
    (out / "motion.css").write_text("\n".join(css) + "\n")
    tw = ["@theme {"]
    tw += [f"  --ease-{k}: cubic-bezier({', '.join(str(x) for x in v)});" for k, v in TOKENS["ease"].items()]
    tw += [f"  --duration-{k}: {v}ms;" for k, v in TOKENS["duration"].items() if v]
    tw += ["}"]
    (out / "motion.tailwind.css").write_text("\n".join(tw) + "\n")
    print(f"wrote {out}/motion.tokens.json, motion.css, motion.tailwind.css")
    print("Use: transition: transform var(--%s-modal); Tailwind: ease-expo-out duration-moderate" % p)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("spring")
    s.add_argument("--bounce", type=float, default=0.0); s.add_argument("--duration", type=float, default=0.5)
    s.add_argument("--damping", type=float); s.add_argument("--response", type=float, default=0.5)
    s.add_argument("--stiffness", type=float); s.add_argument("--damping-c", type=float); s.add_argument("--mass", type=float, default=1.0)
    b = sub.add_parser("bezier"); b.add_argument("p", type=float, nargs=4); b.add_argument("--name")
    c = sub.add_parser("compare"); c.add_argument("names", nargs="+")
    t = sub.add_parser("tokens"); t.add_argument("--out", default="design-tokens"); t.add_argument("--prefix", default="motion")
    a = ap.parse_args()
    {"spring": cmd_spring, "bezier": cmd_bezier, "compare": cmd_compare, "tokens": cmd_tokens}[a.cmd](a)


if __name__ == "__main__":
    main()
