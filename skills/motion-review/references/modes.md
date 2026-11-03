# Review modes in detail

## Audit (whole codebase)
1. **Recon** - stack and motion libraries (package.json: motion, gsap, lottie, rive, three, react-spring, aos,
   animate.css, tailwind animate), where tokens live, global CSS transitions, layout/route transition setup,
   `prefers-reduced-motion` handling, components with motion (grep: `transition`, `@keyframes`, `animate(`,
   `motion.`, `gsap.`, `useSpring`, `AnimatePresence`, `ScrollTrigger`, `whileInView`, `animate-`).
2. **Inventory** - a table: component · trigger · frequency tier · purpose · properties · duration · curve ·
   reduced motion · file:line. Missing purpose or wrong tier = finding.
3. **Consistency** - count distinct durations and curves; more than ~6 durations or ~5 curves in a product means
   no system. Propose the token set (`easing.py tokens`) and the mapping old -> new.
4. **Render** the key flows (`motion.cjs strip`) and the reduced-motion variants (`--reduced-motion`).
5. **Report** - Part 1 table (top 15-30 findings), Part 2 verdict by tier, Part 3 plan: P0 (feel-breaking,
   accessibility, perf), P1 (consistency, missing feedback), P2 (polish) with effort estimates; optional
   PLAN.md per area.

## Perf (jank)
Symptom -> fix:
| Symptom | Likely cause -> fix |
|---|---|
| stutters | layout properties animated -> transform/opacity |
| choppy shadow | box-shadow animated -> `filter: drop-shadow()` or pseudo-element opacity |
| jank only during navigation/loading | JS/main-thread animation competing -> CSS/WAAPI (off main thread) |
| Motion x/y drops frames | motion < 14.2 -> upgrade or full transform string |
| hand-rolled animation drops frames in React | setState per frame -> ref.current.style / motion value |
| drag gets laggier as content grows | CSS variable on a parent drives child transform -> set transform directly |
| blur transition lags (Safari) | blur > 12-20px -> 2-8px |
| unexpected properties animate | `transition: all` -> named properties |
| 1px shift at start/end | layer promotion flip -> `will-change: transform` only while animating |
| WebGL scene drops frames | DPR uncapped, draw calls, shadows, uncompressed textures, shader compile stalls -> `<root>/reference/performance.md` §4 |
| scroll feels heavy | scroll listeners / many ScrollTriggers / smooth-scroll on touch -> ScrollTrigger batch, fewer pins, Lenis off on touch |
Report: the symptom, the measured cause (Performance panel, `renderer.info`, `motion.cjs check` sparkline), the fix
with before/after numbers when measurable.

## Opportunities (motion is missing)
Hunt where motion carries information and is currently absent: state changes that teleport (list add/remove,
filters, tab content), overlays without origin, feedback missing on press/submit/copy, loading without progress,
success/error without acknowledgement, navigation without spatial continuity, onboarding/first-run, empty states,
data that updates in place (numbers jumping), the marketing hero (no authored moment), and on showcase sites every
static island: run `motion.cjs coverage` - each static section, static text block and unanimated map layer is an
opportunity (`<root>/reference/site-motion.md` §3, §6).
Gate each candidate (frequency, purpose, speed budget, function). Output Part 1 - opportunities table (where ·
purpose · proposal · tier · effort), Part 2 - **rejected candidates** with the reason (required: it shows the gate
was applied), Part 3 - verdict and the 3 highest-value additions.

## Remove (too much motion)
Delete motion on keyboard/high-frequency actions, decorative loops, entrances on body text in product UI (not on
showcase sites, where text reveals are part of the language), duplicated staggers in app views, hover scales on
grids, scroll-jacking, preloaders; reduce durations over budget and travel distances. Hazards:
removing an exit that a parent waits for (onAnimationComplete), layout that depended on a transform, focus timing.
Output: Part 1 - removed and reduced (file:line, what, why), Part 2 - **kept** (required: what stays and why),
Part 3 - cleanup (dead keyframes, unused libraries) and verdict.

## Film review (rendered video)
See `film-review.md`.
