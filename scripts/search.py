#!/usr/bin/env python3
"""astudio-motion search - BM25 search over the astudio motion & 3D database.

Usage:
  search.py "<query>" [-d DOMAIN] [-n N] [--json]
  search.py "<what moves, where, for whom>" --plan [-p "Project"]   # motion-plan draft
  search.py --list

Domains: easing, duration, ui (component recipes), transition, shot (38 launch-film shots),
gsap (GSAP presets), tool, web3d, shader, learn (free courses/docs to point users to).
Queries match English data: translate briefs into 2-5 English keywords first
("плавное появление карточек" -> "card stagger entrance").
Results are starting points to reason about, never instructions. Python 3.8+, stdlib only.
"""
import argparse, csv, json, math, re, sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# domain: (file, search columns (first = identity, weighted x3), output columns or None = all)
DOMAINS = {
    "easing": ("easings.csv", ["Name", "Family", "Use for", "Feel", "GSAP"], None),
    "duration": ("durations.csv", ["Element", "Context", "Notes"], None),
    "ui": ("ui-recipes.csv", ["Component", "Keywords", "Motion", "Tool"], None),
    "transition": ("transitions.csv", ["Transition", "Keywords", "Medium", "Cause / when"], None),
    "shot": ("shots.csv", ["Shot", "Keywords", "What", "Position", "Why"],
             ["Shot", "Slug", "Position", "What", "Timing", "Easing", "Camera", "Subject", "Sync", "Style", "Why", "Seen in"]),
    "gsap": ("gsap-presets.csv", ["Category", "Keywords", "Trigger", "Intensity Tier"],
             ["Category", "Intensity Tier", "Trigger", "Duration", "Easing", "GSAP Snippet", "Framework Notes", "Do", "Don't", "Performance Notes"]),
    "tool": ("tools.csv", ["Tool", "Keywords", "Best for", "Category"], None),
    "web3d": ("web3d-patterns.csv", ["Pattern", "Keywords", "Best for", "Composition"], None),
    "shader": ("shader-techniques.csv", ["Technique", "Keywords", "Look", "Use for"], None),
    "learn": ("learning.csv", ["Title", "What it teaches", "Track", "Author", "Format"], None),
}

AUTO = {
    "easing": "ease easing curve bezier spring bounce linear overshoot",
    "duration": "duration timing ms seconds long fast slow hold stagger delay",
    "ui": "button dropdown modal drawer toast tooltip accordion tab toggle hover press skeleton marquee cursor",
    "transition": "transition seam cut wipe morph zoom whip iris crossfade page route",
    "shot": "shot launch film promo reveal opening ending lockup camera montage",
    "gsap": "gsap scrolltrigger timeline splittext flip",
    "tool": "tool app software library runtime which choose after effects cavalry blender unreal figma rive lottie remotion",
    "web3d": "3d three threejs r3f webgl webgpu model scene camera particles globe configurator",
    "shader": "shader glsl wgsl noise sdf raymarch fbm gradient distortion fluid",
    "learn": "learn course tutorial lesson study youtube docs",
}

SYNONYMS = {
    "appear": "entrance enter reveal", "entrance": "enter reveal", "intro": "opening reveal entrance",
    "logo": "lockup mark wordmark logo", "outro": "ending lockup close", "ending": "close lockup",
    "card": "cards stagger list", "list": "stagger list", "menu": "dropdown menu", "popup": "modal popover",
    "notification": "toast", "loader": "progress spinner loader", "loading": "loader progress skeleton",
    "scroll": "scroll scrolltrigger reveal pinned", "parallax": "parallax depth layers",
    "text": "text split type headline", "typography": "type text kinetic", "kinetic": "kinetic type text",
    "product": "product reveal device", "app": "ui product interface", "ui": "interface ui",
    "video": "film video shot", "promo": "launch promo film", "ad": "promo vertical social",
    "smooth": "ease-out expo smooth", "bouncy": "spring bounce overshoot back", "snappy": "ui-out snappy fast",
    "cinematic": "camera expo inOut cinematic", "premium": "expo spring premium",
    "3d": "3d three webgl", "particles": "particles points", "background": "background gradient shader",
}

TOKEN = re.compile(r"[a-zа-яё0-9#.]+", re.I)


def tok(s):
    return [t.lower().strip(".") for t in TOKEN.findall(s or "") if len(t.strip(".")) > 1]


def expand(q):
    return q + " " + " ".join(SYNONYMS[t] for t in tok(q) if t in SYNONYMS)


def load(fname):
    p = DATA / fname
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


class BM25:
    def __init__(self, docs, k1=1.4, b=0.75):
        self.docs = [tok(d) for d in docs]
        self.k1, self.b = k1, b
        self.avg = sum(map(len, self.docs)) / max(1, len(self.docs))
        df = Counter(t for d in self.docs for t in set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.tf = [Counter(d) for d in self.docs]

    def score(self, q):
        qt = tok(q)
        out = []
        for i, d in enumerate(self.docs):
            s = 0.0
            for t in qt:
                f = self.tf[i].get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(d) / self.avg))
            out.append(s)
        return out


def search(domain, query, n=3):
    fname, scols, ocols = DOMAINS[domain]
    rows = load(fname)
    if not rows:
        return []
    ocols = ocols or [c for c in rows[0].keys() if c.lower() not in ("no", "id")]
    bm = BM25([" ".join([r.get(scols[0], "")] * 3 + [r.get(c, "") for c in scols]) for r in rows])
    sc = bm.score(expand(query))
    ranked = sorted(range(len(rows)), key=lambda i: -sc[i])
    res = []
    for i in ranked[:n]:
        if sc[i] <= 0:
            break
        res.append({"_score": round(sc[i], 2), **{c: rows[i].get(c, "") for c in ocols if rows[i].get(c)}})
    return res


def detect(query):
    q = set(tok(expand(query)))
    best, bs = "ui", 0
    for d, kw in AUTO.items():
        s = len(q & set(kw.split()))
        if s > bs:
            best, bs = d, s
    return best


SITE_RX = re.compile(r"\b(site|website|landing|homepage|web ?page|awwwards|portfolio|showcase)\b|сайт|лендинг|страниц", re.I)
SITE_SYSTEM = [
    "Total choreography (reference/site-motion.md): every visible element performs - headings, body text, labels, "
    "buttons, links, images, icons, numbers, rows, rules, badges, maps, header, footer - from one reveal grammar.",
    "Build from skills/gsap/templates/site-motion.js + site-motion.css: tag every element with data-reveal, the hero "
    "with data-hero, maps with data-map; SiteMotion.init().",
    "Smooth numbers: reveals 1.1-1.3s expo.out; image wipe 1.4s power4.inOut + inner scale 1.9s; staggers chars 0.02 / "
    "words 0.05 / lines 0.09 / rows 0.06 / cards 0.1; hovers 0.55s; Lenis lerp 0.09; scrub 0.8-1.2; nothing under 0.6s.",
    "LCP-safe hero: the hero photo visible at frame 0 (partial clip + scale), heading rising from t=0, settled <= 2.0s.",
    "Check: motion.cjs coverage (no static sections, >= 90% moving, LCP delta < 300ms) + check (no hard-stop) + strips.",
]


def plan(query, project=None):
    """A motion-plan draft: what the database suggests for this brief."""
    site = bool(SITE_RX.search(query)) and not re.search(r"\b(video|film|reel|ролик|видео)\b", query, re.I)
    q_tool = query + (" web gsap scrolltrigger splittext lenis css" if site else "")
    q_ui = query + (" showcase text lines button hero image count map scroll reveal" if site else "")
    durs = search("duration", query + (" showcase web reveal hero" if site else ""), 6 if site else 4)
    if site:
        durs = [d for d in durs if d.get("Context", "").startswith("Web")] or durs
    return {
        "project": project or "Untitled", "query": query,
        "site_system": SITE_SYSTEM if site else [],
        "tools": search("tool", q_tool, 3),
        "ui_recipes": search("ui", q_ui, 6 if site else 4),
        "easings": search("easing", query + (" expo-out reveal in-out" if site else " ui-out expo"), 4),
        "durations": durs,
        "transitions": search("transition", query, 3),
        "shots": [] if site else search("shot", query, 3),
        "web3d": search("web3d", query, 2),
        "shaders": search("shader", query, 2),
        "learn": search("learn", query, 3),
        "note": "Starting points only. Decide the motion language first (reference/direction.md), gate every "
                "animation by frequency and purpose (reference/principles.md), then render and look "
                "(scripts/motion.cjs) before calling anything done.",
    }


def md_plan(p):
    L = [f"# Motion plan draft: {p['project']}", f"_Query: {p['query']}_", ""]
    if p.get("site_system"):
        L.append("## Showcase site: total choreography")
        L += [f"- {x}" for x in p["site_system"]] + [""]
    sec = [("Tools", "tools", "Tool", ["Best for", "Agent workflow", "Skill"]),
           ("UI recipes", "ui_recipes", "Component", ["Motion", "Curve", "Duration", "Gotchas"]),
           ("Easing candidates", "easings", "Name", ["CSS", "GSAP", "Use for"]),
           ("Durations", "durations", "Element", ["Range", "Notes"]),
           ("Transitions", "transitions", "Transition", ["How it is built", "Duration", "Cause / when"]),
           ("Shots (launch-film language)", "shots", "Shot", ["What", "Easing"]),
           ("Web 3D patterns", "web3d", "Pattern", ["Composition", "Build"]),
           ("Shader techniques", "shaders", "Technique", ["Look", "Library file"]),
           ("Learn more", "learn", "Title", ["Author", "URL"])]
    for title, key, ident, cols in sec:
        if not p.get(key):
            continue
        L.append(f"## {title}")
        for r in p[key]:
            L.append(f"- **{r.get(ident, '')}** - " + " · ".join(f"{c}: {r[c]}" for c in cols if r.get(c)))
        L.append("")
    L.append(f"_{p['note']}_")
    return "\n".join(L)


def fmt(results):
    out = []
    for i, r in enumerate(results, 1):
        out.append(f"--- [{i}] score={r.pop('_score')}")
        for k, v in r.items():
            out.append(f"{k}: {v}")
    return "\n".join(out) if out else "No match. Retry once with narrower English keywords or an explicit -d DOMAIN."


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--domain", "-d", choices=sorted(DOMAINS))
    ap.add_argument("-n", type=int, default=3)
    ap.add_argument("--plan", action="store_true", help="motion-plan draft across all domains")
    ap.add_argument("-p", "--project")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for d, (f, _, _) in sorted(DOMAINS.items()):
            print(f"{d:11} {f} ({len(load(f))} rows)")
        return
    if not a.query:
        ap.error("query required")
    if a.plan:
        p = plan(a.query, a.project)
        print(json.dumps(p, ensure_ascii=False, indent=2) if a.json else md_plan(p))
        return
    d = a.domain or detect(a.query)
    res = search(d, a.query, a.n)
    if not a.json:
        print(f"[domain: {d}]")
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else fmt(res))


if __name__ == "__main__":
    main()
