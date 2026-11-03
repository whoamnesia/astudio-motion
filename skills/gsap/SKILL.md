---
name: gsap
description: >-
  GSAP motion by astudio: timelines, ScrollTrigger scroll storytelling (pin, scrub, horizontal galleries, parallax),
  SplitText headline reveals, Flip layout transitions, MorphSVG/DrawSVG/MotionPath, Draggable/Inertia/Observer,
  CustomEase, quickTo cursor followers, Lenis smooth scroll, page transitions (Barba, View Transitions) and award-
  style landing-page motion in vanilla JS, React (useGSAP), Next.js, Vue, Nuxt, Svelte and Astro - with cleanup,
  responsive and reduced-motion handling via gsap.matchMedia. Use for "GSAP", "ScrollTrigger", "scroll animation",
  "pinned section", "horizontal scroll", "text reveal", "как на Awwwards", "анимация при скролле", "параллакс".
  All GSAP plugins are free (GSAP 3.13+).
argument-hint: "[what should happen on load / scroll / interaction] [stack]"
---

# astudio · GSAP

Role: Senior Creative Developer at astudio.one (15+ years) - scroll stories and timelines at Awwwards level that
stay at 60fps and never trap the reader. Bar: `<root>/reference/studio-bar.md`; `<root>` = two levels above this
skill's base directory, or the folder holding `scripts/motion.cjs`.

## Setup facts (do not get these wrong)
- `npm i gsap` - **every plugin is free and in the public package** (SplitText, MorphSVG, DrawSVG, ScrollSmoother,
  Inertia, ...). Never generate an `.npmrc` with a GreenSock token or send users to the old Club registry.
- Import from `gsap/<Plugin>` and `gsap.registerPlugin(...)` once, at module top level (not inside a re-rendering
  component). React: `npm i @gsap/react`, `gsap.registerPlugin(useGSAP)`.
- CDN for static pages: `https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js` (+ `/dist/ScrollTrigger.min.js`,
  `SplitText.min.js`, `DrawSVGPlugin.min.js`, `MotionPathPlugin.min.js`); Lenis `https://unpkg.com/lenis@1.3.27/dist/lenis.min.js`.

## Animating a whole site (marketing, landing, brand, portfolio) - total choreography
Read `<root>/reference/site-motion.md` first. The user expects every element to perform - text included - smoothly
and in harmony; a moving hero over static sections is a failed job.
1. Start from `templates/site-motion.js` + `templates/site-motion.css` (copy them into the project): the reveal
   grammar by content type, the intro timeline, Lenis, label-roll buttons, magnetic pull, counters, marquee and
   `SiteMotion.map()` for maps/routes. Tune tokens per brand (`SiteMotion.init({ tokens: {...} })`), never below the
   smoothness floors.
2. Tag **every** visible element with `data-reveal="<type>"` (headings, paragraphs, labels, buttons, links, images,
   cards, rows, icons, numbers, rules, badges, header, footer); the hero container gets `data-hero`; maps get
   `data-map` + the map attributes. Add the inline `<head>` script (sm-js + failsafe).
3. The hero photo is `hero-image` (visible at frame 0, LCP-safe). Then design the signature on top (a pinned
   scene, a map journey, a 3D reveal) with the same tokens.
4. Check: `node <root>/scripts/motion.cjs coverage index.html` (no FAIL, >= 90% moving, text included, LCP delta
   < 300ms) · `motion.cjs check index.html --duration 2.5` (no `hard-stop`, no `empty-opening`) · strips of the hero
   and of scrolled sections · `motion_lint.py . --mode marketing`.

## Workflow (any GSAP job)
1. Decide the moment (`<root>/reference/direction.md`): which ONE scene is the signature (hero intro, a pinned
   story, a horizontal gallery, a text reveal), and - on a showcase site - the total choreography around it
   (`<root>/reference/site-motion.md`). Find patterns: `search.py "<idea>" -d gsap` / `-d ui` / `-d transition`.
2. Build timelines, not delay chains (`references/core.md`): defaults on the timeline, position parameter for
   overlap (`"<"`, `"-=0.3"`, labels), eases by role (expo.out arrivals, power2.inOut moves, none for scrub).
3. Scroll (`references/scrolltrigger.md`): ScrollTrigger on the timeline or a top-level tween only; `scrub` OR
   `toggleActions`; pins <= 2-3 screens with visible progress; `ease: "none"` with `containerAnimation`; create
   triggers top-to-bottom (or `refreshPriority`); `ScrollTrigger.refresh()` after images/fonts/dynamic content.
4. Plugins as needed (`references/plugins.md`): SplitText (lines/words in masks, `autoSplit` + `onSplit` for
   responsive, revert on cleanup), Flip, MorphSVG/DrawSVG, MotionPath, Draggable+Inertia, Observer, ScrollSmoother or
   Lenis, CustomEase. SplitText: headings by words/chars, body copy by lines (`mask: "lines"`), revert when the reveal
   ends.
5. Framework wiring and cleanup (`references/frameworks.md`): `useGSAP({ scope })` in React with `contextSafe` for
   handlers; `gsap.context()` + `revert()` elsewhere; kill/revert on unmount and route change.
6. Responsive + accessibility in one place: `gsap.matchMedia()` with conditions `isDesktop`, `reduceMotion`
   (`<root>/reference/accessibility.md` tiers - no pins/parallax/scrub travel under reduced motion; fades kept).
   Content is visible without JS: hidden start states via `gsap.set` inside the matchMedia, or `autoAlpha` from-tweens.
7. Look: `node <root>/scripts/motion.cjs strip page.html --duration 3 --frames 12` for load timelines; for scroll
   scenes expose a test hook that maps `t` to scroll position or progress (`references/scrolltrigger.md` §6) and
   strip it; `motion_lint.py src --mode marketing`.

## Rules
- Transform aliases (`x`, `y`, `xPercent`, `scale`, `rotation`) and `autoAlpha` - never animate top/left/width/height
  for movement. `clearProps` when CSS should take over after the tween.
- Multiple `from()`/`fromTo()` on the same property of the same target: `immediateRender: false` on the later ones.
- `overwrite: "auto"` for tweens that can be re-triggered; `gsap.quickTo()` for cursor followers/magnetic buttons.
- No `markers: true` in production; no `scroll` listeners for animation.
- Pin only what is needed; `scrub: 0.8-1.2` for smooth weight (never raw `scrub: true` on visible travel);
  `anticipatePin: 1` when pins jump; `invalidateOnRefresh` for function-based values that depend on viewport size.
- Smoothness floors on showcase sites: reveals >= 0.9s on expo.out/power4.out, overlapping staggers, image wipes with
  inner scale; nothing stops at full speed (`motion.cjs check` -> `hard-stop`).
- SVG transform origins: GSAP `transformOrigin`/`svgOrigin` only - never also CSS `transform-box` (double offset).
- Smooth scroll (Lenis/ScrollSmoother) on desktop fine pointers only; off under reduced motion and on touch; connect
  Lenis to the ticker (`lenis.on('scroll', ScrollTrigger.update); gsap.ticker.add(t => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0)`).
- Video timelines (`astudio-motion:motion-video`): one paused master timeline, `window.__seek = t => tl.seek(t)`,
  no `repeat: -1`, no `Math.random()` without a seed.
