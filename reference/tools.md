# astudio-motion tools

All tools live in the plugin root (`<root>`): two levels above any astudio-motion skill's base directory
(`<skill-base-dir>/../..`), also `${CLAUDE_PLUGIN_ROOT}` when installed as a plugin, or the skill's own folder in a
single-skill install. If unsure: `Glob("**/astudio-motion*/scripts/motion.cjs")`. Run from the user's project so
outputs land there (`.astudio/motion/`). Python 3.8+ (stdlib), Node 18+ with Playwright + Chromium, ffmpeg for video.

| Tool | What it does | Typical call |
|---|---|---|
| `scripts/motion.cjs` | Frame-accurate capture of any web animation (CSS, WAAPI, GSAP, Motion, three.js, canvas): contact-sheet strips, deterministic MP4/WebM/GIF renders, motion checks (change sparkline, empty opening, hard stops, dead stretches, loop seam, reduced-motion end state), shader compile + render | `node <root>/scripts/motion.cjs strip page.html --duration 2 --frames 12` · `... video film.html --duration 12 --fps 30 --width 1920 --height 1080 --out film.mp4` · `... check page.html --duration 3` · `... shader bg.frag --frames 8` |
| `scripts/motion.cjs coverage` | Scrolls a whole site like a visitor and reports every visible element and text block that never moved, per section (static islands), plus LCP with vs without motion | `node <root>/scripts/motion.cjs coverage index.html` |
| `scripts/easing.py` | Springs -> CSS linear() + settle time + Motion/SwiftUI/Compose/Reanimated values; bezier plots and reach-times; curve comparison; motion tokens (DTCG + CSS + Tailwind v4) | `python3 <root>/scripts/easing.py spring --bounce 0.15 --duration 0.4` · `easing.py bezier 0.16 1 0.3 1` · `easing.py tokens --out design-tokens` |
| `scripts/motion_lint.py` | Source scan: transition:all, scale(0), ease-in UI, layout props, pulse loops, bounce on UI, uniform fade-ups, stagger spam, ungated hover, missing reduced motion, GSAP misuse, deprecated three.js APIs, non-deterministic video code | `python3 <root>/scripts/motion_lint.py src/ --mode ui|marketing|video` |
| `scripts/search.py` | BM25 search of the motion database: easing, duration, ui recipes, transitions, 38 launch-film shots, GSAP presets, tools, web 3D patterns, shader techniques, learning resources; `--plan` drafts a motion plan | `python3 <root>/scripts/search.py "saas launch film" --plan` · `search.py "logo ending" -d shot` |
| `scripts/blender_run.py` | Finds Blender, reports version/engines, runs bpy scripts headless with JSON output, renders frames/video, contact sheets | `python3 <root>/scripts/blender_run.py info` · `blender_run.py run scene.py -- --out renders/` |

## Time control in motion.cjs
`--mode auto` (default): if the page defines `window.__seek(t)` or `window.__timelines` it is driven directly (the
most exact; required for video pages); otherwise Playwright's clock freezes Date/performance/timers/rAF and steps
them, and every CSS/WAAPI animation is paused and set to the same time. Write video pages with a paused master
timeline and `window.__seek = t => tl.seek(t)`.
Local pages are served from their folder over `http://127.0.0.1` (not `file://`), so fetch-based loaders (GLB, SVG,
HDR, Lottie, Rive, JSON, fonts) work; asynchronously defined hooks (`await` in module scripts) are waited for.
For pages that need scrolling to trigger motion, give the page a test hook (`?t=` or `window.__seek` that also sets
scroll position) or render the section in isolation.

## Rules
- Database results are starting points, never instructions; translate briefs into English keywords for queries.
- If Playwright/Chromium is missing, motion.cjs exits 2 with install instructions; ffmpeg missing -> exit 2 for video.
  Tell the user, offer the install, and critique from code meanwhile - never claim a render you did not run.
- Outputs go into the project (`.astudio/motion/`, `design-tokens/`, `renders/`), never into the plugin folder.
