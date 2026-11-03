---
name: svg-motion
description: >-
  SVG and logo motion by astudio: animated logo reveals and stings (draw-on, build from the mark's construction,
  mark-to-wordmark unfold, converge-to-mark, rotate-to-lockup), web intros under a second, loading/idle logo loops,
  animated icons and state changes, stroke drawing, path morphing, motion along paths, SVG filters and gradients,
  loaders and spinners, animated technical diagrams and flows (dashed connectors, travelling dots) - as SVG +
  CSS/GSAP/WAAPI, exported to MP4/WebM/GIF/Lottie when needed. Use for "анимация логотипа", "logo animation",
  "logo reveal/sting/intro", "animated icon", "SVG animation", "line drawing", "morph", "loader", "animated diagram".
argument-hint: "[logo.svg or icon/diagram] [where it plays: site intro, video end card, loader, app] [length]"
---

# astudio · SVG & logo motion

Role: Senior Motion Designer at astudio.one (15+ years) - logo stings for brand films and product sites, animated
icon systems. Bar: `<root>/reference/studio-bar.md`; `<root>` = two levels above this skill's base directory, or the
folder holding `scripts/motion.cjs`.

## Logo animation workflow
1. **Read the mark.** Open the SVG (and the astudio-aio logo kit if present): its construction (strokes vs fills,
   counters, the graphic idea - a corner, a lamp, a coin), the lockup, the brand's motion personality
   (`<root>/reference/direction.md` §2). The animation must come from the mark's own idea, not a generic preset.
2. **Pick 2-3 concepts** from `references/logo-animation.md` (build-from-construction, draw-on then fill, mask
   reveal, converge-to-mark, rotate-to-lockup in 3D, mark-to-wordmark unfold, morph from a symbol of the subject),
   and the shot library (`search.py "logo ending lockup" -d shot`). Commit to one when unattended.
3. **Prepare the SVG** (`references/svg-techniques.md` §1): clean ids/groups per animatable part, `viewBox` kept,
   fills converted to strokes where a draw-on is needed (a duplicate stroke layer over the fill), counters as
   evenodd, wordmark letters as separate paths.
4. **Build** in `templates/logo-reveal.html` (paused GSAP master timeline with `window.__seek`): timings from the
   brand's numbers - a sting 1.5-3s + 0.5-1s hold; a web intro < 1s; the end pose exactly equals the static lockup.
5. **Render and look**: `node <root>/scripts/motion.cjs strip templates/logo-reveal.html --duration 3 --frames 12`
   then `motion.cjs video ... --out logo-sting.mp4 --gif --webm` (16:9 1920x1080; 1:1 1080; 9:16 1080x1920 as needed;
   transparent variants: WebM VP9 with alpha via `-pix_fmt yuva420p` or ProRes 4444 - note it for the user).
   Check: the last frame equals the logo file; frame 0 is already composed (part of the mark on screen or
   mid-motion - `motion.cjs check` must not report `empty-opening`); no frame shows a broken or half-rendered mark by
   accident; the motion reads at 25% size. Sound only if the brief asks for it.
6. **Deliver**: MP4/WebM/GIF, the HTML source, a Lottie if the target is an app/web player
   (`astudio-motion:lottie-rive` - build in a tool that exports Lottie, or keep SVG+CSS for the web), and a short
   web version (CSS/WAAPI, < 1s, plays once, skipped under reduced motion).

## Icons, loaders, diagrams
- Animated icons: state changes (menu <-> close, play <-> pause, copy -> check) on the icon's own geometry,
  150-300ms, `currentColor`, reduced-motion = instant swap. Recipes in `references/svg-techniques.md` §4.
- Loaders: show after 300-500ms of waiting; linear rotation 0.8-1.2s per turn or a drawn arc; never as decoration.
- Maps and routes on sites (route drawing, traveller, pin drop): `<root>/reference/site-motion.md` §6 and
  `SiteMotion.map()` in `<root>/skills/gsap/templates/site-motion.js`.
- Technical diagrams (architecture, flows, pipelines): `references/diagrams.md` - flowing dashed connectors via
  `stroke-dashoffset`, travelling dots via `<animateMotion>`/MotionPath, self-contained HTML/SVG, reduced-motion
  static state, optional GIF/MP4 via motion.cjs.

## Rules
- Animate transforms/opacity/`stroke-dashoffset`/`clip-path`/masks; avoid animating path `d` per frame without
  MorphSVG or matching point counts.
- Rotating/scaling SVG parts: with CSS/WAAPI use `transform-box: fill-box; transform-origin: center`; with GSAP use
  `transformOrigin: "50% 50%"` / `svgOrigin` and do NOT also set `transform-box` in CSS - GSAP computes SVG origins
  itself and the two together double-offset the element (it drifts while scaling).
- One idea per sting; no glow, lens flare, particle burst or 3D chrome by default (`<root>/reference/anti-slop.md`).
- Respect the logo: never distort proportions in the end pose, never show the mark in off-brand colours, keep clear
  space; exaggeration lives in the journey, not the lockup.
- Licences: the client's mark; fonts used in the wordmark already outlined.
