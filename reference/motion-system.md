# Motion systems and handoff

Good motion is not a collection of one-off animations; it is a set of values defined once and applied everywhere
(the same idea as Figma's motion variables and animated components).

## 1. Tokens
`python3 <root>/scripts/easing.py tokens --out design-tokens` writes:
- `motion.tokens.json` - W3C DTCG 2025.10: `duration` ({value, unit: "ms"}), `cubicBezier` ([x1, y1, x2, y2]) and
  `transition` composites ({duration, delay, timingFunction}) referencing them;
- `motion.css` - custom properties (`--motion-duration-*`, `--motion-ease-*`, `--motion-<role>` shorthands,
  `--motion-stagger-*`, `--motion-travel`) with a reduced-motion override block;
- `motion.tailwind.css` - Tailwind v4 `@theme` (`--ease-*`, `--duration-*` -> `ease-expo-out duration-moderate`).
Merge into the project's existing token pipeline (astudio-aio `design-tokens/`, Style Dictionary, Tailwind theme)
instead of shipping a second system. Components reference roles, never raw numbers:
`transition: transform var(--motion-popover), opacity var(--motion-popover);`

Default role map (adjust to the brand's personality, direction.md §2):
| Role | Duration | Ease |
|---|---|---|
| press | fast 150 | out |
| hover | fast 150 | standard |
| popover / dropdown | base 200 | out |
| modal | moderate 300 | out |
| drawer / sheet | slow 450 | drawer (or spring bounce 0) |
| move / morph | moderate 300 | in-out |
| reveal (showcase site) | 1100-1200 | expo-out (`--ease-reveal`) |
| image wipe (showcase site) | 1400 | `--ease-move` power4.inOut + inner scale 1900 expo-out |
| hover (showcase site) | 550 | `--ease-soft` |
| page | slow 450 | cubic-in-out |
Springs as tokens: store `{dampingRatio, response}` and generate platform values with `easing.py spring`.

## 2. Component motion spec
For every animated component, one row: trigger · purpose · properties (from -> to) · duration token · ease token ·
interruption behaviour · exit · reduced-motion variant · frequency tier. `data/ui-recipes.csv` holds tested
defaults (`search.py -d ui`).

## 3. Motion spec document (MOTION.md)
Write `MOTION.md` beside DESIGN.md when you define motion for a product or brand:
1. Principles (3-5 sentences: what motion is for in this product, the personality in numbers).
2. Tokens table (durations, eases, springs, staggers) with the reduced-motion mapping.
3. Patterns: enter/exit, overlays, navigation/page transitions, lists, feedback, loading, success/error, scroll.
4. Signature moments (with strips/GIFs) and where they are allowed.
5. Never list: what must not animate (keyboard actions, data tables, high-frequency controls).
6. Accessibility rules and the pause controls.
7. Implementation notes per platform (CSS/Motion/GSAP, Reanimated, SwiftUI, Compose).

## 4. Handoff from design tools
- **Figma Motion** (open beta, 2026): motion lives on the canvas timeline; components carry motion; motion variables
  with modes switch easing across a file; Dev Mode's Motion tab exposes CSS, JSON, React/motion.dev code. With the
  Figma MCP server: `get_motion_context(fileKey, nodeId, recursive: true)` is the source of truth for keyframes,
  easing and timing (use its code snippets directly, implement `textAnimations` with their derived stagger timing,
  respect `timelineCohorts`), `get_design_context` gives structure and assets - linked by node id. Prototype Smart
  Animate interactions and animated GIF/SVG export are not available through MCP; say so.
- **After Effects**: read keyframe values from the comp (or ask for a Bodymovin/Lottie export) and convert the
  speed graph to cubic-bezier: AE ease influence 33% ≈ cubic-bezier(0.33, 0, 0.67, 1); 80% out ≈ (0.8, 0, 0.2, 1)-ish
  - measure, don't trust names.
- **Lottie/Rive files**: keep them as runtime assets; never re-implement a designer's Lottie by hand unless asked.
- **Video references**: step frames (`ffmpeg -ss T -i ref.mp4 -frames:v 1 f.png`) and measure positions per frame
  to recover durations and curves before rebuilding a motion.

## 5. Versioning and review
Motion changes get reviewed like visual changes: before/after strips (`motion.cjs strip` on both builds) in the PR,
time-coded comments ("t=0.42s the panel lands before the content").
